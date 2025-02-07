import pytest
import threading
import json
import time
from io import StringIO
from system import *

def mock_event_log_input():
    return StringIO("""{"Event" : "LogPosition"}
    {"Event" : "Target", "Symbol" : "AAPL", "Target" : 80}
    {"Event" : "Wait", "Seconds" : 4}
    {"Event" : "LogPosition"}""")

def read_event_log(mock_input):
    """ Simulate reading the event log from stdin using StringIO. """
    event_log = []
    for line in mock_input:
        event = json.loads(line)
        event_log.append(event)
    return event_log

def test_full_pipeline():
    broker = Broker()
    position_manager = PositionManager(broker)

    # start the Position Manager in a separate thread
    thread_position_manager = threading.Thread(target=position_manager.match_position_to_target)
    thread_position_manager.start()

    # read the mocked event log and execute the strategy
    event_log = read_event_log(mock_event_log_input())
    strategy = Strategy(position_manager)
    strategy.replay_events_log(event_log)

    # thread termination
    broker.terminate_broker()
    position_manager.terminate_position_manager()
    thread_position_manager.join()

    # get the final state
    final_state = position_manager.get_current_state()

    # expected output structure
    expected_output = {
        "AAPL": {
            "Target": 80,
            "Position": 80,  # It should have matched the final target
            "Total Traded": 80  # Bought 200 initially, then sold 120
        }
    }

    assert "AAPL" in final_state
    assert final_state["AAPL"]["Target"] == expected_output["AAPL"]["Target"]
    assert final_state["AAPL"]["Position"] == expected_output["AAPL"]["Position"]
    assert final_state["AAPL"]["Total Traded"] == expected_output["AAPL"]["Total Traded"]

    print(json.dumps(final_state, indent=4))

