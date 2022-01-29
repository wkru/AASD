import unittest
from time import sleep

from spade.behaviour import OneShotBehaviour
import timeout_decorator

from utils import create_agent, wait_and_get
from src.agents.reviewCollector import ReviewCollectorAgent
from src.agents.informationBroker import InformationBrokerAgent
from src.agents.user import UserAgent


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

        self.information_broker.register(str(self.user0.jid))
        self.information_broker.register(str(self.user1.jid))
        self.user0.set('information_broker_jid', str(self.information_broker.jid))
        self.user0.set('review_collector', str(self.review_collector.jid))
        self.user1.set('information_broker_jid', str(self.information_broker.jid))
        self.user1.set('review_collector', str(self.review_collector.jid))
        self.information_broker.set('review_collector', str(self.review_collector.jid))

        self.user0.set('new_request', {'category': 'salt', 'comment': 'some comment'})
        self.user0.add_behaviour(UserAgent.AddRequestBehav())
        requests = wait_and_get(self.information_broker, 'requests', value_to_check=[])
        request_id = requests[0]['id']
        self.user1.set("request_to_accept", request_id)
        self.user1.add_behaviour(UserAgent.AcceptBehav())

    def tearDown(self) -> None:
        for a in self.agents:
            a.stop()

    def get_send_behav_for(self, msg):
        class SendBehaviour(OneShotBehaviour):
            def run(self):
                print("Sending message: {}".format(msg))
                self.send(msg)
        return SendBehaviour()

    @timeout_decorator.timeout(10)
    def test_issuing_review_tokens(self):
        tokens = wait_and_get(self.review_collector, 'tokens', value_to_check={})
        self.assertTrue(len(tokens) == 1)

    @timeout_decorator.timeout(10)
    def test_users_get_review_tokens(self):
        user0_tokens = wait_and_get(self.user0, 'review_tokens', value_to_check={})
        user1_tokens = wait_and_get(self.user0, 'review_tokens', value_to_check={})

        self.assertTrue(len(user0_tokens) == 1)
        self.assertTrue(len(user1_tokens) == 1)


if __name__ == '__main__':
    unittest.main()
