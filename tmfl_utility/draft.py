from requests import get

class Draft:
    def __init__(self, draft_id):
        self.draft_id = draft_id
        self._base_url = "https://api.sleeper.app/v1/draft/{}".format(draft_id)

    def get_picks(self):
        picks = get("{}/{}".format(self._base_url, "picks")).json()
        return {p.get("player_id"): p for p in picks}