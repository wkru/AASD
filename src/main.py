import time
import logging
from typing import Type

from spade.agent import Agent
from agents.informationBroker import InformationBrokerAgent
from agents.user import UserAgent
from agents.brokerDirectory import BrokerDirectoryAgent

from factories.abstractFactory import AbstractFactory
from factories.reviewCollector import ReviewCollectorFactory


agents: list[Agent] = []


def create_agent(agent_cls: Type[Agent], jid: str) -> Agent:
    agent = agent_cls(f'{jid}@localhost', "aasd")
    agents.append(agent)
    return agent


def create_via_factory(factory_cls: Type[AbstractFactory]) -> Agent:
    agent = factory_cls.create_agent()
    agents.append(agent)
    return agent


def main():
    ib_agent = create_agent(InformationBrokerAgent, "information-broker-1")
    create_agent(BrokerDirectoryAgent, "broker-directory")
    create_via_factory(ReviewCollectorFactory)
    create_agent(UserAgent, "user1")

    for a in agents:
        if isinstance(a, InformationBrokerAgent):
            future = a.start()
            future.result()
        else:
            a.start()

    while ib_agent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            for a in agents:
                a.stop()
    print("Agents finished")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
