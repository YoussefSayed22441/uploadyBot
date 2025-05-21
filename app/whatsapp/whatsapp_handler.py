import requests
import re
from app import app
from app.scheduler.post_scheduler import PostScheduler

class WhatsAppHandler:
    def __init__(self):
        self.token = app.config['WHATSAPP_TOKEN']
        self.phone_number_id = app.config['WHATSAPP_PHONE_NUMBER_ID']
        self.api_url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
        self.scheduler = PostScheduler()

    def parse_message(self, data):
        try:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            return {
                'from': message['from'],
                'type': message['type'],
                'content': message.get('text', {}).get('body', '')
            }
        except (KeyError, IndexError):
            return None

    def process_command(self, message):
        if not message:
            return None

        content = message['content'].lower().strip()
        
        if content.startswith('/help'):
            return self.send_help_message(message['from'])
        elif content.startswith('/schedule'):
            return self.handle_schedule_command(message)
        elif content.startswith('/list'):
            return self.handle_list_command(message['from'])
        else:
            return self.send_message(message['from'], "Unknown command. Use /help for available commands.")

    def send_help_message(self, to):
        help_text = """Available commands:
/schedule [time] [groups] [post content] - Schedule a new post
/list - List all scheduled posts
/help - Show this help message"""
        return self.send_message(to, help_text)

    def extract_group_id(self, group_link):
        # Handle different Facebook group link formats
        patterns = [
            r'facebook\.com/groups/(\d+)',  # https://facebook.com/groups/123456789
            r'fb\.com/groups/(\d+)',        # https://fb.com/groups/123456789
            r'groups/(\d+)'                 # groups/123456789
        ]
        
        for pattern in patterns:
            match = re.search(pattern, group_link)
            if match:
                return match.group(1)
        return None

    def handle_schedule_command(self, message):
        try:
            # Format: /schedule HH:MM group_link1,group_link2 "post content"
            parts = message['content'].split(' ', 3)
            if len(parts) < 4:
                return self.send_message(message['from'], "Invalid format. Use: /schedule HH:MM group_link1,group_link2 \"post content\"")

            time_str = parts[1]
            group_links = parts[2].split(',')
            content = parts[3].strip('"')

            # Convert group links to IDs
            group_ids = []
            invalid_links = []
            
            for link in group_links:
                group_id = self.extract_group_id(link.strip())
                if group_id:
                    group_ids.append(group_id)
                else:
                    invalid_links.append(link)

            if invalid_links:
                return self.send_message(
                    message['from'],
                    f"Invalid group links: {', '.join(invalid_links)}\nPlease provide valid Facebook group links."
                )

            if not group_ids:
                return self.send_message(message['from'], "No valid group links provided.")

            # Schedule the post
            post_id = self.scheduler.schedule_post(time_str, group_ids, content)
            
            return self.send_message(
                message['from'],
                f"Post scheduled successfully!\nTime: {time_str}\nGroups: {', '.join(group_links)}\nContent: {content}"
            )
        except Exception as e:
            return self.send_message(message['from'], f"Error scheduling post: {str(e)}")

    def handle_list_command(self, to):
        posts = self.scheduler.get_scheduled_posts()
        if not posts:
            return self.send_message(to, "No scheduled posts found.")
        
        response = "Scheduled Posts:\n\n"
        for post_id, post in posts.items():
            response += f"ID: {post_id}\n"
            response += f"Time: {post['time']}\n"
            response += f"Groups: {', '.join(post['groups'])}\n"
            response += f"Content: {post['content']}\n"
            response += f"Status: {post['status']}\n\n"
        
        return self.send_message(to, response)

    def send_message(self, to, message):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            return response.json()
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return None 