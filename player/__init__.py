from dataclasses import dataclass
from strategy import UpdateRule


@dataclass
class Player:
    id: int
    rounds_played: int
    rounds_won: int
    update_rule: UpdateRule
    strategy_win_rate: {}
    strategy: int
    pay_off_sum: int
