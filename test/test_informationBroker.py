import unittest
from time import sleep

import timeout_decorator

from utils import create_agent, wait_and_get
from src.agents.reviewCollector import ReviewCollectorAgent
from src.agents.informationBroker import InformationBrokerAgent
from src.agents.user import UserAgent
from src.misc.review import Token


class TestInformationBroker(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = []
        self.information_broker = create_agent(InformationBrokerAgent, 'information_broker-0')
        self.review_collector = create_agent(ReviewCollectorAgent, 'review-collector-0')
        self.user0 = create_agent(UserAgent, 'user0')
        self.user1 = create_agent(UserAgent, 'user1')
        self.agents.extend([self.information_broker, self.review_collector, self.user0, self.user1])

        for a in self.agents:
            future = a.start()
            future.result()

    def tearDown(self) -> None:
        for a in self.agents:
            a.stop()

    # @timeout_decorator.timeout(10)
    # def test_issuing_review_tokens(self):
    #     self.information_broker.set('requests', [])
    #     self.information_broker.set('tokens_to_issue', [{'from_': 'user0', 'to': 'user1', 'request_id': 0}])
    #     self.information_broker.add_behaviour(InformationBrokerAgent.ReviewTokenCreationReqBehav())
    #
    #     tokens = wait_and_get(self.review_collector, 'tokens', value_to_check={})
    #
    #     self.assertEqual(tokens, {0: Token(0, ['user0', 'user1'])})

    # @timeout_decorator.timeout(10)
    # def test_information_broker_drops_issued_tokens(self):
    #     to_issue = [{'from_': 'user0', 'to': 'user1', 'request_id': 0}]
    #     self.information_broker.set('tokens_to_issue', to_issue)
    #     self.information_broker.add_behaviour(InformationBrokerAgent.ReviewTokenCreationReqBehav())
    #
    #     sleep(0.01)
    #     tokens = self.information_broker.get('tokens_to_issue')
    #
    #     self.assertEqual(tokens, [])

    # @timeout_decorator.timeout(10)
    # def test_users_get_review_tokens(self):
    #     self.assertEqual(self.user0.get('review_tokens'), {})
    #     self.assertEqual(self.user1.get('review_tokens'), {})
    #
    #     self.information_broker.set('tokens_to_issue', [{'from_': str(self.user0.jid), 'to': str(self.user1.jid), 'request_id': 0}])
    #     self.information_broker.add_behaviour(InformationBrokerAgent.ReviewTokenCreationReqBehav())
    #
    #     user0_tokens = wait_and_get(self.user0, 'review_tokens', value_to_check={})
    #     user1_tokens = wait_and_get(self.user0, 'review_tokens', value_to_check={})
    #
    #     self.assertEqual(user0_tokens, {0: Token(0, ['user0@localhost', 'user1@localhost'])})
    #     self.assertEqual(user1_tokens, {0: Token(0, ['user0@localhost', 'user1@localhost'])})


if __name__ == '__main__':
    unittest.main()
