import os,sys
# To avoid 'no module named...' in trading_bot files importing
# local modules. Add trading_bot to path.
sys.path.insert(0, os.path.abspath('./trading_bot/'))

import unittest
from datetime import datetime
from pandas import DataFrame


from trading_bot.gateio_utils import ExchangeApi, Interval
from trading_bot.indicators import Indicators
from trading_bot.live_data import LiveData
from trading_bot.strategy_hammer import StrategyHammer


class TestStrategyHammer(unittest.TestCase):

    def test_start(self):
        """"Startegy hammer example 25th march at 9 on 1h chart."""
        self.exchange_api = ExchangeApi()
        self.contract = "BTC_USDT"
        self.live_data = LiveData()
        
        self.live_data.df = DataFrame(
                            self.exchange_api.get_candle_stick_time_range(
                                contract=self.contract,
                                interval=Interval.INT_1H,
                                start=datetime(2022, 3, 20, 10, 0),
                                end=datetime(2022, 3, 25, 9, 0)
                            ))
        indicators = Indicators()
        indicators.add_atr(self.live_data.df)
        # Add EMA 20 for hammer strategy
        indicators.add_ema(self.live_data.df, 20)

        strategy_hammer = StrategyHammer(self.live_data)
        strategy_hammer.start()

        self.assertTrue(strategy_hammer.is_setup_ready())
        self.assertEqual(strategy_hammer.entry, 44009.89)
        self.assertEqual(strategy_hammer.stop_loss, 43921.87022)
        self.assertEqual(strategy_hammer.target, 44097.90978)


if __name__ == '__main__':
    unittest.main()