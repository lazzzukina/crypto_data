from abc import ABC
from abc import abstractmethod


class ExchangeStrategy(ABC):
    @abstractmethod
    def connect(self, pairs):
        pass

    @abstractmethod
    def subscribe(self, ws, pairs):
        pass

    @abstractmethod
    def process_message(self, ws, message):
        pass
