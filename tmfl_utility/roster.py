from tmfl_utility import keeper_rules
from tmfl_utility.keeper_rules import KeeperRules
from tmfl_utility.draft import Draft
from tmfl_utility.user import User

class Roster:
    def __init__(self, roster_id, owner_id, players, keeper_rules = KeeperRules()):
        """A roster of players in a sleeper league

        Args:
            roster_id (integer): sleeper roster id
            owner_id (string): sleeper owner id
            players (list[string]): list of playerids on roster
        """
        self.roster_id = roster_id
        self.players = players
        self.owner_id = owner_id
        self.owner = User(owner_id)
        self.keeper_rules = keeper_rules

    def get_keeper_costs(self, draft:Draft, waiver_adds_list:list):
        picks = draft.get_picks()
        keeper_costs = []
        for p in self.players:
            player_info = picks.get(p, None)
            keeper_info = {
                "rights_holder": self.owner.display_name,
                "id": p,
                "round_selected": -1 if player_info == None else player_info["round"],
                "keeper_eligible": True
            }
            if p in waiver_adds_list:
                keeper_info["round_selected"] = -1
                keeper_info["keeper_eligible"] = False
            
            if keeper_info.get("round_selected") in self.keeper_rules.excluded_rounds:
                keeper_info["keeper_eligible"] = False
                keeper_info["keeper_cost"] = -1

            if self.keeper_rules.free_agent_cost == -1:
                if keeper_info["round_selected"] == -1:
                    keeper_info["keeper_eligible"] = False
                    keeper_info["keeper_cost"] = -1

            if keeper_info["keeper_eligible"]:
                keeper_info["keeper_cost"] = keeper_info["round_selected"] \
                    - self.keeper_rules.round_cost

            keeper_costs.append(keeper_info)
        return keeper_costs
        

        return