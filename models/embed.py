class Embed:
    def __init__(self, description, title=None):
        self.title = title
        self.description = description
        self.author = None
        self.fields = []
        self.thumbnail = None
        self.image = None
        self.footer = None
        self.color = None

    def set_author(self, name, url=None, icon_url=None):
        self.author = {"name": name, "url": url, "icon_url": icon_url}

    def add_field(self, name, value, inline=False):
        self.fields.append({"name": name, "value": value, "inline": inline})

    def set_thumbnail(self, url):
        self.thumbnail = {"url": url}

    def set_image(self, url):
        self.image = {"url": url}

    def set_footer(self, text, icon_url=None):
        self.footer = {"text": text, "icon_url": icon_url}

    def set_color(self, color):
        self.color = color

    def to_dict(self):
        embed_dict = {
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "fields": self.fields,
            "thumbnail": self.thumbnail,
            "image": self.image,
            "footer": self.footer,
            "color": self.color,
        }
        # Remove keys with value None
        return {k: v for k, v in embed_dict.items() if v is not None}