import unittest

import timeout_decorator

from utils import create_agent, wait_and_get
from src.agents.reviewCollector import ReviewCollectorAgent
from src.agents.informationBroker import InformationBrokerAgent
from src.agents.user import UserAgent
from misc.review import ReviewToken


class TestInformationBroker(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = []
        self.information_broker = create_agent(InformationBrokerAgent, 'information_broker-0')
        self.review_collector = create_agent(ReviewCollectorAgent, 'review-collector-0')
        self.user = create_agent(UserAgent, 'user')
        self.agents.extend([self.information_broker, self.review_collector, self.user])

        for a in self.agents:
            future = a.start()
            future.result()

    def tearDown(self) -> None:
        for a in self.agents:
            a.stop()

    @timeout_decorator.timeout(10)
    def test_issuing_review_tokens(self):
        self.information_broker.set('requests', [])
        self.information_broker.set('tokens_to_issue', [{'from_': 'user0', 'to': 'user1', 'request_id': 0}])
        self.information_broker.add_behaviour(InformationBrokerAgent.ReviewTokenCreationReqBehav())

        tokens = wait_and_get(self.review_collector, 'tokens', value_to_check={})

        self.assertEqual(tokens, {0: ReviewToken(0, ['user0', 'user1'])})


if __name__ == '__main__':
    unittest.main()
