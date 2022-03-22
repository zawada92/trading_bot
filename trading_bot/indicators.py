import logging

from pandas import DataFrame
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, PSARIndicator, SMAIndicator
from ta.volatility import AverageTrueRange
from typing import Tuple

logger = logging.getLogger(__name__)


class Indicators():
    """Adds technical analysis indicators to pandas DataFrame.
    It uses ta 3rd party module for technical analysis.

    Methods:
    add_psar(self, df: DataFrame):
        Add to DataFrame the Parabolic Stop and reverse indicator.
    add_rsi(df):
        Add to DataFrame the Relative Strength index indicator.
    add_sma(df, periods):
        Add to DataFrame the Simple Moving Average indicator.
    add_ema(df, periods):
        Add to DataFrame the Exponential Moving Average indicator.
    add_atr(df):
        Add to DataFrame the Average True Range indicator.
    find_lowest_near(df, i, l, next_no=5):
        Find lowest value in number of next candles.
    def find_highest_near(df, i, h, next_no=5):
        Find highiest value in number of next candles."""

    def add_psar(self, df: DataFrame)-> None:
        """Add to DataFrame the Parabolic Stop and reverse indicator.
        
        Params:
            df(DataFrame): Data.
        """
        psar = PSARIndicator(df["high"], df["low"], df["close"], 0.01, 0.20)
        df["psar"] = psar.psar()
        df["psar_up_ind"] = psar.psar_up_indicator()
        df["psar_down_ind"] = psar.psar_down_indicator()

    def add_rsi(self, df: DataFrame)-> None:
        """Add to DataFrame the Relative Strength index indicator.
        
        Params:
            df(DataFrame): Data.
        """
        rsi = RSIIndicator(df["close"])
        df["rsi"] = rsi.rsi()

    def add_sma(self, df: DataFrame, periods: int)-> None:
        """Add to DataFrame the Simple Moving Average indicator.
        
        Params:
            df(DataFrame): Data.
            periods(int): Periods for SMA. Like SMA20, SMA50.
        """
        sma_str = "sma" + str(periods)
        df[sma_str] = SMAIndicator(
                        close=df["close"],
                        window=periods,
                        fillna=True
                        ).sma_indicator()

    def add_ema(self, df: DataFrame, periods: int)-> None:
        """Add to DataFrame the Exponential Moving Average indicator.
        
        Params:
            df(DataFrame): Data.
            periods(int): Periods for EMA. Like EMA20, EMA50.
        """
        ema_str = "ema" + str(periods)
        df[ema_str] = EMAIndicator(
                        close=df["close"],
                        window=periods,
                        fillna=True
                        ).ema_indicator()

    def add_atr(self, df: DataFrame)-> None:
        """Add to DataFrame the Average True Range indicator.
        
        Params:
            df(DataFrame): Data.
        """
        if(len(df) > 14): # ATR is calculated from last 14 values.
            df["atr"] = AverageTrueRange(
                        high=df["high"],
                        low=df["low"],
                        close=df["close"],
                        fillna=True
                        ).average_true_range()
        else:
            logger.warning(
                "Failed adding ATR to data which lenght is lower than 14.")

    def find_lowest_near(
        self,
        df: DataFrame,
        i: int,
        l: float,
        next_no: int = 5
    ) -> Tuple[int, float]:
        """Find lowest value in number of next candles.
        
        Params:
            df(DataFrame): Data.
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

    def find_highest_near(
        self,
        df: DataFrame,
        i: int,
        h: float,
        next_no: int = 5
    ) -> Tuple[int, float]:
        """Find highiest value in number of next candles.
        
        Params:
            df(DataFrame): Data.
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
            if highsCount == next_no:
                break
        return (idx, h)


