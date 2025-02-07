import os
from time import time
from random import random, randint
from time import sleep
from logging import getLogger
from typing import Callable
from logging import basicConfig
from core import *


basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
class Order: #
    """
    The Order class simulates an order being executed over time.
    Once order is filled, a trade confirmation will be sent to the submitter via the registered callback.
    If an order is canceled, the submitteed will still receive a trade confirmation for the partially filled amount.
    """

    def __init__(self,
                 order_id: int,
                 symbol: str,
                 amount: int,
                 buy_sell: bool,
                 broker_callback: Callable
    ):
        self.order_id = order_id
        self.symbol = symbol
        self.amount = amount
        self.buy_sell = buy_sell
        self.broker_callback = broker_callback

        self.amount_filled = 0
        self.cancelling = False
        self.logger = getLogger(f'Order-{order_id}')

    def execute_order(self):
        execute_order_start_time = time()
        while not self.cancelling and self.amount_filled < self.amount:
            filled = min(randint(1,20), self.amount - self.amount_filled)
            self.amount_filled += filled
            self.logger.debug(f'Filled {self.amount_filled} out of {self.amount} for {self.symbol}')
            sleep(random())
        
        self.logger.debug(f'Finished filling order id {self.order_id} {bs_str(self.buy_sell)} {self.amount_filled} {self.symbol}')
        confirmation = TradeConfirmation(self.order_id, self.symbol, self.amount_filled, self.buy_sell)
        self.broker_callback(confirmation)
        self.logger.debug(f'Executed order in {time() - execute_order_start_time} seconds')
    
    def cancel_order(self):
        self.logger.debug(f'Cancelling order id {self.order_id} {bs_str(self.buy_sell)} {self.amount_filled} {self.symbol}')
        self.cancelling = True