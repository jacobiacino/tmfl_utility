from requests import get
from tmfl_utility.players import Players
from tmfl_utility.keeper_rules import KeeperRules
from tmfl_utility.roster import Roster
from tmfl_utility.draft import Draft

class League:
    def __init__(self, league_id, keeper_rules = KeeperRules()):
        self.league_id = league_id
        self._base_url = "https://api.sleeper.app/v1/league/{}".format(self.league_id)
        self.keeper_rules = keeper_rules

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
            and transaction['type'] in ['waiver', 'free_agent', 'commissioner']


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
        # P = Players()
        # players = P.get_players()
        all_adds = set()
        for i in range(1, 18):
            transactions = get("{}/transactions/{rnd}".format(self._base_url, rnd=i)).json()
            # for t in transactions:
            #     if t['adds'] is not None:
            #         if '7526' in t['adds'].keys():
            #             print('shits here')
            waiver_or_fa_adds = {
                k for sublist in [
                    t['adds'].keys() for t in transactions \
                        if self.__is_completed_waiver_or_fa_add(t)
                ] for k in sublist
            }
            all_adds = all_adds.union(waiver_or_fa_adds)

        # return [
        #     {
        #         'id': a,
        #         'name': players[a].get('search_full_name', a),
        #         'positions': players[a].get('fantasy_positions')
        #     }
        #     for a in all_adds
        # ]

        return all_adds
    
    def get_rosters(self):
        """Returns all current league rosters

        Returns:
            list[Roster]: list of all current rosters
        """
        rosters = get("{}/{}".format(self._base_url, "rosters")).json()
        return [Roster(r.get("roster_id"), r.get("owner_id"), r.get("players"), self.keeper_rules) for r in rosters]

    def get_draft(self):
        """Gets the first available draft for this league

        Returns:
            Draft: first available draft for this league
        """
        draft_id = get("{}/{}".format(self._base_url, "drafts")).json()[0].get("draft_id")
        return Draft(draft_id)

    def get_keeper_report(self):
        """returns a list of all currently rostered players' keeper eligibility
        and their cost, based on the provided league rules

        Returns:
            list[dict]: player keeper eligibility and cost
        """
        draft = self.get_draft()
        rosters = self.get_rosters()
        waiver_adds = self.get_completed_waiver_or_fa_adds()
        all_keeps = []
        for r in rosters:
            kc = r.get_keeper_costs(draft, waiver_adds)
            all_keeps = all_keeps + kc
        return all_keeps