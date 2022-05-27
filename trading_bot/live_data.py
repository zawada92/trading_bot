import logging

from pandas import DataFrame

logger = logging.getLogger(__name__)


class LiveData:
    """Stores real time downloaded data in DataFrame format"""

    def __init__(self) -> None:
        #TODO add other data about downloaded data
        self.df = DataFrame()

