import requests
import random
import time
from typing import Optional, List, Dict, Any
from .base import TempMailBase

class MoeMail(TempMailBase):
    def __init__(self, api_key: str, base_url: str = "https://moemail.985100.xyz"):
        self.api_key = api_key
        self.base_url = f"{base_url}/api"
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        self.email_id = None
    
    def get_domains(self) -> List[str]:
        response = requests.get(f"{self.base_url}/config", headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data.get("domains", [])
    
    def create_email(self, prefix: Optional[str] = None, domain: Optional[str] = None) -> Dict[str, Any]:
        domains = self.get_domains()
        if not domains:
            raise ValueError("No available domains")
        
        if domain is None:
            domain = random.choice(domains)
        
        if prefix is None:
            prefix = f"user{random.randint(100000, 999999)}"
        
        payload = {
            "name": prefix,
            "expiryTime": 3600000,
            "domain": domain
        }
        
        response = requests.post(f"{self.base_url}/emails/generate", headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        self.email_id = data.get("id")
        email_address = f"{prefix}@{domain}"
        
        return {
            "address": email_address,
            "email_id": self.email_id,
            "domain": domain,
            "username": prefix
        }
    
    def get_messages(self, email_address: str, email_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if email_id is None:
            email_id = self.email_id
        
        if not email_id:
            raise ValueError("email_id is required")
        
        response = requests.get(f"{self.base_url}/emails/{email_id}", headers=self.headers)
        response.raise_for_status()
        data = response.json()
        
        messages = data.get("messages", [])
        return messages
    
    def get_message_content(self, email_address: str, message_id: str, email_id: Optional[str] = None) -> Dict[str, Any]:
        if email_id is None:
            email_id = self.email_id
        
        if not email_id:
            raise ValueError("email_id is required")
        
        response = requests.get(f"{self.base_url}/emails/{email_id}/{message_id}", headers=self.headers)
        response.raise_for_status()
        data = response.json()
        
        return data
    
    def wait_for_verification_code(self, email_address: str, timeout: int = 60) -> Optional[str]:
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.get_messages(email_address)
            
            for message in messages:
                subject = message.get("subject", "")
                
                code = self.extract_verification_code(subject)
                if code:
                    return code
            
            time.sleep(3)
        
        return None
