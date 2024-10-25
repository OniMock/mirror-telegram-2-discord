class UserInterface:
    @staticmethod
    def display_menu():
        print("\nChoose an option:")
        print("1. List all groups and choose one to mirror")
        print("2. Enter the username at(@) or ID of the group to mirror")
        print("0. Exit")

    @staticmethod
    def get_user_choice():
        return input("Enter your choice: ")

    @staticmethod
    def display_groups(groups):
        for index, group in enumerate(groups):
            print(f"{index + 1}: {group.name} (ID: {group.id})")

    @staticmethod
    def display_subgroups(subgroups):
        print(f"0: Mirror all SubGroups")
        for index, topic in enumerate(subgroups):
            print(f"{index + 1}: {topic.title} (ID: {topic.id})")

    @staticmethod
    def get_group_selection():
        return int(input("Select a group to mirror (by number): ")) - 1

    @staticmethod
    def get_subgroup_selection():
        return int(input("Select a SubGroup to mirror (by number): "))

    @staticmethod
    def get_group():
        return input("Enter the username at(@) or ID or link of the group you want to mirror: ")

    @staticmethod
    def exit():
        print("Exiting...")
