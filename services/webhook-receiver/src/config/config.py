from pydantic_settings import BaseSettings
class setting(BaseSettings):
    github_app_id:str
    github_webhook_secret:str
    
    redis_url:str="redis://redis:6379/0"
    
    class Config:
        env_file = ".env"
    
settings = setting()