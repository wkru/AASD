from time import sleep

from spade.agent import Agent


def wait_and_get(agent: Agent, key: str, value_to_check=None):
    while True:
        obj = agent.get(key)
        if obj is not None and (value_to_check is None or obj != value_to_check):
            break
        sleep(0.001)
    return obj


def create_agent(agent_cls, jid):
    return agent_cls(f'{jid}@localhost', 'aasd')
