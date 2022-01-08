import time

from agents.informationBroker import InformationBrokerAgent
from agents.user import UserAgent
from agents.brokerDirectory import BrokerDirectoryAgent

from agents.productVault import ProductVaultAgent
from messages import productVaultServices, requestManagement

from utils import Location

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
    useragent1 = UserAgent("user1@localhost", "aasd")
    useragent1.start()
    useragent2 = UserAgent("user2@localhost", "aasd")
    useragent2.start()

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

    while rragent.is_alive() or pvagent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            useragent1.stop()
            useragent2.stop()
            rragent.stop()
            pvagent.stop()
            bd_agent.stop()
            break
    print("Agents finished")
