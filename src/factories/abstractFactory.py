from abc import ABC, abstractmethod
from typing import Type

from spade.agent import Agent

from config import DOMAIN, PASSWORD


class AbstractFactory(ABC):
    jid_template: str
    cur_id: int = 0

    @classmethod
    def _generate_jid(cls, id: int) -> str:
        return f'{cls.jid_template}-{id}@{DOMAIN}'

    @classmethod
    def _create_agent(cls, agent_cls: Type[Agent]):
        agent = agent_cls(cls._generate_jid(cls.cur_id), PASSWORD)
        cls.cur_id += 1
        return agent

    @classmethod
    @abstractmethod
    def create_agent(cls):
        pass



