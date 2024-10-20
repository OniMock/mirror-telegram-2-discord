from dataclasses import field


class Content:
    def __init__(self, message, user_name=None):
        self.user_name = user_name
        self.message = message

    def format_payload(self, original_user=None, original_message=None):
        payload = {
            "content": self.message,
            "username": self.user_name,
        }
        if original_user:
            payload["embeds"] = [{
                "description": "*repply*:",
                "fields": [
                    {
                        "name": original_user,
                        "value": original_message or "",
                        "inline": False
                    }
                ],
                "footer": {"text": "Powered by Onimock"},
            }]

        return payload