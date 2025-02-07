import pytest
import time
from system import Broker, Order, TradeConfirmation

@pytest.fixture
def broker_and_confirmation():
    broker = Broker()
    trade_confirmations = []

    def mock_client_callback(confirmation: TradeConfirmation):
        trade_confirmations.append(confirmation)

    # what does this line do?
    broker.register_client_trade_confirmation_callback(mock_client_callback)
    return broker, trade_confirmations

def test_order_submission_and_execution(broker_and_confirmation):
    broker, trade_confirmations = broker_and_confirmation

    order_id = broker.order("AAPL", 100, True)

    # Let the thread execute for a short time to fill the order
    time.sleep(2) # why do we want to simulate asynchronous order execution?

    assert len(trade_confirmations) > 0
    trade_confirmation = trade_confirmations[0]

    # validating that a trade confirmation was received
    assert trade_confirmation.symbol == "AAPL"
    assert 0 < trade_confirmation.amount <= 100
    assert trade_confirmation.buy_sell is True






