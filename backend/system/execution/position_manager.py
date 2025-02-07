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
from system.core import *
from .broker import Broker

basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

class PositionManager:
    """
    The Position Manager class is a service provided to the strategy.
    It manages placing new orders and canceling existing orders to 
    hit the target positions provided by the strategy.
    """
    def __init__(self, broker: Broker):
        self.broker = broker
        self.broker.register_client_trade_confirmation_callback(self._trade_confirmation_callback)
        
        self.position_by_symbol = defaultdict(int)
        self.target_by_symbol = defaultdict(int)
        self.order_ids_by_symbol = defaultdict(list)
        self.total_traded_by_symbol = defaultdict(int)

        self.target_queue = LifoQueue()
        self.trade_queue = LifoQueue()

        self.terminate = False

        self.logger = getLogger("Position Manager")
        self.logger.debug('Position Manager Initalized')

    def get_current_state(self):
        state = {}
        for symbol in self.position_by_symbol:
            state[symbol] = \
                {
                    'Target' : self.target_by_symbol[symbol],
                    'Position' : self.position_by_symbol[symbol],
                    'Total Traded' : self.total_traded_by_symbol[symbol]
                }
        return state

    def update_target(self, symbol: str, amount: int):
        self.logger.debug(f'Received target update for {symbol} and amount ${amount}')
        self.target_queue.put((symbol, amount))
    
    def _trade_confirmation_callback(self, confirmation: TradeConfirmation):
        self.logger.debug('Received confirmation %s %i of %s' %
                          (bs_str(confirmation.buy_sell), confirmation.amount, confirmation.symbol))
        self.trade_queue.put((confirmation.trade_id, confirmation.symbol, confirmation.amount, confirmation.buy_sell))

    def _update_position(self):
        symbols = []

        while not self.trade_queue.empty():
            trade_id, symbol, amount, buy_sell = self.trade_queue.get()
            self.order_ids_by_symbol[symbol].remove(trade_id)
            self.logger.debug('Updating position with %s %i of %s' % (bs_str(buy_sell), amount, symbol))
            self.position_by_symbol[symbol] += amount * bs_int(buy_sell)
            self.total_traded_by_symbol[symbol] += amount
            symbols.append(symbol)
        return symbols

    def _update_target(self):
        symbols = []
        while not self.target_queue.empty():
            symbol, amount = self.target_queue.get()
            self.logger.debug('Updating target %s %i' % (symbol, amount))
            self.target_by_symbol[symbol] = amount
            symbols.append(symbol)
        return symbols

    def cancel_orders(self, order_id : int):
        self.broker.cancel_order(order_id)
    
    def place_order(self, symbol: str, amount: int, buy_sell: bool):
        new_order_id = self.broker.order(symbol, amount, buy_sell)
        self.order_ids_by_symbol[symbol].append(new_order_id)
        self.logger.debug(f'Placed {"buy" if buy_sell else "sell"} order for {amount} shares of {symbol}')
        
    
    def maybe_get_order(self, order_id: int):
        return self.broker.get_order(order_id) #get_order might return None
    
    def match_position_to_target(self):
        
        self.logger.debug('Started running Position Manager')

        while not self.terminate:

            symbols_update = self._update_position()
            symbols_target = self._update_target()
            
            to_check = set(symbols_update + symbols_target)

            self.logger.debug('Processing delta between target, position, and orders')
            for symbol, target_position in self.target_by_symbol.items():
                if symbol not in to_check:
                    continue
                current_position = self.position_by_symbol[symbol]

                if symbol in self.order_ids_by_symbol:
                    for order_id in self.order_ids_by_symbol[symbol]:
                        maybe_order = self.maybe_get_order(order_id)
                        if maybe_order is not None:
                            current_position += maybe_order.amount_filled * bs_int(maybe_order.buy_sell)
                
                delta = target_position - current_position
                self.logger.debug('Position delta for %s is %i' % (symbol, delta))

                # Match current_position to target_position form the calculated delta. You can:
                    # To place new order:
                        # self.place_order(symbol, amount, buy_sell)
                    # To cancel an order:
                        # self.cancel_order(order_id)
                    # To get partially filled orders:
                        # maybe_order = self.maybe_get_order(order_id)
                # When you cancel an order, the partially filled amount will be confirmed as a trade and the local dicts
                # will be automatically updated

            while not self.terminate and self.trade_queue.qsize() == 0 and self.target_queue.qsize() == 0:
                sleep(0.001)

        self.logger.debug('Exiting Position Manager')
    
    def terminate_position_manager(self):
        self.logger.debug('Terminating Position Manager')
        self.terminate = True
    
    def log_position(self):
        state = self.get_current_state()
        self.logger.debug(json.dumps(state))
