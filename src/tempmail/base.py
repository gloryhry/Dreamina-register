from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class TempMailBase(ABC):
    @abstractmethod
    def create_email(self, prefix: Optional[str] = None, domain: Optional[str] = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_domains(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_messages(self, email_address: str, email_id: Optional[str] = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_message_content(self, email_address: str, message_id: str, email_id: Optional[str] = None) -> Dict[str, Any]:
        pass
    
    def extract_verification_code(self, content: str) -> Optional[str]:
        import re
        match = re.search(r'verification code is ([A-Z0-9]{6})', content, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
