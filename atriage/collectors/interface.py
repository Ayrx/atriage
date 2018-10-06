from abc import ABC, abstractmethod


class CollectorInterface(ABC):

    @abstractmethod
    def parse_directory(self, directory):
        pass

    @abstractmethod
    def gather_all_samples(self, directory):
        pass
