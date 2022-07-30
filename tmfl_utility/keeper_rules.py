class KeeperRules:
    def __init__(self, excluded_rounds = [], round_cost = 0, free_agent_cost = -1):
        """Keeper rules for your league. Includes flexibility for increasing round
        cost, excluding rounds from being kept, and free agent costs

        Args:
            excluded_rounds (list, optional): list of rounds that
            keepers are excluded from. If your league does not allow
            first and second round picks to be kept, this would be [1,2].
            Must be populated with positive integers. Defaults to [].
            
            round_cost (int, optional): The increase in round cost from original draft
            to keep a player. If an original 3rd round pick costs a 2nd rounder this year
            this value would be 1. Defaults to 0.

            free_agent_cost (int, optional): the round cost of a free agent.
            If free agents are not allowed to be kept, set to -1. Defaults to -1.
        """
        for r in excluded_rounds:
            if r <= 0:
                raise ValueError(
                    "non-positive round: {} given. All excluded rounds must be >= 1" \
                        .format(r)
                )
        self.excluded_rounds = excluded_rounds
        self.round_cost = round_cost
        self.free_agent_cost = free_agent_cost