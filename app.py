from flask import Flask
from flask_restful import Api
from main.pictures.pictures_management import DownloadPicturesPedraobot, GetDeletePicturesPedrabot
from main.pedraobot.product_advertising import Product


app = Flask(__name__)
api = Api(app)

api.add_resource(Product, '/pedraobot/products')
api.add_resource(DownloadPicturesPedraobot, '/pedraobot/pictures')
api.add_resource(GetDeletePicturesPedrabot, '/pedraobot/pictures/<string:identifier>')