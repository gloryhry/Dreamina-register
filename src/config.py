import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TEMPMAIL_TYPE = os.getenv("TEMPMAIL_TYPE", "moemail")
    
    MOEMAIL_API_KEY = os.getenv("MOEMAIL_API_KEY", "")
    MOEMAIL_BASE_URL = os.getenv("MOEMAIL_BASE_URL", "https://moemail.985100.xyz")
    
    TEMPMAILHUB_API_KEY = os.getenv("TEMPMAILHUB_API_KEY", "")
    TEMPMAILHUB_BASE_URL = os.getenv("TEMPMAILHUB_BASE_URL", "https://tempmailhub.985100.xyz")
    TEMPMAILHUB_CHANNEL = os.getenv("TEMPMAILHUB_CHANNEL", "minmail")
    
    PROXY_URL = os.getenv("PROXY_URL", "")
    
    REGISTER_COUNT = int(os.getenv("REGISTER_COUNT", "1"))
    
    HEADLESS = os.getenv("HEADLESS", "false").lower() in ("true", "1", "yes")
    
    GPTLOAD_API_URL = os.getenv("GPTLOAD_API_URL", "https://gptload.985100.xyz")
    GPTLOAD_AUTH_KEY = os.getenv("GPTLOAD_AUTH_KEY", "")
    GPTLOAD_CHANNEL_NAME = os.getenv("GPTLOAD_CHANNEL_NAME", "jimeng")
    
    @classmethod
    def validate(cls):
        if cls.TEMPMAIL_TYPE == "moemail" and not cls.MOEMAIL_API_KEY:
            raise ValueError("MOEMAIL_API_KEY is required when TEMPMAIL_TYPE is moemail")
        if cls.TEMPMAIL_TYPE == "tempmailhub" and not cls.TEMPMAILHUB_API_KEY:
            raise ValueError("TEMPMAILHUB_API_KEY is required when TEMPMAIL_TYPE is tempmailhub")
