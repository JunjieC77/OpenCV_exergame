import json

class ProfileManager:
    def __init__(self, filename="profile.json"):
        self.filename = filename
        self.profiles = self.load_profiles()

    def load_profiles(self):
        try:
            with open(self.filename, "r") as file:
                profiles = json.load(file)
        except FileNotFoundError:
            profiles = {"profiles": {}}
        return profiles

    def save_profiles(self):
        with open(self.filename, "w") as file:
            json.dump(self.profiles, file, indent=4)

    def create_profile(self, player_name):
        if player_name not in self.profiles["profiles"]:
            self.profiles["profiles"][player_name] = {"high_score": 0}
            return True
        return False

    def delete_profile(self, player_name):
        if player_name in self.profiles["profiles"]:
            del self.profiles["profiles"][player_name]
            return True
        return False

    def select_profile(self, player_name):
        return self.profiles["profiles"].get(player_name)