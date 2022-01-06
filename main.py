import time

import spade
from agents.informationBroker import InformationBrokerAgent
from agents.user import UserAgent


if __name__ == "__main__":
    rragent = InformationBrokerAgent("request-registry@localhost", "aasd")
    future = rragent.start()
    future.result() # wait for receiver agent to be prepared.
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