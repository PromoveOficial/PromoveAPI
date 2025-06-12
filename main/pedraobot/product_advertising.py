from pathlib import Path
from dotenv import load_dotenv
from flask_restful import Resource
from flask import request
from PIL import Image
from ..utils import log
from .responses import *
from spacy.tokens import DocBin
from .language_model import DATA_TRAINING
import psycopg2 as psy
import requests
import spacy
import io
import json
import os
import re

class ProductAdvertisingDatabase():
    connection = None
    database_name = "PRODUCT_ADVERTISING"

    def __init__(self):
        self.get_connection()
    
    @classmethod
    def get_connection(cls):
        load_dotenv()
        cls.connection = json.loads(os.getenv(f"CONNECTION_{cls.database_name}"))

class Product(Resource):
    CONNECTION = ProductAdvertisingDatabase().connection

    def __init__(self, id=None, data=None): #id can be the numerical id or the url
        try:
            if id is None ^ data is None: # xor
                raise ParameterError()
            
            if data is not None:
                self.__add_product_to_database(data)
                product = data
            else: 
                product = self.__get_product_from_database(id)
                
            self.id = product['id']
            self.name = product['name']
            self.url = product['url']
            self.picture_path = product['product_path']
            self.coupon = product['coupon']
            self.phrase = product['phrase']
            self.category = product['category']
            self.price = product['price']
            
            
        except ParameterError as e:
            log(f"[FAIL PRODUCT INIT]: {e}")
            
    """
        Right request example:
        $ curl -X POST https://url/pedraobot/products?tk=verify_token -H 'Content-Type:application/json' -d "data"
        The POST request should contain a JSON object with the following structure:
        data = {
            'name': 'name', // can't be None
            'url': 'content', // can't be None
            'picture_url': None,
            'coupon': None,
            'phrase': None,
            'category': None,
            'price': {
                'actual_price': '123.21', // can't be None
                'last_price': None
            }
        }
    """
    def post(self):
        try: 
            RULE_URL = r'^https:\/\/[A-Za-z\$\-=&\.\/?_0-9:]+$' # (Caracters without accent) Numbers $ - = / ? _ :
            RULE_NAME = r'^[A-Za-z0-9:\-\.\/ á-úÁ-Úà-ùÀ-Ùâ-ûÂ-Ûã-ũÃ-Ũ]+$' # (Caracter without accent or with that accents: ^ ~ ´ `) Numbers : - . /
            RULE_PRICE = r'^\d{1,17}[\.,]\d{1,2}$' # from 1 to 17 numbers | 1 . or , | 2 more numbers for decimal
            
            token = request.args.get('tk')
            VERIFY_TOKEN = os.environ.get('API_VERIFY_TOKEN')
            
            if VERIFY_TOKEN != token:
                raise Unauthorized(request.host) # Upgrade this later
            
            if request.headers.get('Content-Type') != 'application/json': # Server just accept json post requests
                raise UnsupportedMediaType()
            
            data = request.get_json()
            name = data['name']
            url = data['url']
            price = data['price']
            
            # Verify if important data matches needed formart
            if not (
                re.match(RULE_NAME, name) and                                               
                re.match(RULE_URL, url) and                                                 
                re.match(RULE_PRICE, price['actual_price']) and                             
                (price['last_price'] is None or re.match(RULE_PRICE, price['last_price']))  
            ): raise UnprocessableEntity()
            
            id_product_added = self.__add_product_to_database(data)
            # Cathces internal logic error
            if id_product_added is None:
                raise InternalError()

            response = RequestComplete({"product_id": id_product_added})
            
        except RequestError as e:
            response = e
        except (KeyError, TypeError):
            response = UnprocessableEntity()
        except psy.Error as e:
            log(f"[DATABASE ERROR] - {e}")
            self.delete_product()
        except Exception as e:
            log(f"[EXCEPTIONAL ERROR] - {e}")   
            response = ExceptionalError()
        finally:
            log(f"[{request.host}]: {response}")
            return response.content
    
    def get(self):
        response = None
        try:    
            token = request.args.get('tk')
            VERIFY_TOKEN = os.environ.get('API_VERIFY_TOKEN')
            
            if token != VERIFY_TOKEN:
                raise Unauthorized(request.host)

            query_type = request.args.get('query-type')
            if query_type not in ['exact', 'like']:
                raise QueryNotSupported()
            
            if query_type == 'exact':
                identifier = request.args.get('identifier')
                if identifier is None: 
                    raise NoParameter('identifier')
                if re.match(r"^\d+$", identifier):
                    identifier = int(identifier)    
                product = self.__get_product_from_database(identifier)
                
            elif query_type == 'like':
                query = request.args.get('query')
                if identifier is None: 
                    raise NoParameter('query')
                product = self.__get_products_match(query)
                
            if product is None:
                raise ProductNotFound()
                        
            response = RequestComplete(product)
            
        except RequestError as e:
            response = e
        except psy.Error as e:
            log(f"[DATABASE ERROR] - {e}")
            response = InternalError()
        except Exception as e:
            log(f"[EXCEPTIONAL ERROR] - {e}")   
            response = ExceptionalError()
        finally: 
            return response.content

    def __get_products_match(query):
        raise NotImplementedYet()
        
    def __delete_product(self, product_id: int | str):
        with psy.connect(**self.CONNECTION) as conn:
            with conn.cursor() as cur:
                #Apaga os preços associados a esse produto
                query = "DELETE FROM product_price WHERE product_id = %s"
                cur.execute(query, (product_id,))
                conn.commit()
                
                #Apaga a imagem associada ao produto
                imagem = Path(self.picture_path)
                imagem.unlink(missing_ok=True)
                
                #Apaga o produto em si
                query = "DELETE FROM product WHERE id = %s;"
                cur.execute(query, (product_id,))
                conn.commit()
                log(f"[SUCCESS: DELETE PRODUCT] product/{product_id}")
                return True

    def __add_product_to_database(self, data: object):
        log(f"[TRY: ADD PRODUCT] product/{data['url']}")
        with psy.connect(**self.CONNECTION) as conn:
            with conn.cursor() as cur:
                if self.__get_product_from_database(data['url'], check=True):
                    raise ProductAlredyExists()
                
                query = """
                    INSERT INTO product (name, url, coupon, phrase, category)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                """
                
                cur.execute(query, (
                    data['name'],
                    data['url'],
                    data['coupon'],
                    data['phrase'],
                    data['category']
                ))
                product_id = cur.fetchone()[0]
                conn.commit()
                
                if (self.__add_price_to_database(self.product_id, data['price']) 
                    and self.__download_picture(picture_url=data['picture_url'])):
                    self.__delete_product(product_id)
                
                log(f"[SUCCESS: ADD PRODUCT] product/{data['url']} - ID: {self.product_id}")
                
                formatted_product = {
                    'id': product_id,
                    'name': data[2], 
                    'url': data[3], 
                    'picture_path': data[4],
                    'coupon': data[5],
                    'phrase': data[6],
                    'category': data[7],
                    'price': {
                        'actual_price': data[8],
                        'last_price': data[9]
                    }
                }
                
                return formatted_product

    def __add_price_to_database(self, product_id, price):
        log(f"[TRY: ADD PRICE] product/{product_id} - price/{price}")
        with psy.connect(**self.CONNECTION) as conn:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO product_price (product_id, actual_price, last_price)
                    VALUES (%s, %s, %s);
                """
                cur.execute(query, (product_id, price['actual_price'], price['last_price']))
                log(f"[SUCCESS: ADD PRICE] product/{product_id} - price/{price}")
                return True
    
    def __download_picture(self, picture_url=None):
        log(f"[TRY: DOWNLOAD PICTURE] {picture_url}")
        response = requests.get(picture_url)
        if response.status_code != 200:
            raise ImageNotFoud()
        
        image = Image.open(io.BytesIO(response.content))
        if image.mode in ('RGBA', 'P'): 
            image = image.convert('RGB')
    
        original_format = image.format.lower() if image.format else 'unknown'
        
        if original_format not in ['png', 'jpeg', 'jpg']:
            image.save(self.picture_path, 'PNG')
        else:
            image.save(self.picture_path)
        
        # Update picture path in database
        with psy.connect(**self.CONNECTION) as conn:
            with conn.cursor() as cur:
                query = """
                    UPDATE product 
                    SET picture_path = %s
                    WHERE id = %s;
                """
                cur.execute(query, (self.picture_path, self.product_id))
                conn.commit()
        
        log(f"[SUCCESS: DOWNLOAD PICTURE] {picture_url} - Saved as {self.picture_path}")
        return True
    
    def __get_product_from_database(self, id: int | str, check=False):
        log(f"[TRY: GET PRODUCT] product/{id}")
        with psy.connect(**self.CONNECTION) as conn:
            with conn.cursor() as cur:
                WHERE = {
                    str: 'WHERE url = %s',
                    int: 'WHERE id = %s'
                }
                query = f"""
                    SELECT is_active, product_id, name, url, picture_path, coupon, phrase, category, actual_price, last_price 
                        FROM product_price
	                        INNER JOIN product
		                    ON product_price.product_id = product.id
                        {WHERE[type(id)]}
                """
                                                    
                cur.execute(query, (id,))
                product = cur.fetchone()
                
                # Check just if the prouct alredy exists in the database
                if check:
                    return True
                    
                if product is None:
                    raise ProductNotFound()
                if not product[0]: #check is product is active
                    raise ProductInactive()
                    
                formatted_product = {
                    'id': product[1],
                    'name': product[2], 
                    'url': product[3], 
                    'picture_path': product[4],
                    'coupon': product[5],
                    'phrase': product[6],
                    'category': product[7],
                    'price': {
                        'actual_price': product[8],
                        'last_price': product[9]
                    }
                }
                
                return formatted_product