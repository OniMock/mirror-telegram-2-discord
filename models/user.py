def get_username(user):
    """
    Retrieves a formatted username from a user object.

    Prioritizes first and last names, then falls back to title and username.
    If none are available, returns 'Unknown User'.

    Args:
        user: An object representing a user with attributes like first_name,
              last_name, title, and username.

    Returns:
        A string with the user's name or 'Unknown User'.
    """
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
