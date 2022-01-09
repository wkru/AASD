import unittest
import json

import timeout_decorator

import utils
from agents.user import UserAgent
from agents.reviewCollector import ReviewCollectorAgent
from misc.review import Review


def review_setup():
    user0 = 'user0@localhost'
    user1 = 'user1@localhost'
    user2 = 'user2@localhost'
    reviews = {
        user0: [
            Review('love it!', rating=5, request_id=0, from_=user1, to=user0),
            Review('ok', rating=3, request_id=1, from_=user2, to=user0),
            Review('meh', rating=2, request_id=2, from_=user2, to=user0),
        ],
        user1: [
            Review('very good', rating=5, request_id=3, from_=user0, to=user1),
            Review('could be better', rating=1, request_id=4, from_=user2, to=user1),
        ],
        user2: [],
    }
    return user0, user1, user2, reviews


def create_agent(agent_cls, jid):
    return agent_cls(f'{jid}@localhost', 'aasd')


class TestReviewCollector(unittest.TestCase):
    review_collector = None
    user = None
    agents = []

    def setUp(self) -> None:
        self.agents = []
        self.review_collector = create_agent(ReviewCollectorAgent, 'review-collector-0')
        self.user = create_agent(UserAgent, 'user0')
        self.agents.append(self.review_collector)
        self.agents.append(self.user)

        for a in self.agents:
            future = a.start()
            future.result()

        self.user.set(UserAgent.review_collector_key, str(self.review_collector.jid))

    @timeout_decorator.timeout(10)
    def test_leaderboard(self):
        leaderboard = ['a', 'b', 'c']
        self.review_collector.set('leaderboard', leaderboard)
        self.user.add_behaviour(UserAgent.LeaderboardReqBehav())

        msg = utils.wait_and_get(self.user, 'last_received_msg')

        self.assertEqual(json.loads(msg.body), leaderboard)

    @timeout_decorator.timeout(10)
    def test_no_reviews(self):
        *_, user2, reviews = review_setup()

        self.review_collector.set('reviews', reviews)
        self.user.set('target_jid', user2)
        self.user.add_behaviour(UserAgent.ReviewsReqBehav())

        msg = utils.wait_and_get(self.user, 'last_received_msg')

        self.assertEqual(json.loads(msg.body), reviews[user2])

    @timeout_decorator.timeout(10)
    def test_reviews(self):
        user0, *_, reviews = review_setup()

        self.review_collector.set('reviews', reviews)
        self.user.set('target_jid', user0)
        self.user.add_behaviour(UserAgent.ReviewsReqBehav())

        msg = utils.wait_and_get(self.user, 'last_received_msg')
        obj = json.loads(msg.body, object_hook=lambda d: Review(**d))
        self.assertEqual(obj, reviews[user0])

    def tearDown(self) -> None:
        for a in self.agents:
            a.stop()


class TestReviewCollectorInner(unittest.TestCase):
    def test_reviews(self):
        user0, user1, _, reviews = review_setup()
        review_collector = create_agent(ReviewCollectorAgent, 'review-collector-0')
        review_collector.set('reviews', reviews)
        reviews_user1 = review_collector.get_reviews(user1)
        self.assertEqual(reviews_user1, reviews[user1])
        self.assertNotEqual(reviews_user1, reviews[user0])


if __name__ == '__main__':
    unittest.main()
