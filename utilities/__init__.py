from random import randrange, random, choice
from typing import Tuple
import numpy as np
from networkx import Graph
import json
from player import Player
from strategy import UpdateRule, Strategy, Round, replicator_dynamics, logit_replicator_dynamics


def draw_update_rule(): return UpdateRule(randrange(len(UpdateRule)))


def get_random_strategy(node_id: int, c_prob):
    if type(c_prob) == float:
        return Strategy.COOPERATION.value if random() <= c_prob else Strategy.DEFECT.value
    if c_prob == "random":
        return Strategy.COOPERATION.value if random() <= 0.5 else Strategy.DEFECT.value
    with open(c_prob) as json_file:
        strategies = json.load(json_file)
        # reason behind +1: nodes  are 0-based, input file is not
        return Strategy.COOPERATION.value if strategies[str(node_id + 1)] == "C" else Strategy.DEFECT.value


def calculate_d_max(pay_off_matrix): return np.max(pay_off_matrix) - np.min(pay_off_matrix)


def get_user_by_id(users, node_id):
    return next((user for user in users if user.id == node_id))


def get_neighbours(player_id: int, network: Graph): return list(network.neighbors(player_id))


def find_most_successful_player(network, player, players):
    max_pay_off = 0
    best_id = player.id
    for related_players in network.edges(player.id):
        related_player = get_user_by_id(players, related_players[1])
        if max_pay_off < related_player.pay_off_sum:
            max_pay_off = related_player.pay_off_sum
            best_id = related_player.id
    return best_id


def init_random_players(nodes: int, c_prob):
    """ c_prob: float, random or file path"""
    initialized_players = []
    for user_id in range(nodes):
        player_update_rule = draw_update_rule()
        player_strategy = \
            Strategy.COOPERATION.value if player_update_rule is UpdateRule.TIT_FOR_TAT else get_random_strategy(user_id, c_prob)

        initialized_players.append(
            Player(
                id=user_id,
                rounds_played=0,
                rounds_won=0,
                update_rule=player_update_rule,
                strategy=player_strategy,
                strategy_win_rate={Strategy.COOPERATION: 0, Strategy.DEFECT: 0},
                pay_off_sum=0
            )
        )
    return initialized_players


def simulate(pay_off_matrix, row_player: Player, column_player: Player) \
        -> Tuple[Round, Round]:
    row_payoff = pay_off_matrix[0]
    column_payoff = pay_off_matrix[1]

    row_sum = row_payoff[0][0] \
        if row_player.strategy == Strategy.COOPERATION.value else row_payoff[1][0]
    column_sum = column_payoff[0][1] \
        if column_player.strategy == Strategy.COOPERATION.value else column_payoff[1][1]
    return Round(row_player, row_sum, row_player.strategy), Round(column_player, column_sum, column_player.strategy)


def update_strategy(network: Graph, players, result: Round, opponent_result: Round, won_round: bool, comp_prob: float, d_max: int, K: float, change_update_rule: bool):
    player = result.node
    opponent = opponent_result.node
    edited = False
    original_player_strategy = player.strategy
    changed_rule = None
    if player.update_rule is UpdateRule.RANDOM and not won_round and type(comp_prob) != str:
        player.strategy = \
            Strategy.COOPERATION.value if random() < comp_prob else Strategy.DEFECT.value
        if original_player_strategy != player.strategy and change_update_rule:
            changed_rule = opponent.update_rule
            edited = True
    if player.update_rule is UpdateRule.ADAPT and not won_round:
        player.strategy = opponent.strategy
        if change_update_rule:
            changed_rule = opponent.update_rule
            edited = True
    if player.update_rule is UpdateRule.TIT_FOR_TAT:
        player.strategy = opponent.strategy
        if change_update_rule:
            changed_rule = opponent.update_rule
            edited = True
    if player.update_rule is UpdateRule.REPLICATOR_DYNAMICS:
        replicator_value = replicator_dynamics(player, opponent, d_max)
        if replicator_value is None:
            return
        player.strategy = opponent.strategy if random() < replicator_value else player.strategy
        if original_player_strategy != player.strategy and change_update_rule:
            edited = True
    if player.update_rule is UpdateRule.BEST_TAKES_OVER and not won_round:
        most_successful_player = get_user_by_id(players, find_most_successful_player(network, player, players))
        player.strategy = most_successful_player.strategy
        if change_update_rule:
            changed_rule = most_successful_player.update_rule
            edited = True
    if player.update_rule is UpdateRule.LOGIT_REPLICATOR_DYNAMICS:
        player_neighbours = get_neighbours(player.id, network)
        random_neighbour_id = choice(player_neighbours)
        random_neighbour = get_user_by_id(players, random_neighbour_id)
        player_avg_pay_off = player.pay_off_sum / player.rounds_played

        if random_neighbour.rounds_played == 0:
            return

        random_neighbour_avg_pay_off = random_neighbour.pay_off_sum / random_neighbour.rounds_played
        if random_neighbour is None:
            print("Error: player with id not found: ", random_neighbour_id)
        change_prob = logit_replicator_dynamics(player_avg_pay_off, random_neighbour_avg_pay_off, K)
        if random() <= change_prob:
            player.strategy = random_neighbour.strategy
            if change_update_rule:
                changed_rule = random_neighbour.update_rule
                edited = True
    if edited and change_update_rule and change_update_rule is not None:
        change_update_rule(player, changed_rule)


def change_player_update_rule(player, update_rule):
    player.update_rule = update_rule


def play_a_round(row_player: Player,
                 column_player: Player,
                 pay_off_matrix: np.ndarray):
    # get results for both player
    row_player_results, column_player_results = simulate(pay_off_matrix, row_player, column_player)

    # record pay offs by the result of this round
    row_player.pay_off_sum += row_player_results.payoff
    column_player.pay_off_sum += column_player_results.payoff

    if row_player_results.payoff < column_player_results.payoff:
        column_player.rounds_won += 1
        rounds_won_by_current_strategy = column_player.strategy_win_rate[Strategy(column_player.strategy)]
        column_player.strategy_win_rate[Strategy(column_player.strategy)] = rounds_won_by_current_strategy + 1

    elif row_player_results.payoff != column_player_results.payoff:
        row_player.rounds_won += 1
        rounds_won_by_current_strategy = row_player.strategy_win_rate[Strategy(row_player.strategy)]
        row_player.strategy_win_rate[Strategy(row_player.strategy)] = rounds_won_by_current_strategy + 1

    row_player.rounds_played += 1
    column_player.rounds_played += 1

    return row_player_results, column_player_results
