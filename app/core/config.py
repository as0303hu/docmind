from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",extra="ignore")
    
    #App
    app_env:str ="development"
    log_level:str = "INFO"
    
    #Database
    database_url:str =""
    
    #openAI
    openai_api_key:str=""
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