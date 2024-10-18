class Content:
    def __init__(self, message, user_name=None, photo_url=None):
        self.user_name = user_name
        self.message = message
        self.photo_url = photo_url

    def format_payload(self):
        payload = {
            "content": self.message,
            "username": self.user_name,
            "avatar_url": self.photo_url
        }
        return {k: v for k, v in payload.items() if v is not None}
