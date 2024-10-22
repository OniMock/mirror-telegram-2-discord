from models.embed import Embed


class Content:
    def __init__(self, username):
        self.username = username
        self.avatar = None
        self.avatar_url = None
        self.content = ""
        self.embeds = []

    def set_content(self, content):
        self.content = content

    def set_avatar(self, avatar_base64):
        self.avatar = avatar_base64

    def set_avatar_url(self, avatar_url):
        self.avatar_url = avatar_url

    def add_embed(self, embed: Embed):
        self.embeds.append(embed)

    def to_dict(self):
        data = {
            "username": self.username,
            "content": self.content,
            "embeds": [embed.to_dict() for embed in self.embeds],
        }

        if self.avatar_url:
            data["avatar_url"] = self.avatar_url

        # Remove None values from the dictionary
        return {k: v for k, v in data.items() if v}

    def avatar_to_dict(self):
        return {"avatar": self.avatar}
