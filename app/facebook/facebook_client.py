import requests
from app import app

class FacebookClient:
    def __init__(self):
        self.access_token = app.config['FACEBOOK_ACCESS_TOKEN']
        self.api_url = "https://graph.facebook.com/v17.0"

    def post_to_group(self, group_id, message, image_url=None):
        endpoint = f"{self.api_url}/{group_id}/photos" if image_url else f"{self.api_url}/{group_id}/feed"
        
        data = {
            "access_token": self.access_token,
            "message": message
        }
        
        if image_url:
            data["url"] = image_url
            
        try:
            response = requests.post(endpoint, data=data)
            return response.json()
        except Exception as e:
            print(f"Error posting to group: {str(e)}")
            return None

    def get_groups(self):
        endpoint = f"{self.api_url}/me/groups"
        try:
            response = requests.get(endpoint, params={"access_token": self.access_token})
            return response.json()
        except Exception as e:
            print(f"Error getting groups: {str(e)}")
            return None

    def verify_token(self):
        endpoint = f"{self.api_url}/debug_token"
        try:
            response = requests.get(
                endpoint,
                params={
                    "input_token": self.access_token,
                    "access_token": self.access_token
                }
            )
            return response.json()
        except Exception as e:
            print(f"Error verifying token: {str(e)}")
            return None 