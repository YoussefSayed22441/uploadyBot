import requests
import json

def test_webhook():
    # Your local Flask server URL
    local_url = "http://localhost:5000/webhook"
    
    # Sample WhatsApp webhook payload
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123456789",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "1234567890",
                        "phone_number_id": "1234567890"
                    },
                    "messages": [{
                        "from": "1234567890",
                        "id": "wamid.123",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {
                            "body": "/schedule 15:00 https://facebook.com/groups/123456789 \"Test post\""
                        }
                    }]
                }
            }]
        }]
    }
    
    # Send test request
    response = requests.post(local_url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_webhook() 