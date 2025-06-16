from flask import Flask
from flask_restful import Api
from main.pictures.pictures_management import DownloadPicturesPedraobot, GetPicturesPedrabot
from main.pedraobot.product_advertising import Product


app = Flask(__name__)
api = Api(app)

api.add_resource(Product, '/pedraobot/products')
api.add_resource(DownloadPicturesPedraobot, '/pictures/pedraobot')
api.add_resource(GetPicturesPedrabot, '/pictures/pedraobot/<string:identifier>')