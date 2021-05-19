from strategy.round import Round
import enum
from math import e


class Strategy(enum.Enum):
    COOPERATION = 0
    DEFECT = 1


def get_formatted_rule_name(rule):
    if rule is UpdateRule.RANDOM:
        return "Random"
    if rule is UpdateRule.ADAPT:
        return "Adapt"
    if rule is UpdateRule.TIT_FOR_TAT:
        return "TitForTat"
    if rule is UpdateRule.REPLICATOR_DYNAMICS:
        return "Replicator Dynamics"
    if rule is UpdateRule.BEST_TAKES_OVER:
        return "BestTakesOver"
    if rule is UpdateRule.LOGIT_REPLICATOR_DYNAMICS:
        return "Logit Replicator Dynamics"


def get_formatted_name(rule_id: int):
    switch = {
        0: "Random",
        1: "Adapt",
        2: "Tit for tat",
        3: "Replicator dynamics",
        4: "Best takes over",
        5: "Logit replicator dynamics"
    }
    return switch.get(rule_id)


class UpdateRule(enum.Enum):
    RANDOM = 0
    ADAPT = 1
    TIT_FOR_TAT = 2
    REPLICATOR_DYNAMICS = 3
    BEST_TAKES_OVER = 4
    LOGIT_REPLICATOR_DYNAMICS = 5


def replicator_dynamics(player, opponent, d_max):
    G_i = (player.pay_off_sum / player.rounds_played) / player.rounds_played
    G_j = (opponent.pay_off_sum / opponent.rounds_played) / opponent.rounds_played
    if G_i < G_j:
        return (G_i - G_j) / d_max
    else:
        return None


def logit_replicator_dynamics(player_avg_pay_off, random_neighbour_avg_pay_off, K: float):
    return 1 / (1 + pow(e, -1 * (random_neighbour_avg_pay_off - player_avg_pay_off) / K))
