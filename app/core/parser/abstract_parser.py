from abc import ABC, abstractmethod


class AbstractParser(ABC):

    @abstractmethod
    def parse(self, tokens):
        pass

    @property
    @abstractmethod
    def is_valid(self):
        pass