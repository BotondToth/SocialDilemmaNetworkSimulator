from schema import Schema, And, Or

schema = Schema(
        {

            'n': And(int),
            'p': And(float),
            'm': And(int),
            'G': And(str),
            'competitive_probability': Or(And(float), And(str)),
            'pajek_path': And(str),
            'pay_off': And(list),
            'K': And(float),
            'ROUNDS': And(int),
            'change_update_rule': And(bool)
        }
    )