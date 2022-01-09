from abc import ABC, abstractmethod
from typing import Type

from spade.agent import Agent

from src.config import DOMAIN, PASSWORD


class AbstractFactory(ABC):
    jid_template: str

    def __init__(self):
        self.cur_id: int = 0

    def _generate_jid(self, id: int) -> str:
        return f'{self.jid_template}-{id}@{DOMAIN}'

    def _create_agent(self, agent_cls: Type[Agent]):
        agent = agent_cls(self._generate_jid(self.cur_id), PASSWORD)
        self.cur_id += 1
        return agent

    @abstractmethod
    def create_agent(self):
        pass



