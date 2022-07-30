from requests import get

class Players:
    def __init__(self):
        self._base_url = "https://api.sleeper.app/v1/players"

    def get_players(self):
        """Gets all player information for players currently available on the Sleeper
        fantasy platform.

        Returns:
            list[dict]: all player information currently avaialble from Sleeper
        """
        return get("{}/{}".format(self._base_url, "nfl")).json()