import logging
import pandas as pd

from gateio_utils import ExchangeApi
from plot_data import PlotData


logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Bot():
    """Main class for automated trading."""

    def __init__(self) -> None:
        self.exchange_api = ExchangeApi()
        self.df = pd.DataFrame(
                    self.exchange_api.get_candle_stick(
                    contract="BTC_USDT",
                    interval="1h",
                    limit=10))


if __name__ == '__main__':
    bot = Bot()
    PlotData.plot_ohlc(bot.df)

