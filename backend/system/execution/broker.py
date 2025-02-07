import os
import sys
import json
import threading
from enum import Enum
from time import time
from dataclasses import dataclass
from random import random, randint, seed
from time import sleep
from collections import defaultdict
from logging import getLogger, basicConfig
from queue import LifoQueue
from typing import Callable
from core import *
from order import Order

basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

class Broker: #
    """
    The Broker class provides a simple API for the Position Manager. Namely, to submit orders and cancel orders while providing
    a conduit to access executing orders.
    """
    def __init__(self):
        self.next_order_id = (i for i in range(sys.maxsize))
        self.orders_by_id = {}
        self.client_callback = None
        self.logger = getLogger('Broker')
    
    def register_client_trade_confirmation_callback(self, callback: Callable):
        self.logger.debug('Registered client trade confirmation callback')
        self.client_callback = callback
    
    def _trade_confirmation_callback(self, confirmation: TradeConfirmation):
        self.logger.debug(f'Received trade confirmation for order id {confirmation.trade_id} {bs_str(confirmation.buy_sell)} {confirmation.amount} {confirmation.symbol}')
        del self.orders_by_id[confirmation.trade_id]
        self.client_callback(confirmation)
    
    def order(self, symbol: str, amount: int, buy_sell: bool):
        self.logger.debug('Received order %s %i of %s' % (bs_str(buy_sell), amount, symbol))
        if self.client_callback is None:
            raise Exception('Unable to process order without first registering a client callback')
        
        order_id = next(self.next_order_id)
        order = Order(order_id, symbol, amount, buy_sell, self._trade_confirmation_callback)
        self.orders_by_id[order_id] = order
        self.logger.debug('Creating order id %i thread' % order_id)
        thread_order = threading.Thread(target = order.execute_order)
        thread_order.start()
        return order.order_id

    def terminate_broker(self):
        self.logger.debug('Terminating all orders from broker')
        for order in self.orders_by_id.values():
            order.cancel_order()
        
    def cancel_order(self, order_id: int):
        self.logger.debug('Canceling order id %i' % order_id)
        if order_id in self.orders_by_id:
            self.orders_by_id[order_id].cancel_order()
    
    def get_order(self, order_id: int):
        try:
            if order_id in self.orders_by_id:
                return self.orders_by_id[order_id]
            else:
                return None    
        except KeyError:
            return None