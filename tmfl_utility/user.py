from requests import get

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self._base_url = "https://api.sleeper.app/v1/user/{}".format(user_id)
        self.display_name = get(self._base_url).json().get("display_name")

    def update_display_name(self):
        self.display_name = get(self._base_url).json().get("display_name")