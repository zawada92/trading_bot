import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, PSARIndicator, SMAIndicator
from ta.volatility import AverageTrueRange


class Indicators():
    """Adds technical analysis indicators to pandas DataFrame.
    It uses ta 3rd party module for technical analysis.
    """

    def add_psar(self, df: pd.DataFrame)-> None:
        """Add to DataFrame the Parabolic Stop and reverse indicator.
        
        Params:
            df(pd.DataFrame): Data.
        """
        psar = PSARIndicator(df["high"], df["low"], df["close"], 0.01, 0.20)
        df["psar"] = psar.psar()
        df["psar_up_ind"] = psar.psar_up_indicator()
        df["psar_down_ind"] = psar.psar_down_indicator()

    def add_rsi(self, df: pd.DataFrame)-> None:
        """Add to DataFrame the Relative Strength index indicator.
        
        Params:
            df(pd.DataFrame): Data.
        """
        rsi = RSIIndicator(df["close"])
        df["rsi"] = rsi.rsi()

    def add_sma(self, df: pd.DataFrame, periods: int)-> None:
        """Add to DataFrame the Simple Moving Average indicator.
        
        Params:
            df(pd.DataFrame): Data.
            periods(int): Periods for SMA. Like SMA20, SMA50.
        """
        sma_str = "sma" + str(periods)
        df[sma_str] = SMAIndicator(
                        close=df["close"],
                        window=periods,
                        fillna=True
                        ).sma_indicator()

    def add_ema(self, df: pd.DataFrame, periods: int)-> None:
        """Add to DataFrame the Exponential Moving Average indicator.
        
        Params:
            df(pd.DataFrame): Data.
            periods(int): Periods for EMA. Like EMA20, EMA50.
        """
        ema_str = "ema" + str(periods)
        df[ema_str] = EMAIndicator(
                        close=df["close"],
                        window=periods,
                        fillna=True
                        ).ema_indicator()

    def add_atr(self, df: pd.DataFrame)-> None:
        """Add to DataFrame the Average True Range indicator.
        
        Params:
            df(pd.DataFrame): Data.
        """
        df["atr"] = AverageTrueRange(
                        high=df["high"],
                        low=df["low"],
                        close=df["close"],
                        fillna=True
                        ).average_true_range()

    def is_hammer(self, o: float, h: float, l: float, c: float)-> bool:
        """Indicate if candle with OHLC input values is a hammer.
        Hammer candle is then one which all body is in 0.382 fibonacci
        range of total candle size.
        
        Params:
            o(float): Open value.
            h(float): High value.
            l(float): Low value.
            c(float): Close value.

        Returns:
            bool: True if candle is hammer, False otherwise.
        """
        range = h - l
        fib_barier_low = 0.382 * range + l
        fib_barier_high = h - 0.382 * range

        if o > fib_barier_high and c > fib_barier_high:
            True
        elif o < fib_barier_low and c < fib_barier_low:
            True

        return False

    def find_lowest_near(self, df, i, l, next_no = 5):
        """Find lowest value in number of next candles.
        
        Params:
            df(pd.DataFrame): Data.
            i(int): Index of candle with input lowest value.
            l(float): Input lowest value actually found in area.
            next_no(int): Number of next candles to check.

        Returns:
            tuple: Index and value pair of canlde with lowest low.
        """
        lowsCount = 0
        idx = i
        for index, val in enumerate(df['low'][i:]):
            if val > l:
                lowsCount += 1
            if val <= l:
                l = val
                idx = i + index
                lowsCount = 0
            if lowsCount == next_no:
                break
        return (idx, l)

    def find_highest_near(self, df, i, h):
        """Find highiest value in number of next candles.
        
        Params:
            df(pd.DataFrame): Data.
            i(int): Index of candle with input highiest value.
            l(float): Input highiest value actually found in area.
            next_no(int): Number of next candles to check.

        Returns:
            tuple: Index and value pair of canlde with highiest high.
        """
        highsCount = 0
        idx = i
        for index, val in enumerate(df['high'][i:]):
            if val < h:
                highsCount += 1
            if val >= h:
                h = val
                idx = i + index
                highsCount = 0
            if highsCount == 5:
                break
        return (idx, h)


