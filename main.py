import traceback

class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_detail):
        super().__init__(error_message)
        self.error_message = f"{error_message} | Traceback: {traceback.format_exc()}"

    def __str__(self):
        return self.error_message


# Main execution block for running the data ingestion and validation pipeline
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig, TrainingPipelineConfig
from networksecurity.logging.logger import logging
import sys
from datetime import datetime

if __name__ == "__main__":
    try:
        logging.info("Starting the Network Security pipeline.")
        trainingpipelineconfig = TrainingPipelineConfig(timestamp=datetime.now())
        
        data_ingestion_config = DataIngestionConfig(training_pipeline_config=trainingpipelineconfig)
        data_ingestion = DataIngestion(data_ingestion_config)
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion completed.")

        datavalidation_config = DataValidationConfig(training_pipeline_config=trainingpipelineconfig)
        data_validation = DataValidation(dataingestionartifact, datavalidation_config)
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data validation completed.")

        print("Drift report:")
        print(data_validation_artifact.drift_report_file_path)

    except Exception as e:
        raise NetworkSecurityException(e, sys)