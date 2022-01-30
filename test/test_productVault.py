import unittest
import json
from time import sleep

import timeout_decorator

from utils import wait_and_get, create_agent
from src.agents.user import UserAgent
from src.agents.productVault import ProductVaultAgent
from src.agents.informationBroker import InformationBrokerAgent
from src.misc.review import Review, Token


class TestReviewCollector(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = []
        self.product_vault = create_agent(ProductVaultAgent, 'product-vault-0')
        self.information_broker = create_agent(InformationBrokerAgent, 'information-broker-0')
        self.user = create_agent(UserAgent, 'user0')
        self.user1 = create_agent(UserAgent, 'user1')
        self.agents.extend([self.product_vault, self.user, self.user1, self.information_broker])

        for a in self.agents:
            future = a.start()
            future.result()

        self.information_broker.register(str(self.user.jid))
        self.information_broker.register(str(self.user1.jid))
        self.user.set('information_broker_jid', str(self.information_broker.jid))
        self.user.set('product_vault_jid', str(self.product_vault.jid))
        self.user1.set('information_broker_jid', str(self.information_broker.jid))
        self.user1.set('product_vault_jid', str(self.product_vault.jid))

        self.product_data = {'category': 'Pepper', 'comment': 'Black pepper', 'location': 'jp'}

        self.user.set('vault_add_product_data', self.product_data)
        self.user.add_behaviour(UserAgent.VaultAddBehav())

    def tearDown(self) -> None:
        for a in self.agents:
            a.stop()

    @timeout_decorator.timeout(10)
    def test_add_to_vault(self):
        sleep(1)
        offers = self.product_vault.get('offers')

        self.assertEqual(len(offers), 2)
        self.assertEqual(offers[1], self.product_data)

    @timeout_decorator.timeout(10)
    def test_get_vault_categories(self):
        categories = self.product_vault.get('categories')

        self.user.add_behaviour(UserAgent.VaultCategoriesReqBehav())
        user_categories = self.user.get('queue').get(timeout=5)

        self.assertEqual(categories, user_categories)

    @timeout_decorator.timeout(10)
    def test_get_vault_offers(self):
        sleep(1)
        offers = self.product_vault.get('offers')

        self.user.add_behaviour(UserAgent.VaultOffersReqBehav())
        user_offers = self.user.get('queue').get(timeout=5)

        self.assertEqual(len(offers), len(user_offers))
        self.assertEqual(offers[0], user_offers['0'])
        self.assertEqual(offers[1], user_offers['1'])

    @timeout_decorator.timeout(10)
    def test_get_from_vault(self):
        sleep(1)
        self.user1.set('vault_get_product_data', 1)
        self.user1.add_behaviour(UserAgent.VaultGetReqBehav())

        sleep(1)

        offers = self.product_vault.get('offers')
        self.assertEqual(len(offers), 1)


if __name__ == '__main__':
    unittest.main()
