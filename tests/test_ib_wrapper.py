from source.ib import client, wrapper
from source.ib.finishable_queue import FinishableQueue, Status
from ibapi.contract import Contract
from ibapi.wrapper import (
    ListOfHistoricalTick, ListOfHistoricalTickBidAsk, ListOfHistoricalTickLast
)

import enum
import threading
import unittest

class Const(enum.Enum):
    RID_RESOLVE_CONTRACT = 43
    RID_FETCH_HISTORICAL_TICKS = 18001
    QUEUE_MAX_WAIT_SEC = 10

class TestIBWrapper(unittest.TestCase):
    contract = Contract()
    contract.secType = "STK"
    contract.symbol = "AAPL"
    contract.exchange = "SMART"
    contract.currency = "USD"

    def setUp(self):
        self.wrapper = wrapper.IBWrapper()
        self.client = client.IBClient(self.wrapper)

        self.client.connect('127.0.0.1', 4002, 1001)

        thread = threading.Thread(target=self.client.run)
        thread.start()

        setattr(self.client, "_thread", thread)

        self.resolved_contract = self.client.resolve_contract(
            self.contract, Const.RID_RESOLVE_CONTRACT.value
        )

        print(self.resolved_contract)

    def test_historical_ticks(self):
        end_time = "20200327 16:30:00"

        queue = FinishableQueue(
            self.wrapper.init_historical_ticks_data_queue(
                Const.RID_FETCH_HISTORICAL_TICKS.value
            )
        )

        self.client.reqHistoricalTicks(
            Const.RID_FETCH_HISTORICAL_TICKS.value, self.resolved_contract,
            "", end_time, 1000, "MIDPOINT", 1, False, []
        )

        result = queue.get(timeout=Const.QUEUE_MAX_WAIT_SEC.value)

        self.assertFalse(self.wrapper.has_err())
        self.assertNotEqual(queue.get_status(), Status.TIMEOUT)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ListOfHistoricalTick)

    def test_historical_ticks_bid_ask(self):
        end_time = "20200327 16:30:00"

        queue = FinishableQueue(
            self.wrapper.init_historical_ticks_data_queue(
                Const.RID_FETCH_HISTORICAL_TICKS.value
            )
        )

        self.client.reqHistoricalTicks(
            Const.RID_FETCH_HISTORICAL_TICKS.value, self.resolved_contract,
            "", end_time, 1000, "BID_ASK", 1, False, []
        )

        result = queue.get(timeout=Const.QUEUE_MAX_WAIT_SEC.value)

        self.assertFalse(self.wrapper.has_err())
        self.assertNotEqual(queue.get_status(), Status.TIMEOUT)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ListOfHistoricalTickBidAsk)

    def test_historical_ticks_last(self):
        end_time = "20200327 16:30:00"

        queue = FinishableQueue(
            self.wrapper.init_historical_ticks_data_queue(
                Const.RID_FETCH_HISTORICAL_TICKS.value
            )
        )

        self.client.reqHistoricalTicks(
            Const.RID_FETCH_HISTORICAL_TICKS.value, self.resolved_contract,
            "", end_time, 1000, "TRADES", 1, False, []
        )

        result = queue.get(timeout=Const.QUEUE_MAX_WAIT_SEC.value)

        self.assertFalse(self.wrapper.has_err())
        self.assertNotEqual(queue.get_status(), Status.TIMEOUT)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ListOfHistoricalTickLast)

    def tearDown(self):
        self.client.disconnect()
