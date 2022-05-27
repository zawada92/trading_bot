import datetime
import logging
import time

from pandas import DataFrame

from gateio_utils import ExchangeApi, Interval
from indicators import Indicators
from plot_data import PlotData
from strategy_hammer import StrategyHammer
from live_data import LiveData
from strategy import Strategy


log_format = "%(asctime)s: %(message)s"
# To append existing bot.log file use filemode = "a"
# To overwrite existing log file or create new if not exist use filemode = "w"
logging.basicConfig(
            filename = "bot.log",
            filemode = "a",
            format=log_format,
            level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Bot():
    """Main class for automated trading.
    
    Attributes:
        exchange_api(ExchangeApi): API to exchange.
        limit(int): Last number of candles to download
        contract_list(list): List of contracts.
        live_data(LiveData): Object storing real time downoaded
            charts data.
    
    Methods:
    start():
        Starts automated trading.
    strategy_exec():
        Strategy execution."""

    def __init__(self) -> None:
        self.exchange_api = ExchangeApi()
        self.live_data = LiveData()
        self.limit = 40 
        self.contract_list = [
            "BTC_USDT",
            "ETH_USDT",
            "BNB_USDT",
            "SOL_USDT",
            "LUNA_USDT",
            "XRP_USDT",
            "ADA_USDT",
            "AVAX_USDT",
            "DOT_USDT",
            "DOGE_USDT",
            "SHIB_USDT"
        ]

    def strategy_exec(
        self,
        indicators: Indicators,
        strategy: Strategy,
        interval: str
    ) -> None:
        """Strategy execution.

        Params:
            indicators(Indicators): Object to add chart indicators.
            strategy(Strategy): Object of strategy to execute.
            interval(str): Interval for downloading data.
        """
        logger.debug("Strategy execution start")
        for contract_pair in self.contract_list:
            self.live_data.df = DataFrame(
                                    self.exchange_api.get_candle_stick(
                                    contract=contract_pair,
                                    interval=interval,
                                    limit=self.limit))
            indicators.add_atr(self.live_data.df)
            # Add EMA 20 for hammer strategy
            indicators.add_ema(self.live_data.df, 20)

            strategy.start()

            if strategy.is_setup_ready():
                logger.debug("'{}' entry '{}' stop loss: '{}' target: '{}'"
                    .format(
                        contract_pair,
                        strategy.entry,
                        strategy.stop_loss,
                        strategy.target))

                PlotData.plot_ohlc(self.live_data.df, contract_pair, True)
                strategy.clear()
            else:
                logger.debug("Setup not found '{}'".format(contract_pair))
                # if contract_pair == "BTC_USDT":
                #     PlotData.plot_ohlc(self.live_data.df, contract_pair, True)

        logger.debug("Strategy execution end")

    def start(self):
        """Starts automated trading."""

        logger.debug("Automated trading bot start!")

        indicators = Indicators()
        strategy_hammer = StrategyHammer(self.live_data)

        now = datetime.datetime.now()
        while True:
            while now.minute % 5 or now.second > 2:
                time.sleep(1)
                now = datetime.datetime.now()
            self.strategy_exec(indicators, strategy_hammer, Interval.INT_5M)
            now = datetime.datetime.now()        


if __name__ == '__main__':
    bot = Bot()
    bot.start()

