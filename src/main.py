import time

from agents.informationBroker import InformationBrokerAgent
from agents.user import UserAgent
from agents.brokerDirectory import BrokerDirectoryAgent
from agents.productVault import ProductVaultAgent


def create_agent(agent_cls, jid):
    return agent_cls(jid, "aasd")


if __name__ == "__main__":
    bd_agent = create_agent(BrokerDirectoryAgent, "broker-directory@localhost")
    _ = bd_agent.start()
    rragent = create_agent(InformationBrokerAgent, "information-broker-1@localhost")
    future = rragent.start()
    future.result()  # wait for receiver agent to be prepared.
    pvagent = create_agent(ProductVaultAgent, "product-vault-1@localhost")
    future = pvagent.start()
    future.result()  # wait for receiver agent to be prepared.
    useragent = UserAgent("user1@localhost", "aasd")
    useragent.start()

    # useragent.add_behaviour(useragent.VaultOffersReqBehav())

    # useragent.add_behaviour(useragent.VaultCategoriesReqBehav())

    # useragent.set("vault_add_product_data", {'category': 2,
    #                                          'comment': 'Black pepper',
    #                                          'location': 'Korytko na parterze'})
    # useragent.add_behaviour(useragent.VaultAddBehav())

    # useragent.set("vault_get_product_data", {'id': 0})
    # useragent.add_behaviour(useragent.VaultGetReqBehav())

    # useragent.add_behaviour(useragent.VaultOffersReqBehav())

    while rragent.is_alive() or pvagent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            useragent.stop()
            rragent.stop()
            pvagent.stop()
            break
    print("Agents finished")
