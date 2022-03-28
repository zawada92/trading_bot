import logging

from enum import Enum
from pandas import DataFrame
from strategy import Strategy

logger = logging.getLogger(__name__)


class EmaPlacement(Enum):
    """Defines for description of EMA line placement on the chart
    in relation to candles."""

    CROSSED, ABOVE, BELOW = range(0,3)


class StrategyHammer (Strategy):
    """Hammer strategy API.
    C - 38.2 candle with wick crossing EMA20
    E - Entry is that candle close or close to this value
    S - If ATR is above 100 then 50 pips below entry.
        Otherwise 20 pips below.
    T - If ATR is above 100 then 50 pips above entry.
        Otherwise 20 pips above.
        
    Attributes:
        df(DataFrame): Exchange data.
        entry(float): Order entry value.
        stop_loss(float): Order stop loss value.
        target(float): Order target profit value.
        market_order(bool): If order entry is market order.
        _pips(int): Number of pips to calculate order details.

    Methods:
    start():
        Starts strategy setup.
    _is_condition_met():
        Check if strategy conditions are met.
    _set_entry():
        Sets entry value in strategy setup.
    _set_stop_loss():
        Sets stop loss value in strategy setup.
    _set_target():
        Sets target profit value in strategy setup.
    get_entry():
        Gets entry value in strategy setup.
    get_stop_loss():
        Gets stop loss value in strategy setup.
    get_target():
        Gets target profit value in strategy setup.
    is_setup_ready():
        Check if strategy setup is ready. We have our CEST.
    """

    def __init__(
        self,
        df: DataFrame,
        tail_len: int = 6,
        market_order: bool = False
    ) -> None:
        """Params:
            df(DataFrame): Exchange data.
            tail_len(int): Number of last candles to check if EMA is 
                above/below(default 6)
            market_order(bool): If order entry is market order
                (default False)"""
        super().__init__(df)
        self.market_order = market_order
        self.tail_len = tail_len
        self._pips = 0 # used to calculate stop loss and target 
        # TODO improve pips implementation.

    def start(self) -> None:
        """Starts hammer strategy setup."""
        super().start()

    def _is_hammer(self, o: float, h: float, l: float, c: float)-> bool:
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
            return True
        if (o < fib_barier_low) and (c < fib_barier_low):
            return True

        return False

    def _check_cdl_vs_ema(self) -> int:
        """Checks last candles placement compared to EMA value.
        If candles are above or below EMA.
        
        Returns:
            int: EmaPlacement ABOVE or BELOW.
        """
        above = True
        below = True
        lows = self.df['low'][-self.tail_len:]
        highs = self.df['high'][-self.tail_len:]
        emas = self.df['ema20'][-self.tail_len:]
        for l, h, ema in zip(lows, highs, emas):
            if l < ema:
                above = False
            if h > ema:
                below = False

        if above:
            return EmaPlacement.ABOVE
        if below:
            return EmaPlacement.BELOW
        return EmaPlacement.CROSSED

    def _is_condition_met(self) -> bool:
        """Check if strategy conditions are met.
        
        Returns:
            bool: True if conditions met. False otherwise.
        """
        trend = self._check_cdl_vs_ema()
        trend = EmaPlacement.BELOW
        if(trend != EmaPlacement.CROSSED):
            #TODO find our target candle which we are checking. Make it a dict.
            l = self.df['low'].iloc[-2]
            h = self.df['high'].iloc[-2]
            c = self.df['close'].iloc[-2]
            o = self.df['open'].iloc[-2]
            atr = self.df['atr'].iloc[-2]
            ema20 = self.df['ema20'].iloc[-2]
            hammer = self._is_hammer(o, h, l, c)
            if atr > 100:
                self._pips = 50
            else:
                self._pips = 20

            if hammer and atr < 3000:
                if trend == EmaPlacement.ABOVE:
                    if l < ema20:
                        return True
                if trend == EmaPlacement.BELOW:
                    if h > ema20:
                        return True

        return False

    def _set_entry(self):
        """Sets entry value in strategy setup."""
        # TODO rethink if entry is market value at the time of processing.
        if (self.market_order):
            # TODO proceed to market order creation...
            # self.entry = create_market_order()
            pass
        else:
            self.entry = self.df["close"].iloc[-2]

    def _set_stop_loss(self):
        """Sets stop loss value in strategy setup."""
        self.stop_loss = self.entry - self._pips

    def _set_target(self):
        """Sets target profit value in strategy setup."""
        self.target = self.entry + self._pips

