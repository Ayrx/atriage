from abc import ABC, abstractmethod


class CollectorInterface(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def parse_directory(self, directory):
        pass

    @abstractmethod
    def gather_all_samples(self, directory):
        pass
