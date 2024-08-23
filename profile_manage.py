import json

def load_profiles(filename="profile.json"):
    try:
        with open(filename, "r") as file:
            profiles = json.load(file)
    except FileNotFoundError:
        profiles = {"profiles": {}}
    return profiles

def save_profiles(profiles, filename="profile.json"):
    with open(filename, "w") as file:
        json.dump(profiles, file, indent=4)

def create_profile(profiles, player_name):
    if player_name not in profiles["profiles"]:
        profiles["profiles"][player_name] = {"high_score": 0}
        return True
    return False

def delete_profile(profiles, player_name):
    if player_name in profiles["profiles"]:
        del profiles["profiles"][player_name]
        return True
    return False

def select_profile(profiles, player_name):
    return profiles["profiles"].get(player_name)