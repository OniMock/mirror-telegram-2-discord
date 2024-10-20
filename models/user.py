def get_username(user):
    if user.first_name:
        user_name = user.first_name
        if user.last_name:
            user_name += f" {user.last_name}"
    elif user.username:
        user_name = user.username
    else:
        user_name = "Unknown User"
    return user_name