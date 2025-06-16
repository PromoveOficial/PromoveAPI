"""
    This class exists for keep the pictures even if the docker container 
    stop.
    Plus its easier for manage external requests, like meta api for example
"""

import requests
import re
import logging
import io
from flask_restful import Resource
from flask import request, send_file
from PIL import Image
from .responses import *

class DownloadPicturesPedraobot(Resource):
    def __init__(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        self.logger = logger
    
    def post(self):
        try:
            RULE_URL = r'^https?:\/\/[A-Za-z\$\-=&\.\/?_0-9:]+$' # http or http (Caracters without accent) Numbers $ - = / ? _ :
            
            url = request.args.get('picture-url')
            name = request.args.get('picture-name')
            
            if url is None:
                raise NoParameter('url')
            if name is None:
                raise NoParameter('name')
            
            if not re.match(RULE_URL, url):
                raise WrongUrlFormat()
            
            self.__download_picture(picture_name=name, picture_url=url)
            
            response = RequestComplete('Picture save success')
        except RequestError as e:
            response = e
        except Exception as e:
            self.logger.critical(f"[EXCEPTIONAL ERROR] {e}")
            response = ExceptionalError()
        finally:
            self.logger.info(f"{response.__str__()}")
            return response.content
         
    def __download_picture(self, picture_url=None, picture_name=None):
        self.logger.info(f"[TRY: DOWNLOAD PICTURE] {picture_url}")
        response = requests.get(picture_url)
        if response.status_code != 200:
            raise ImageNotFoud()
        
        picture_path = f"main/pictures/pedraobot/products/{picture_name}.png"
        image = Image.open(io.BytesIO(response.content))
        if image.mode in ('RGBA', 'P'): 
            image = image.convert('RGB')

        image.save(picture_path, "PNG")        
        
        self.logger.info(f"[SUCCESS: DOWNLOAD PICTURE] {picture_url} - Saved as {picture_name}")

class GetPicturesPedrabot(Resource):
    def __init__(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        self.logger = logger
    
    def get(self, identifier):
        try:
            
            response = send_file(f"main/pictures/pedraobot/products/{identifier}.png", mimetype='image/png')
       
        except RequestError as e:
            response = e.content
        except Exception as e:
            self.logger.critical(f"[EXCEPTIONAL ERROR] {e}")
            response = ExceptionalError().content
        finally:
            self.logger.info(f"{response.__str__()}")
            return response
    