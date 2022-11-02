import gate_api
import logging

from datetime import datetime, timezone
from gate_api.exceptions import ApiException, GateApiException


logger = logging.getLogger(__name__)


class Interval:
    """Intervals constant Strings."""

    INT_10S = "10s"
    INT_1M = "1m"
    INT_5M = "5m"
    INT_15M = "15m"
    INT_30M = "30m"
    INT_1H = "1h"
    INT_4H = "4h"
    INT_8H = "8h"
    INT_1D = "1d"
    INT_7D = "7d"


class ExchangeApi:
    """Util class for crypto exchange interactions.

    Attributes:
        configuration(Configurationa): API configuration
        api_client(ApiClient): API client
        api_instance(SpotApi): Spot API instance
        settle(str): Settle currency

    Methods:
    get_candle_stick(contract, interval, limit=100):
        Download data in candle stick format (ohlc)"""

    def __init__(self) -> None:
        # Defining the host is optional and defaults to:
        # https://api.gateio.ws/api/v4
        self.configuration = gate_api.Configuration(
            host="https://api.gateio.ws/api/v4"
        )
        self.api_client = gate_api.ApiClient(self.configuration)
        # Create an instance of the API class
        self.api_instance = gate_api.SpotApi(self.api_client)
        self.settle = "usdt"  # str | Settle currency

    def get_candle_stick(
        self, contract: str, interval: str, limit: int = 100
    ) -> list:
        """Download data in candle stick format (ohlc) for crypto pair,
        f.e. BTC_USDT.

        Params:
            contract(str): String describing currency pair.
            interval(str): String describing time interval of data.
            limit(int): Number of last candles with data to download
                        (default 100)

        Returns:
            list: List of dictionary items with OHLC format data.
        """
        try:
            pair = self.api_instance.get_currency_pair(contract)
            api_response = self.api_instance.list_candlesticks(
                currency_pair=contract, limit=limit, interval=interval
            )

            logger.info(
                "Exchange data '{}':\n'{}'".format(contract, api_response)
            )
            keys = ["time", "volume", "close", "high", "low", "open"]
            response = []

            for item in api_response:
                dict_item = dict(zip(keys, item))
                dict_item["time"] = datetime.fromtimestamp(
                    int(dict_item["time"])
                ).strftime("%H:%M %d.%m.%y")

                for k, v in dict_item.items():
                    if k != "time":
                        dict_item[k] = float(v)

                response.append(dict_item)

            return response

        except GateApiException as ex:
            logger.error(
                "Gate api exception, label: %s, message: %s\n"
                % (ex.label, ex.message)
            )

        except ApiException as e:
            logger.error(
                "Exception when calling SpotApi->list_candlesticks: %s\n" % e
            )

    def get_candle_stick_time_range(
        self,
        contract: str,
        interval: str,
        start: datetime,
        end: datetime,
        limit: int = 100,
    ) -> list:
        """Download data in candle stick format (ohlc) for crypto pair,
        f.e. BTC_USDT in specific time range.

        Params:
            contract(str): String describing currency pair.
            interval(str): String describing time interval of data.
            start(datetime): Start of time range
            end(datetime): End of time range
            limit(int): Irrelevant. Conflicts with start/end
                (default 100).

        Returns:
            list: List of dictionary items with OHLC format data from
                specified time range.
        """
        try:

            timestamp1 = start.replace(tzinfo=timezone.utc).timestamp()
            timestamp2 = end.replace(tzinfo=timezone.utc).timestamp()
            api_response = self.api_instance.list_candlesticks(
                currency_pair=contract,
                limit=limit,
                _from=int(timestamp1),
                to=int(timestamp2),
                interval=interval,
            )

            logger.info("Exchange data:\n'{}'".format(api_response))
            keys = ["time", "volume", "close", "high", "low", "open"]
            response = []

            for item in api_response:
                dict_item = dict(zip(keys, item))
                dict_item["time"] = datetime.fromtimestamp(
                    int(dict_item["time"])
                ).strftime("%H:%M %d.%m.%y")

                for k, v in dict_item.items():
                    if k != "time":
                        dict_item[k] = float(v)

                response.append(dict_item)

            return response

        except GateApiException as ex:
            logger.error(
                "Gate api exception, label: %s, message: %s\n"
                % (ex.label, ex.message)
            )

        except ApiException as e:
            logger.error(
                "Exception when calling SpotApi->list_candlesticks: %s\n" % e
            )


if __name__ == "__main__":
    api = ExchangeApi()
    api.get_candle_stick(contract="BTC_USDT", interval="1h", limit=10)
