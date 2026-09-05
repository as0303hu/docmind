from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",extra="ignore")
    
    #App
    app_env:str ="development"
    log_level:str = "INFO"
    
    #Database
    database_url:str =""
    
    #openAI
    llm_provider: Literal["openai", "azure"] = "openai"
    openai_api_key:str=""
    azure_openai_api_key:str = ""
    azure_openapi_endpoint: str =""
    azure_openai_api_version: str = "2024-10-21"
    azure_embedding_deployment:str =""
    azure_llm_deployment:str =""
    embedding_model:str = "text-embedding-3-small"
    embedding_dimension:int = 1536
    llm_model:str = "gpt-4o-mini"
    llm_temprature:float=0.0
    llm_max_tokens:int = 1024
    
    
    # Chunking
    chunk_size:int=1000
    chunk_overlap:int=200
    
    
    # Search
    top_k:int=5
    
settings=Settings()