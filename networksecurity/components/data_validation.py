from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from scipy.stats import ks_2samp
import pandas as pd
import os
import sys
import yaml

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def validate_number_of_columns(self, dataframe:pd.DataFrame)->bool:
        try:
            number_of_columns =len(self._schema_config["columns"])
            logging.info(f"Required number of columns from schema: {number_of_columns}")
            logging.info(f"Actual number of columns in dataframe: {len(dataframe.columns)}")
            logging.info(f"Dataframe columns: {list(dataframe.columns)}")
            # dataframe_columns = dataframe.columns
            if len(dataframe.columns) != number_of_columns:
                return False
            return True
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    # def numerical_columns(self, dataframe:pd.DataFrame)->bool:
    #     try:
    #         numerical_columns = self._schema_config["numerical_columns"]
    #         dataframe_columns = dataframe.columns
    #         for column in numerical_columns:
    #             if column not in dataframe_columns:
    #                 return False
    #         return True
    #     except Exception as e:
    #         raise NetworkSecurityException(e, sys) from e
    def detect_data_drift(self,base_df,current_df,threshold=0.5)->bool:
        try:
            status=True
            report ={}
            for column in base_df.columns:
                d1=base_df[column]
                d2=current_df[column]
                is_sample_dist=ks_2samp(d1,d2)
                if threshold<=is_sample_dist.pvalue:
                    is_found=False
                else:
                    is_found=True
                    status=False
                report.update({
                    column:{
                        "p_value":float(is_sample_dist.pvalue),
                        "drift_status":is_found
                    }   
                })
            drift_report_file_path=self.data_validation_config.drift_report_file_path
            
            dir_path=os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path,content=report)
            return status
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    

    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.valid_train_file_path
            test_file_path = self.data_ingestion_artifact.valid_test_file_path

            train_dataframe = self.read_data(train_file_path)
            test_dataframe = self.read_data(test_file_path)

            status = self.validate_number_of_columns(dataframe=train_dataframe)
            if not status:
                error_message = f"Number of columns in train dataframe is not equal to number of columns in schema."
                raise NetworkSecurityException(error_message, sys)
            status = self.validate_number_of_columns(dataframe=test_dataframe)
            if not status:
                error_message = f"Number of columns in test dataframe is not equal to number of columns in schema."
                raise NetworkSecurityException(error_message, sys)
            
            status=self.detect_data_drift(base_df=train_dataframe,current_df=test_dataframe)
            dir_path=os.path.dirname(self.data_validation_config.drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            
            # Create directories for validated files
            valid_dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(valid_dir_path, exist_ok=True)
            
            train_dataframe.to_csv(self.data_validation_config.valid_train_file_path,index=False,header=True)
            test_dataframe.to_csv(self.data_validation_config.valid_test_file_path,index=False,header=True)

            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
                invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
