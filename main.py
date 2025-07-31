from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.entity.config_entity import DataIngestionConfig
# from networksecurity.entity.artifact_entity import DataIngestionArtifact
from networksecurity.entity.config_entity import TrainingPipelineConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from datetime import datetime
import sys


if __name__ == '__main__':
    try:
        trainingpipelineconfig= TrainingPipelineConfig(timestamp=datetime.now())
        dataingestion= DataIngestionConfig(training_pipeline_config=trainingpipelineconfig)
        data_ingestion_config = DataIngestion(dataingestion)
        logging.info("Data ingestion started")
        dataingestionartifact=data_ingestion_config.initiate_data_ingestion()
        print(dataingestionartifact)

    except Exception as e:
        raise NetworkSecurityException(e, sys)