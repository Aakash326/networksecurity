from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import os
import sys
import pandas as pd
import numpy as np
import pymongo
from pymongo import MongoClient
from typing import List
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv
load_dotenv()


MONGO_DB_URL = os.getenv("MONGO_DB_URL")


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig): ##read data from mongo db and save it to csv
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_collection_as_dataframe(self): # This function exports a MongoDB collection to a pandas DataFrame
        try:
            database_name=self.data_ingestion_config.database_name
            collection_name=self.data_ingestion_config.collection_name
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection=self.mongo_client[database_name][collection_name]

            df=pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list():
                df.drop(columns=["_id"], inplace=True)
            
            df.replace({"na":np.nan}, inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_data_into_feature_store(self,dataframe: pd.DataFrame) -> str: # This function saves the DataFrame to a CSV file in the feature store directory
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_dir
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return feature_store_file_path
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def split_data_as_train_test(self, dataframe: pd.DataFrame) : # This function splits the DataFrame into training and testing sets and saves them to CSV files
        try:
            train_set, test_set = train_test_split(dataframe, test_size=self.data_ingestion_config.train_test_split_ratio)
            logging.info(f"Train set shape: {train_set.shape}, Test set shape: {test_set.shape}")
            dir_path = os.path.dirname(self.data_ingestion_config.train_file_path)
            os.makedirs(dir_path, exist_ok=True)
            train_set.to_csv(self.data_ingestion_config.train_file_path, index=False, header=True)
            test_set.to_csv(self.data_ingestion_config.test_file_path, index=False, header=True)
            logging.info("exported train and test data successfully")
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    
    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe()
            self.export_data_into_feature_store(dataframe)  # don't overwrite dataframe
            self.split_data_as_train_test(dataframe)

            data_ingestion_artifact = DataIngestionArtifact(
                valid_train_file_path=self.data_ingestion_config.train_file_path,
                valid_test_file_path=self.data_ingestion_config.test_file_path,
                invalid_train_file_path="",  # Add empty string for now since this seems to be for data validation
                invalid_test_file_path="",   # Add empty string for now since this seems to be for data validation
                ingested_train_file_path=self.data_ingestion_config.train_file_path,
                ingested_test_file_path=self.data_ingestion_config.test_file_path
            )
            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


