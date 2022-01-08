from abc import ABC, abstractmethod
from typing import Type

from spade.agent import Agent

from config import DOMAIN, PASSWORD


class AbstractFactory(ABC):
    jid_template: str
    agents: list[Agent]

    @classmethod
    def _get_new_id(cls) -> int:
        return len(cls.agents)

    @classmethod
    def _generate_new_jid(cls) -> str:
        return f'{cls.jid_template}-{cls._get_new_id()}@{DOMAIN}'

    @classmethod
    def _create_agent(cls, agent_cls: Type[Agent]):
        new_agent: agent_cls = agent_cls(cls._generate_new_jid(), PASSWORD)
        cls.agents.append(new_agent)
        return new_agent

    @classmethod
    @abstractmethod
    def create_agent(cls):
        pass



