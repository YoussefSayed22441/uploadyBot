import schedule
import time
import threading
from datetime import datetime
from app.facebook.facebook_client import FacebookClient

class PostScheduler:
    def __init__(self):
        self.facebook_client = FacebookClient()
        self.scheduled_posts = {}
        self.scheduler_thread = None

    def schedule_post(self, post_time, groups, content, image_url=None):
        post_id = f"post_{len(self.scheduled_posts)}"
        self.scheduled_posts[post_id] = {
            "time": post_time,
            "groups": groups,
            "content": content,
            "image_url": image_url,
            "status": "scheduled"
        }
        
        # Schedule the post
        schedule.every().day.at(post_time).do(
            self.execute_post,
            post_id=post_id
        )
        
        return post_id

    def execute_post(self, post_id):
        if post_id in self.scheduled_posts:
            post = self.scheduled_posts[post_id]
            success = True
            
            for group_id in post["groups"]:
                result = self.facebook_client.post_to_group(
                    group_id,
                    post["content"],
                    post["image_url"]
                )
                if not result:
                    success = False
            
            post["status"] = "completed" if success else "failed"
            post["executed_at"] = datetime.now().isoformat()

    def get_scheduled_posts(self):
        return self.scheduled_posts

    def cancel_post(self, post_id):
        if post_id in self.scheduled_posts:
            schedule.clear(post_id)
            del self.scheduled_posts[post_id]
            return True
        return False

    def start_scheduler(self):
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)

        if not self.scheduler_thread:
            self.scheduler_thread = threading.Thread(target=run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start() 