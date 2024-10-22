def get_username(user):
    first_name = getattr(user, 'first_name', None)
    last_name = getattr(user, 'last_name', None)
    title = getattr(user, 'title', None)
    username = getattr(user, 'username', 'Unknown User')
    user_name = f"{first_name or ''} {last_name or ''}".strip()

    if user_name:
        return user_name
    elif title:
        return title
    else:
        return username
