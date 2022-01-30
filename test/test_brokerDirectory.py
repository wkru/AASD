import unittest
import json
from time import sleep

import timeout_decorator

from utils import wait_and_get, create_agent
from src.misc.location import Location
from src.agents.user import UserAgent
from src.agents.brokerDirectory import BrokerDirectoryAgent
from src.config import SERVICES


class TestBrokerDirectory(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = []
        self.broker_directory = create_agent(BrokerDirectoryAgent, 'broker-directory')
        self.user0 = create_agent(UserAgent, 'user0')
        self.user1 = create_agent(UserAgent, 'user1')
        self.agents.extend([self.broker_directory, self.user0, self.user1])

        for a in self.agents:
            future = a.start()
            future.result()

        self.user0Location = Location(1, 1)
        self.user0.set('location', self.user0Location)
        self.user0.add_behaviour(UserAgent.ServicesReqBehav())

        self.user1Location = Location(99, 99)
        self.user1.set('location', self.user1Location)
        self.user1.add_behaviour(UserAgent.ServicesReqBehav())

    def tearDown(self) -> None:
        for a in self.agents:
            a.stop()

    @timeout_decorator.timeout(10)
    def test_get_services_jids(self):
        sleep(1)

        users_location = [(self.user0, self.user0Location),
                          (self.user1, self.user1Location)]

        for user_location in users_location:
            lengths = [loc[0].distance_to(user_location[1]) for loc in SERVICES]
            index_min = min(range(len(lengths)), key=lengths.__getitem__)
            expected_svcs = SERVICES[index_min][1]

            test_svcs = {}
            svc_names = [('information_broker_jid', 'information-broker'),
                         ('product_vault_jid', 'product-vault'),
                         ('review_collector_jid', 'review-collector')]

            for svc in svc_names:
                test_svcs[svc[1]] = user_location[0].get(svc[0])

            self.assertEqual(expected_svcs, test_svcs)


if __name__ == '__main__':
    unittest.main()
