from enum import Enum
from time import sleep
import json
from logging import getLogger

class Event(str, Enum): #
    Target = 'Target'
    Wait = 'Wait'
    LogPosition = 'LogPosition'

class Strategy: #
    """
    The Strategy class simply replays an event log to test the Position Manager
    """
    def __init__(self, position_manager):
        self.position_manager = position_manager
    
    def replay_events_log(self, events):

        for event in events:
            if event['Event'] == Event.Wait:
                sleep(event['Seconds'])
            elif event['Event'] == Event.Target:
                self.position_manager.update_target(event['Symbol'], event['Target'])
            elif event['Event'] == Event.LogPosition:
                self.position_manager.log_position()
            else:
                raise Exception('Unknown replay event')