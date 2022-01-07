import time

from agents.informationBroker import InformationBrokerAgent
from agents.user import UserAgent
from agents.brokerDirectory import BrokerDirectoryAgent


def create_agent(agent_cls, jid):
    return agent_cls(jid, "aasd")


if __name__ == "__main__":
    bd_agent = create_agent(BrokerDirectoryAgent, "broker-directory@localhost")
    _ = bd_agent.start()
    rragent = create_agent(InformationBrokerAgent, "information-broker-1@localhost")
    future = rragent.start()
    future.result()  # wait for receiver agent to be prepared.
    useragent = UserAgent("user1@localhost", "aasd")
    useragent.start()

    while rragent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            useragent.stop()
            rragent.stop()
            break
    print("Agents finished")
