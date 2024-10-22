class UserInterface:
    def display_menu(self):
        print("\nChoose an option:")
        print("1. List all groups and choose one to mirror")
        print("2. Enter the username at(@) or ID of the group to mirror")
        print("0. Exit")

    def get_user_choice(self):
        return input("Enter your choice: ")

    def display_groups(self, groups):
        for index, group in enumerate(groups):
            print(f"{index + 1}: {group.name} (ID: {group.id})")

    def get_group_selection(self):
        return int(input("Select a group to mirror (by number): ")) - 1

    def get_group(self):
        return input("Enter the username at(@) or ID of the group you want to mirror: ")

    def exit(self):
        print("Exiting...")
