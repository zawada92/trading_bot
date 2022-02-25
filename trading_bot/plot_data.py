import logging
import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots


logger = logging.getLogger(__name__)

class PlotData():
    """Visualization class using plotly express."""

    def __init__(self) -> None:
        pass

    @classmethod
    def plot_ohlc(self, df: pd.DataFrame, contract: str) -> None:
        """Plot OHLC data.
        
        Params:
            df(pd.DataFrame): Data.
        """
        fig = make_subplots(rows=1, cols=1)

        fig.add_trace(
            go.Candlestick(
                x=df['time'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='coin'),
            row=1,
            col=1)

        fig.update_layout(
        title = {
            'text': contract,
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        font = dict(
            family = "Courier New, monospace",
            size = 20,
            color = "#7f7f7f")
        )

        logger.info("Plot OHLC data. Pair: %s", contract)
        fig.show()

