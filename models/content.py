class Content:
    def __init__(self, username):
        self.username = username
        self.avatar = None
        self.avatar_url = ""
        self.content = ""
        self.embeds = []
        self.current_embed = None

    def set_content(self, content):
        self.content = content

    def set_avatar(self, avatar_base64):
        self.avatar = avatar_base64

    def set_avatar_url(self, avatar_url):
        self.avatar_url = avatar_url

    def add_embed(self, description, title=None):
        embed = {
            "title": title,
            "description": description,
            "author": None,
            "fields": [],
            "thumbnail": None,
            "image": None,
            "footer": None,
            "color": None
        }
        self.embeds.append(embed)
        self.current_embed = embed
        return embed

    def set_author(self, name, url=None, icon_url=None):
        if self.current_embed is not None:
            self.current_embed["author"] = {"name": name, "url": url, "icon_url": icon_url}

    def add_field(self, name, value, inline=False):
        if self.current_embed is not None:
            self.current_embed["fields"].append({"name": name, "value": value, "inline": inline})

    def set_thumbnail(self, url):
        if self.current_embed is not None:
            self.current_embed["thumbnail"] = {"url": url}

    def set_image(self, url):
        if self.current_embed is not None:
            self.current_embed["image"] = {"url": url}

    def set_footer(self, text, icon_url=None):
        if self.current_embed is not None:
            self.current_embed["footer"] = {"text": text, "icon_url": icon_url}

    def set_color(self, color):
        if self.current_embed is not None:
            self.current_embed["color"] = color

    def to_dict(self) -> dict:
        data = {
            "username": self.username,
            "content": self.content,
            "embeds": self.embeds
        }

        if self.avatar_url:
            data["avatar_url"] = self.avatar_url

        return data

    def avatar_to_dict(self):
        return {
            "avatar": self.avatar
        }
