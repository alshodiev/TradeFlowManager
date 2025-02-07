from dataclasses import dataclass

@dataclass
class TradeConfirmation: #
    """ Dataclass for trade confirmation """
    trade_id: int
    symbol: str
    amount: int
    buy_sell: bool

    def __str__(self) -> str:
        direction = "BUY" if self.buy_sell else "SELL"
        return f"TradeConfirmation(trade_id={self.trade_id}, symbol={self.symbol}, amount={self.amount}, direction={direction})"
    