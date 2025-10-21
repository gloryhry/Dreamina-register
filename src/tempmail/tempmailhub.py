import requests
import time
from typing import Optional, List, Dict, Any
from .base import TempMailBase
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class TempMailHub(TempMailBase):
    def __init__(self, api_key: str, channel: str = "minmail", base_url: str = "https://tempmailhub.985100.xyz"):
        self.api_key = api_key
        self.channel = channel
        self.base_url = f"{base_url}/api/mail"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.access_token = None
        
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get_domains(self) -> List[str]:
        return []
    
    def create_email(self, prefix: Optional[str] = None, domain: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "provider": self.channel
        }
        
        if prefix:
            payload["prefix"] = prefix
        
        if domain:
            payload["domain"] = domain
        
        response = requests.post(f"{self.base_url}/create", headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            raise ValueError(f"Failed to create email: {data.get('error')}")
        
        email_data = data.get("data", {})
        self.access_token = email_data.get("accessToken")
        
        return {
            "address": email_data.get("address"),
            "domain": email_data.get("domain"),
            "username": email_data.get("username"),
            "access_token": self.access_token
        }
    
    def get_messages(self, email_address: str, email_id: Optional[str] = None) -> List[Dict[str, Any]]:
        payload = {
            "address": email_address,
            "provider": self.channel
        }
        
        if self.access_token:
            payload["accessToken"] = self.access_token
        
        response = requests.post(f"{self.base_url}/list", headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            raise ValueError(f"Failed to get messages: {data.get('error')}")
        
        return data.get("data", [])
    
    def get_message_content(self, email_address: str, message_id: str, email_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "address": email_address,
            "id": message_id,
            "provider": self.channel
        }
        
        if self.access_token:
            payload["accessToken"] = self.access_token
        
        response = requests.post(f"{self.base_url}/content", headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            raise ValueError(f"Failed to get message content: {data.get('error')}")
        
        return data.get("data", {})
    
    def wait_for_verification_code(self, email_address: str, timeout: int = 60) -> Optional[str]:
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.get_messages(email_address)
            
            for message in messages:
                subject = message.get("subject", "")
                
                code = self.extract_verification_code(subject)
                if code:
                    return code
            
            time.sleep(5)
        
        return None
