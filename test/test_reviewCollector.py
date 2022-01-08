import unittest
import json

from factories.reviewCollector import ReviewCollectorFactory
from agents.user import UserAgent
from messages.reviewManagement import LeaderboardResponse
import utils


class TestReviewCollector(unittest.TestCase):
    review_collector = None
    user0 = None
    agents = []

    def setUp(self) -> None:
        def _create_agent(agent_cls, jid):
            return agent_cls(f'{jid}@localhost', 'aasd')

        self.user0 = _create_agent(UserAgent, 'user0')
        self.review_collector = ReviewCollectorFactory.create_agent()
        self.agents.append(self.user0)
        self.agents.append(self.review_collector)

        for a in self.agents:
            future = a.start()
            future.result()

    def test_leaderboard(self):
        leaderboard = ['a', 'b', 'c']
        self.review_collector.set('leaderboard', leaderboard)
        self.user0.add_behaviour(UserAgent.LeaderboardReqBehav())

        msg = utils.wait_and_get(self.user0, 'last_received_msg')

        self.assertEqual(json.loads(msg.body), leaderboard)

    def tearDown(self) -> None:
        for a in self.agents:
            a.stop()


if __name__ == '__main__':
    unittest.main()
