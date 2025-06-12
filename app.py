import ngrok
import pyperclip as pc
import os
from main.pedraobot.product_advertising import Product
from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv


app = Flask(__name__)
api = Api(app)

api.add_resource(Product, '/pedraobot/products')

def start(app):
    port = 5000
    load_dotenv(override=True)  # Carrega as variáveis de ambiente do arquivo .env
    ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
    listener = None
    
    try:
        ngrok.set_auth_token(ngrok_token)
        listener = ngrok.connect(port)
        url = listener.url()
        tested_endpoint = '/pedraobot/products'
        print(f"Ngrok tunnel established at: {url}{tested_endpoint}")
        pc.copy(f"{url}{tested_endpoint}")  # Copia a URL do ngrok para a área de transferência
        print("URL copiada para a área de transferência.")
        
        app.run(port=port) #Aqui é a lógica do servidor, que deve ser executada em produção
    except KeyboardInterrupt:
        print("Terminando a execução...")
        ngrok.disconnect(url)
        ngrok.kill()
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")
        ngrok.disconnect(url)
        ngrok.kill()
            
if __name__ == '__main__':
    start(app)