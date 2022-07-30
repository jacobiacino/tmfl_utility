from requests import get
from tmfl_utility.players import Players

class League:
    def __init__(self, league_id):
        self.league_id = league_id
        self._base_url = "https://api.sleeper.app/v1/league/{}".format(self.league_id)

    def get_league(self):
        """Return all league information

        Returns:
            dict: All league metadata
        """
        return get(self._base_url)

    def __is_completed_waiver_or_fa_add(self, transaction):
        """Evaluates a player transaction to determine if it was a successful waiver or
        free agent roster addition

        Args:
            transaction ([dict]): a sleeper league player transaction

        Returns:
            bool: True if the transaction was a successful waiver or free agent player add
            False otherwise
        """
        return transaction['adds'] is not None \
            and transaction['status'] == 'complete' \
            and transaction['type'] in ['waiver', 'free_agent']


    def get_completed_waiver_or_fa_adds(self):
        """Gets all successfull waiver or free agent claims for a league. This is a useful
        utility for evaulating players that fall under free agent keeper rules.

        Args:
            league_id (integer): the league id to examine

        Returns:
            list[dict]: A list of all players that were successfully added to a roster
            through waivers or free agency. returned with the following elements:
                id: string
                name: string
                positions: list[string]
        """
        P = Players()
        players = P.get_players()
        all_adds = set()
        for i in range(1, 18):
            transactions = get("{}/transactions/{rnd}".format(self._base_url, rnd=i)).json()
            waiver_or_fa_adds = {
                k for sublist in [
                    t['adds'].keys() for t in transactions \
                        if self.__is_completed_waiver_or_fa_add(t)
                ] for k in sublist
            }
            all_adds = all_adds.union(waiver_or_fa_adds)

        return [
            {
                'id': a,
                'name': players[a].get('search_full_name', a),
                'positions': players[a].get('fantasy_positions')
            }
            for a in all_adds
        ]