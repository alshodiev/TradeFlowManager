def bs_str(buy_sell: bool) -> str:
    """ Convert a boolean buy_sell flag into a string"""
    return "BUY" if buy_sell else "SELL"

def bs_int(buy_sell: bool) -> int:
    """ Convert a boolean buy_sell flag into an integer"""
    return 1 if buy_sell else -1