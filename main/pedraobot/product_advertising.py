from pathlib import Path
from dotenv import load_dotenv
from flask_restful import Resource
from flask import request
from .responses import *
from spacy.tokens import DocBin
from .language_model import DATA_TRAINING
import logging
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
    def __init__(self):
        self.CONNECTION = ProductAdvertisingDatabase().connection
        
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        self.logger = logger
            
    """
        Right request example:
        $ curl -X POST https://url/pedraobot/products?tk=verify_token -H 'Content-Type:application/json' -d "data"
        The POST request should contain a JSON object with the following structure:
        data = {
            'name': 'name', # can't be None
            'url': 'content', # can't be None
            'picture_url': None,
            'coupon': None,
            'phrase': None,
            'category': None,
            'price': {
                'actual_price': '123.21', # can't be None
                'last_price': None
            }
        }
    """
    def post(self):
        try: 
            RULE_URL = r'^https:\/\/[A-Za-z\$\-=&\.\/?_0-9:\_+]+$' # (Caracters without accent) Numbers $ - = / ? _ :
            RULE_NAME = r'^[A-Za-z0-9:\-\.\/ á-úÁ-Úà-ùÀ-Ùâ-ûÂ-Ûã-ũÃ-Ũ!]+$' # (Caracter without accent or with that accents: ^ ~ ´ `) Numbers : - . /
            RULE_PRICE = r'^\d{1,17}[\.,]\d{1,2}$' # from 1 to 17 numbers | 1 . or , | 2 more numbers for decimal
                        
            token = request.args.get('tk')
            VERIFY_TOKEN = os.environ.get('API_VERIFY_TOKEN')
            
            if VERIFY_TOKEN != token:
                raise Unauthorized() # Upgrade this later
            
            if request.headers.get('Content-Type') != 'application/json': # Server just accept json post requests
                raise UnsupportedMediaType()
            
            data = request.get_json()
            name = data['name']
            url = data['url']
            price = data['price']
            
            self.logger.info(url)
            
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
            self.logger.error(f"[DATABASE ERROR] - {e}")
        except Exception as e:
            self.logger.critical(f"[EXCEPTIONAL ERROR] - {e}")   
            response = ExceptionalError()
        finally:
            self.logger.info(f"{response}")
            return response.content
    
    """ 
        Right Requisition example:
        curl -X GET https://url/pedraobot/products?tk=verify_token&query_type=exact&identifier=30
        query_type can be exact or like for a search precisely for a product or all that matches respectively
        like is in development yet so don't use that 
        
        if you choose query_type=exact, you must pass a identifier= id or url of the product
        if you choose query_type=like just pass the query and we will do the rest bitch
    """
    def get(self):
        self.logger.debug(request.__str__)

        response = None
        try:    
            token = request.args.get('tk')
            VERIFY_TOKEN = os.environ.get('API_VERIFY_TOKEN')
            
            if token != VERIFY_TOKEN:
                raise Unauthorized()
            
            if request.headers.get('Content-Type') == 'application/json':
                response = self.__get_product_data()
                   
            response = RequestComplete(response)
            
        except RequestError as e:
            response = e
        except psy.Error as e:
            self.logger.info(f"[DATABASE ERROR] - {e}")
            response = InternalError()
        except Exception as e:
            self.logger.info(f"[EXCEPTIONAL ERROR] - {e}")   
            response = ExceptionalError()
        finally: 
            return response.content

    def __get_product_data(self):
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
            
        return product
            
    def __get_products_match(query):
        raise NotImplementedYet()
        
    def __delete_product(self, product_id: int, product=True, price=True, picture=True):
        with psy.connect(**self.CONNECTION) as conn:
            with conn.cursor() as cur:
                if price:
                    #Apaga os preços associados a esse produto
                    query = "DELETE FROM product_price WHERE product_id = %s"
                    cur.execute(query, (product_id,))
                    conn.commit()
                
                if picture:
                    #Apaga a imagem associada ao produto
                    imagem = Path(self.picture_path)
                    imagem.unlink(missing_ok=True)
                
                if product:
                    #Apaga o produto em si
                    query = "DELETE FROM product WHERE id = %s;"
                    cur.execute(query, (product_id,))
                    conn.commit()
                    self.logger.info(f"[SUCCESS: DELETE PRODUCT] product/{product_id}")
                return True

    def __add_product_to_database(self, data: object):
        self.logger.info(f"[TRY: ADD PRODUCT] product/{data['url']}")
        
        save_picture_parameters = {'picture_url': data['picture_url'], 'picture_name': product_id}
        url_pictures = os.environ.get('URL_PICTURES_SERVER')
        picture_result = requests.post(url_pictures, params=save_picture_parameters)
        
        if picture_result['Code'] != 200:
            self.__delete_product(product_id=product_id)
            raise PictureMissing()
        
        picture_path = picture_result['Content']['picture_path']
        
        
        with psy.connect(**self.CONNECTION) as conn:
            with conn.cursor() as cur:
                if self.__get_product_from_database(data['url'], check=True):
                    raise ProductAlredyExists()
                
                query = """
                    INSERT INTO product (name, url, coupon, phrase, category, picture_path)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """
                
                cur.execute(query, (
                    data['name'],
                    data['url'],
                    data['coupon'],
                    data['phrase'],
                    data['category'],
                    picture_path
                ))
                product_id = cur.fetchone()[0]
                conn.commit()
                
                if not self.__add_price_to_database(product_id=product_id, price=data['price']):
                    self.__delete_product(product_id=product_id, picture=False, price=False)
                
                self.logger.info(f"[SUCCESS: ADD PRODUCT] product/{data['url']} - ID: {product_id}")
                
                return product_id

    def __add_price_to_database(self, product_id, price):
        self.logger.info(f"[TRY: ADD PRICE] product/{product_id} - price/{price}")
        with psy.connect(**self.CONNECTION) as conn:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO product_price (product_id, actual_price, last_price)
                    VALUES (%s, %s, %s);
                """
                cur.execute(query, (product_id, price['actual_price'], price['last_price']))
                self.logger.info(f"[SUCCESS: ADD PRICE] product/{product_id} - price/{price}")
                return True
    
    def __get_product_from_database(self, id: int | str, check=False):
        self.logger.info(f"[TRY: GET PRODUCT] product/{id}")
        with psy.connect(**self.CONNECTION) as conn:
            with conn.cursor() as cur:
                WHERE = {
                    str: 'WHERE url = %s',
                    int: 'WHERE id = %s'
                }
                query = f"""
                    SELECT is_active, id, name, url, picture_path, coupon, phrase, category, actual_price, last_price 
                        FROM product_price
	                        INNER JOIN product
		                    ON product_price.product_id = product.id
                        {WHERE[type(id)]}
                """
                                                    
                cur.execute(query, (id,))
                product = cur.fetchone()
                
                # Check just if the prouct alredy exists in the database
                if check:
                    return product is not None
                    
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