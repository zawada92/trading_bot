import logging
import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots


logger = logging.getLogger(__name__)


class PlotData:
    """Visualization class using plotly express.

    Methods:
    plot_ohlc(df, Contract):
        Plot OHLC data."""

    def __init__(self) -> None:
        pass

    @classmethod
    def plot_ohlc(
        self, df: pd.DataFrame, contract: str, ema20: bool = False
    ) -> None:
        """Plot OHLC data.

        Params:
            df(pd.DataFrame): Data.
            contract(str): Currency pair contract.
            ema20(bool): If EMA20 should be shown on screen
                (default False)"""
        fig = make_subplots(rows=1, cols=1)

        fig.add_trace(
            go.Candlestick(
                x=df["time"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="coin",
            ),
            row=1,
            col=1,
        )

        if ema20:
            fig.add_trace(
                go.Scatter(
                    x=df["time"],
                    y=df["ema20"],
                    name="ema20",
                    mode="lines",
                    marker=dict(color="black", size=4),
                ),
                row=1,
                col=1,
            )

        fig.update_layout(
            title={
                "text": contract,
                "y": 0.9,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            font=dict(
                family="Courier New, monospace", size=20, color="#7f7f7f"
            ),
        )

        logger.info("Plot OHLC data. Pair: %s", contract)
        fig.show()
