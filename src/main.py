import time
from typing import Type
import logging
import sys

from spade.agent import Agent

from src.agents.informationBroker import InformationBrokerAgent
from src.agents.user import UserAgent
from src.agents.brokerDirectory import BrokerDirectoryAgent
from src.agents.reviewCollector import ReviewCollectorAgent

from src.agents.productVault import ProductVaultAgent

from src import ui

agents: list[Agent] = []


def create_agent(agent_cls: Type[Agent], jid: str) -> Agent:
    agent = agent_cls(f'{jid}@localhost', "aasd")
    agents.append(agent)
    return agent


def main(run_ui: bool = False):
    if not run_ui:
        bd_agent = create_agent(BrokerDirectoryAgent, "broker-directory")
        rragent = create_agent(InformationBrokerAgent, "information-broker-1")
        pvagent = create_agent(ProductVaultAgent, "product-vault-1")
        rcagent = create_agent(ReviewCollectorAgent, 'review-collector-1')
        rragent2 = create_agent(InformationBrokerAgent, "information-broker-2")
        pvagent2 = create_agent(ProductVaultAgent, "product-vault-2")
        rcagent2 = create_agent(ReviewCollectorAgent, 'review-collector-2')
        # useragent1 = create_agent(UserAgent, "user1")
        # useragent2 = create_agent(UserAgent, "user2")


        for a in agents:
            future = a.start()
            future.result()

        rragent.set(InformationBrokerAgent.review_collector_key, 'review-collector-1@localhost')
        rragent2.set(InformationBrokerAgent.review_collector_key, 'review-collector-2@localhost')

    # useragent1.set('location', Location(1, 1))
    # useragent1.add_behaviour(UserAgent.ServicesReqBehav())

    # useragent1.set('information_broker_jid', 'information-broker-1@localhost')
    # useragent1.add_behaviour(UserAgent.Register())
    # useragent2.set('information_broker_jid', 'information-broker-1@localhost')
    # useragent2.add_behaviour(UserAgent.Register())
    #
    # useragent1.set('information_broker_jid', 'information-broker-1@localhost')
    # useragent1.add_behaviour(UserAgent.Deregister())
    # useragent2.set('information_broker_jid', 'information-broker-1@localhost')
    # useragent2.add_behaviour(UserAgent.Deregister())

    # get request list test
    # useragent1.add_behaviour(useragent1.AskForRequestsBehav())

    # add request test
    # useragent1.set("new_request", {'category': 'book', 'comment': 'The Lord of the Rings'})
    # useragent1.add_behaviour(useragent1.AddRequestBehav())

    # accept request test
    # print(rragent.get("requests"))
    # useragent2.set("request_to_accept", 1)
    # useragent2.add_behaviour(useragent2.AcceptBehav())

    # cancel request test
    # useragent2.set("request_to_cancel", "f9a4be60598dac4d8c28157c2a342cff4e3caed484fc27bab97be2790d75caa5")
    # useragent2.add_behaviour(useragent1.CancelBehav())

    # get categories from information broker
    # useragent1.set('information_broker_jid', 'information-broker-1@localhost')
    # useragent1.add_behaviour(useragent1.CategoriesReqBehav())

    # #
    # useragent1 = UserAgent("user1@localhost", "aasd")
    # useragent1.start()
    #
    # useragent1.add_behaviour(useragent1.VaultOffersReqBehav())
    #
    # useragent1.add_behaviour(useragent1.VaultCategoriesReqBehav())

    # useragent1.set("vault_add_product_data", {'category': 1,
    #                                          'comment': 'Black pepper',
    #                                          'location': 'Korytko na parterze'})
    # useragent1.add_behaviour(useragent1.VaultAddBehav())
    #
    # useragent1.set("vault_get_product_data", {'id': 0})
    # useragent1.add_behaviour(useragent1.VaultGetReqBehav())
    #
    # useragent1.add_behaviour(useragent1.VaultOffersReqBehav())

    if run_ui:
        ui.run()

    if not run_ui:
        while rragent.is_alive() or pvagent.is_alive():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                for a in agents:
                    a.stop()
                break
        logging.info("Agents finished")


if __name__ == "__main__":
    run_ui = len(sys.argv) > 1
    logging_level = logging.ERROR if run_ui else logging.INFO
    logging.basicConfig(level=logging_level)
    main(run_ui=run_ui)
