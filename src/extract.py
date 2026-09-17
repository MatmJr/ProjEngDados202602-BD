from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
import requests

load_dotenv()

class Extract():
    def __init__(self):
        pass

    def extract_pnadc(self):
        url = "https://servicodados.ibge.gov.br/api/v3/agregados/4093/periodos/201201%7C201202-202602/variaveis/4099?localidades=N3[26]&classificacao=2[all]"

        resp = requests.get(url)
        data = resp.json()

        return data

    
    def extract_collection_from_mongo(self, db_name, collection_name):
            mongo_uri = os.getenv("MONGO_URI")
            client = MongoClient(mongo_uri, server_api=ServerApi('1'))

            db = client[db_name]
            data = db[collection_name]

            data = list(data.find())
            return data


