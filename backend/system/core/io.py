import sys
import json

def read_event_log_from_stdin():
    """
    Reads event log from standard input (stdin).
    Each line should represent a JSON object with event details.
    
    Returns:
        list: List of event dictionaries.
    """
    event_log = []
    try:
        for line in sys.stdin:
            events = json.loads(line)
            event_log.append(events)
    except Exception as e:
        print(f"Error reading event log: {e}")
    return event_log