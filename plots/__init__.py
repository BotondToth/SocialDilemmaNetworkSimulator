import random
from networkx import Graph, nx
import matplotlib.ticker as ticker
from strategy import Strategy, get_formatted_rule_name, UpdateRule, get_formatted_name
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from utilities import get_user_by_id
import pandas as pd

FIG_SIZE = (8, 6)


def show_plots(original_nodes, graph, nodes, update_rules_win_rates, competitive_ratio_by_games, update_rule_ratios):
    plot_player_network(graph, original_nodes, "Cooperative and defective players before the game")
    plot_player_network(graph, nodes, "Cooperative and defective players after the game", False)
    plot_win_ratios(nodes)
    plot_update_rule_win_ratios(update_rules_win_rates)
    plot_competitive_ratios(competitive_ratio_by_games)
    plot_update_rule_ratios(update_rule_ratios)
    plt.show()


def plot_player_network(graph: Graph, players, title: str, before_plot: bool = True):
    pos = nx.circular_layout(graph)
    pos = nx.spring_layout(graph, dim=2, pos=pos)
    plt.title(title)
    color_map = []
    for node in graph:
        user = get_user_by_id(players, node)
        if user.strategy == Strategy.COOPERATION.value:
            color_map.append('darkorange')
        else:
            color_map.append('crimson')
    nx.draw_networkx(graph, pos=pos, node_color=color_map, with_labels=True, node_size=300)
    cooperative_patch = mpatches.Patch(color='darkorange', label='Cooperative player')
    defective_patch = mpatches.Patch(color='crimson', label='Defective player')
    plt.legend(loc='best', handles=[cooperative_patch, defective_patch])
    if before_plot:
        plt.subplots(figsize=FIG_SIZE)


def plot_update_rule_ratios(update_rule_ratios):
    every_update_rule = [e.value for e in UpdateRule]
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    rule_rounds = dict()
    for rule in every_update_rule:
        rounds = []
        only_zeros_for_rule = True
        for ratios in update_rule_ratios:
            players_for_this_rule = ratios[UpdateRule(rule)]
            rounds.append(players_for_this_rule)
            if players_for_this_rule != 0:
                only_zeros_for_rule = False
        if not only_zeros_for_rule:
            rule_rounds.update({rule: rounds})

    displayed_rules = []
    for rule_round in rule_rounds:
        r = random.random()
        b = random.random()
        g = random.random()
        color = (r, g, b)
        plot_data = rule_rounds[rule_round]
        label, labeled_rules = get_label_for_update_rule(rule_round, rule_rounds)
        if rule_round not in displayed_rules:
            ax.plot(plot_data, label=label, c=color)
        displayed_rules = np.append(displayed_rules, labeled_rules)

    plt.legend(loc='best')
    ax.set(xlabel='Games', ylabel='Number of players',
           title='Number of players for each update rule during the game')
    ax.grid()
    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_major_locator(ticker.MaxNLocator(integer=True))


def get_label_for_update_rule(rule_round, rule_rounds):
    plot_data = rule_rounds[rule_round]
    label = get_formatted_name(rule_round)
    to_skip = [rule_round]
    displayed_rules = [rule_round]
    for r in list(rule_rounds):
        if r in to_skip:
            continue
        data = rule_rounds[r]
        if np.array_equal(plot_data, data):
            label += ", " + get_formatted_name(r)
            to_skip.append(r)
            displayed_rules.append(r)
    return label, displayed_rules


def plot_competitive_ratios(competitive_ratio_by_games):
    if len(competitive_ratio_by_games) < 2:
        return

    N = len(competitive_ratio_by_games)
    defective_ratios = [1 - x for x in competitive_ratio_by_games]
    ind = np.arange(N)
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    width = 0.3
    df = pd.DataFrame({'x_values': range(0, N), 'Competitive ratio': competitive_ratio_by_games, 'Defective ratio': defective_ratios})
    plt.xlabel('Games')
    plt.ylabel('Ratios')
    plt.title('Competitive ratios over time')
    ax.plot('x_values', 'Competitive ratio', data=df, marker='', color='darkorange', linewidth=2, label='Competitive ratio')
    ax.plot('x_values', 'Defective ratio', data=df, marker='', color='crimson', linewidth=2, label='Defective ratio')
    plt.xticks(ind + width / 2, (n for n in range(N)))
    plt.legend(loc='best')
    plt.show(block=False)


def plot_win_ratios(nodes):
    cooperative_rounds_won = 0
    defective_rounds_won = 0
    all_rounds_played = 0
    for node in nodes:
        cooperative_rounds_won += node.strategy_win_rate[Strategy.COOPERATION]
        defective_rounds_won += node.strategy_win_rate[Strategy.DEFECT]
        all_rounds_played += node.rounds_played

    cooperative_rounds_won /= all_rounds_played
    defective_rounds_won /= all_rounds_played

    labels = ["Cooperative win rate", "Defective win rate"]
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    bars = ax.bar(x - width / 2, [cooperative_rounds_won, defective_rounds_won], width, color=['darkorange', 'crimson'],
                  align='edge')

    ax.set_ylabel('Win rate')
    ax.set_title('Win rates of different strategies')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    autolabel(bars, ax)
    fig.tight_layout()
    plt.margins(0.2)
    plt.show(block=False)


def plot_update_rule_win_ratios(update_rules_win_rates: dict):
    all_rounds = sum(update_rules_win_rates.values())
    win_rates = [v / all_rounds for v in update_rules_win_rates.values()]
    labels = [get_formatted_rule_name(rule) for rule in update_rules_win_rates.keys()]
    x = np.arange(len(labels))
    width = 0.5

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    bars = ax.bar(x - width / 2, win_rates, width, align='edge')

    ax.set_ylabel('Update rule win rates')
    ax.set_title('Win rates of different update rules')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25)

    autolabel(bars, ax)
    fig.tight_layout()
    plt.margins(0.1)
    plt.show(block=False)


def autolabel(rects, ax):
    for rect in rects:
        height = rect.get_height()
        ax.annotate("{:.0%}".format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')


def autolabel_count(rects, ax):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(height,
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
