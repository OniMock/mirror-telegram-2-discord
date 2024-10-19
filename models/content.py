class Content:
    def __init__(self, message, user_name=None):
        self.user_name = user_name
        self.message = message

    def format_payload(self):
        payload = {
            "content": self.message,
            "username": self.user_name
        }
        return {k: v for k, v in payload.items() if v is not None}
