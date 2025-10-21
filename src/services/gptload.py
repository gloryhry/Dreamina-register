import requests
from typing import Optional, List, Dict

class GptloadService:
    def __init__(self, api_url: str, auth_key: str):
        self.api_url = api_url.rstrip('/')
        self.auth_key = auth_key
        self.headers = {
            "Authorization": f"Bearer {auth_key}",
            "Content-Type": "application/json"
        }
    
    def get_groups(self) -> List[Dict]:
        url = f"{self.api_url}/api/groups"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") == 0:
            return result.get("data", [])
        else:
            raise Exception(f"获取groups失败: {result.get('message')}")
    
    def find_group_by_name(self, channel_name: str) -> Optional[int]:
        groups = self.get_groups()
        for group in groups:
            if group.get("name") == channel_name:
                return group.get("id")
        return None
    
    def push_keys(self, group_id: int, keys_list: List[str]) -> Dict:
        url = f"{self.api_url}/api/keys/add-async"
        keys_text = "\n".join(keys_list)
        
        payload = {
            "group_id": group_id,
            "keys_text": keys_text
        }
        
        response = requests.post(url, json=payload, headers=self.headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") == 0:
            return result.get("data", {})
        else:
            raise Exception(f"推送keys失败: {result.get('message')}")
