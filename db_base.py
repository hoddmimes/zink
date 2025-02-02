from abc import ABC, abstractmethod

class db_base(ABC):

    def save(self, application, tag, data):
        pass

    def find(self, application, tag, before, after, limit):
        pass

