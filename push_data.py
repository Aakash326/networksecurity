import os
import sys
import json
import certifi
import pandas as pd
import numpy as np
import pymongo
from dotenv import load_dotenv
from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException

# Load .env
load_dotenv(dotenv_path="/Users/saiaakash/Documents/mlops/NetworkSecurity/.env")
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(f"Connecting to MongoDB at {MONGO_DB_URL}")

ca = certifi.where()

class NetworkDataExtract:
    def __init__(self):
        pass
    
    def csv_to_json(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def insert_data(self, records, database, collection):
        try:
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            self.database = self.mongo_client[database]
            self.collection = self.database[collection]
            self.collection.insert_many(records)
            return len(records)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

if __name__ == "__main__":
    FILE_PATH = '/Users/saiaakash/Documents/mlops/NetworkSecurity/Network_data/phisingData.csv'
    DATABASE = 'Aakash'
    COLLECTION = 'NetworkData'
    
    networkobj = NetworkDataExtract()
    records = networkobj.csv_to_json(FILE_PATH)
    print(records)
    no_of_records = networkobj.insert_data(records, DATABASE, COLLECTION)
    print(no_of_records)