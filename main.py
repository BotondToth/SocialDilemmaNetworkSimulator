import sys
from networkx import Graph
import copy
from plots import show_plots
from random_graphs import get_graph_from_name
import numpy as np

from strategy import Round, UpdateRule, Strategy
from utilities import get_user_by_id, \
    calculate_d_max, \
    init_random_players, \
    play_a_round, update_strategy
from schema import SchemaError
from config_schema import schema
import yaml

from multiprocessing.pool import ThreadPool as Pool


def read_config_yml(file_path: str):
    with open(file_path, "r") as f:
        config_data = yaml.safe_load(f)
        try:
            schema.validate(config_data['SIMULATION'])
            return config_data
        except SchemaError as e:
            print(e)


def simulate_round(node_pair, players, d_max, graph, change_update_rule):
    row_player = get_user_by_id(players, node_pair[0])
    column_player = get_user_by_id(players, node_pair[1])
    if row_player is None or column_player is None:
        return

    row_player_round_pay_off = 0
    column_player_round_pay_off = 0
    row_player_results = Round(row_player.id, 0, row_player.strategy)
    column_player_results = Round(column_player.id, 0, column_player.strategy)
    for i in range(ROUNDS):
        row_player_results, column_player_results = play_a_round(row_player, column_player, pay_off_matrix)
        row_player_round_pay_off += row_player_results.payoff
        column_player_round_pay_off += column_player_results.payoff
        if column_player_results.payoff < row_player_results.payoff:
            update_rules_win_rates[row_player.update_rule] += 1
        elif row_player_results.payoff < column_player_results.payoff:
            update_rules_win_rates[column_player.update_rule] += 1
        else:
            update_rules_win_rates[row_player.update_rule] += 1
            update_rules_win_rates[column_player.update_rule] += 1

    update_rules_played[row_player.update_rule] += ROUNDS
    update_rules_played[column_player.update_rule] += ROUNDS
    update_strategy(
        graph,
        players,
        row_player_results,
        column_player_results,
        column_player_results.payoff < row_player_results.payoff,
        competitive_probability,
        d_max,
        K,
        change_update_rule
    )
    update_strategy(
        graph,
        players,
        column_player_results,
        row_player_results,
        row_player_results.payoff < column_player_results.payoff,
        competitive_probability,
        d_max,
        K,
        change_update_rule
    )
    competitive_players = 0
    update_rules_ratios = EMPTY_UPDATE_RULE_DICT.copy()
    for player in players:
        if player.strategy == Strategy.COOPERATION.value:
            competitive_players += 1
        update_rules_ratios[UpdateRule(player.update_rule)] = update_rule_ratios[player.update_rule] + 1
    for r in every_update_rule:
        if UpdateRule(r) not in update_rules_ratios:
            update_rules_ratios[UpdateRule(r)] = 0
    competitive_ratio_by_games.append(competitive_players / len(players))
    update_rule_ratios_holder.append(update_rules_ratios)


def play(graph: Graph, players, d_max: int, change_update_rule: bool):
    pool_size = 5
    pool = Pool(pool_size)

    edges = list(graph.edges())
    for node_pair in edges:
        pool.apply_async(simulate_round, (node_pair, players, d_max, graph, change_update_rule))

    pool.close()
    pool.join()


config = read_config_yml("./config.yaml")
if not config:
    sys.exit("Cannot parse the provided config file, check logs above for exact error message.")

simulation_settings = config["SIMULATION"]
competitive_probability = simulation_settings["competitive_probability"]
n = simulation_settings["n"]
p = simulation_settings["p"]
m = simulation_settings["m"]
pajek_path = simulation_settings["pajek_path"]
G = get_graph_from_name(simulation_settings["G"], n, p, m, pajek_path)
K = simulation_settings["K"]
nodes = init_random_players(n, competitive_probability)
original_nodes = copy.deepcopy(nodes)
pay_off_matrix = np.array(simulation_settings["pay_off"])
ROUNDS = simulation_settings["ROUNDS"]
change_update_rule = simulation_settings["change_update_rule"]


update_rules_win_rates = dict()
update_rules_played = dict()
update_rule_ratios_holder = []
update_rule_ratios = dict()
EMPTY_UPDATE_RULE_DICT = update_rule_ratios.copy()
every_update_rule = [e.value for e in UpdateRule]
for rule in every_update_rule:
    update_rules_win_rates[UpdateRule(rule)] = 0
    update_rules_played[UpdateRule(rule)] = 0
    update_rule_ratios[UpdateRule(rule)] = 0

for n in nodes:
    player_update_rule = update_rule_ratios[n.update_rule]
    update_rule_ratios[UpdateRule(n.update_rule)] = player_update_rule + 1

update_rule_ratios_holder.append(update_rule_ratios)
competitive_ratio_by_games = []
play(G, nodes, calculate_d_max(pay_off_matrix), change_update_rule)
show_plots(original_nodes, G, nodes, update_rules_win_rates, competitive_ratio_by_games, update_rule_ratios_holder)
