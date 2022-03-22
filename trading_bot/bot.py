import logging

from pandas import DataFrame

from gateio_utils import ExchangeApi
from indicators import Indicators
from plot_data import PlotData
from strategy_hammer import StrategyHammer


logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Bot():
    """Main class for automated trading.
    
    Attributes:
        exchange_api(ExchangeApi): API to exchange.
        contract(str): Currency pair.
        df(DataFrame): Data from exchange.
    
    Methods:
    start():
        Starts automated trading."""

    def __init__(self) -> None:
        self.exchange_api = ExchangeApi()
        self.contract = "BTC_USDT"
        self.df = DataFrame(
                    self.exchange_api.get_candle_stick(
                    contract=self.contract,
                    interval="1h",
                    limit=40))

    def start(self):
        """Starts automated trading."""
        indicators = Indicators()
        indicators.add_atr(self.df)
        # Add EMA 50 for hammer strategy
        indicators.add_ema(self.df, 50)

        strategy_hammer = StrategyHammer(self.df)
        strategy_hammer.start()
        if(strategy_hammer.is_setup_ready()):
            logger.info(
                "Hammer entry '{}' stop loss '{}' target profit '{}'"
                .format(
                    strategy_hammer.entry,
                    strategy_hammer.stop_loss,
                    strategy_hammer.target
                    )
                )
        else:
            logger.info("Not a hammer strategy setup.")


if __name__ == '__main__':
    bot = Bot()
    bot.start()
    PlotData.plot_ohlc(bot.df, bot.contract)

