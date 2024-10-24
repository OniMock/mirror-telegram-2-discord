import re

from models.identifier import Identifier


class CheckString:
    @staticmethod
    def check_string_group(group):
        if group.startswith("https://"):
            group = group[8:]
        elif group.startswith("t.me/"):
            group = group[5:]

        parts = group.split('/')

        if len(parts) >= 3:
            username = parts[1]
            try:
                message_id = int(parts[2])
                return Identifier('link_sub_group', username, message_id)
            except ValueError:
                return Identifier('link_group', username, None)

        if len(parts) >= 2 and parts[1].startswith('+'):
            return Identifier('link_invitation', group, None)

        if len(parts) >= 2:
            username = parts[1]
            return Identifier('link_group', username, None)

        if re.match(r"^\d+$", group):
            group_id = int(group)
            return Identifier('id_group',int(f"-100{group_id}") if not str(group_id).startswith('100') else -group_id, None)

        if re.match(r"^-?\d+$", group):
            group_id = int(group)
            return Identifier('id_group', int(f"-100{abs(group_id)}") if not str(abs(group_id)).startswith('100') else group_id,
                              None)

        return Identifier('username_group', group, None)