from time import sleep

from spade.agent import Agent


def wait_and_get(agent: Agent, key: str):
    while (obj := agent.get(key)) is None:
        sleep(0.001)
    return obj
