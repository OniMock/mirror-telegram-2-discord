class Content:
    def __init__(self, username, avatar):
        self.username = username
        self.avatar = avatar
        self.content = ""
        self.embeds = []
        self.current_embed = None

    def set_content(self, content):
        self.content = content

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
        self.current_embed = embed  # Define o embed atual
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

    def to_dict(self):
        return {
            "username": self.username,
            "content": self.content,
            "embeds": self.embeds
        }
    def avatar_to_dict(self):
        return {
            "avatar": self.avatar
        }