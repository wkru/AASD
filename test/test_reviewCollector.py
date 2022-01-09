import unittest
import json
from time import sleep

import timeout_decorator

from utils import wait_and_get, create_agent
from src.agents.user import UserAgent
from src.agents.reviewCollector import ReviewCollectorAgent
from src.agents.informationBroker import InformationBrokerAgent
from src.misc.review import Review, Token


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


class TestReviewCollector(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = []
        self.review_collector = create_agent(ReviewCollectorAgent, 'review-collector-0')
        self.information_broker = create_agent(InformationBrokerAgent, 'information-broker-0')
        self.user = create_agent(UserAgent, 'user0')
        self.agents.extend([self.review_collector, self.user, self.information_broker])

        for a in self.agents:
            future = a.start()
            future.result()

        self.user.set(UserAgent.review_collector_key, str(self.review_collector.jid))

    def tearDown(self) -> None:
        for a in self.agents:
            a.stop()

    @timeout_decorator.timeout(10)
    def test_leaderboard(self):
        leaderboard = ['a', 'b', 'c']
        self.review_collector.set('leaderboard', leaderboard)
        self.user.add_behaviour(UserAgent.LeaderboardReqBehav())

        msg = wait_and_get(self.user, 'last_received_msg')

        self.assertEqual(json.loads(msg.body), leaderboard)

    @timeout_decorator.timeout(10)
    def test_leaderboard_calculated_correctly(self):
        review1 = Review('1', rating=1, request_id=0, from_='a', to='b')
        review2 = Review('1', rating=2, request_id=0, from_='a', to='b')
        review5 = Review('1', rating=5, request_id=0, from_='a', to='b')
        reviews = {
            'user1': [review5, review1],
            'user2': [review1, review2],
            'user3': [review1] * 2,
            'user0': [review5] * 3,
        }
        self.review_collector.set('reviews', reviews)
        self.review_collector.update_leaderboard()
        self.user.add_behaviour(UserAgent.LeaderboardReqBehav())

        msg = wait_and_get(self.user, 'last_received_msg')

        self.assertEqual(json.loads(msg.body), ['user0', 'user1', 'user2', 'user3'])

    @timeout_decorator.timeout(10)
    def test_no_reviews(self):
        *_, user2, reviews = review_setup()

        self.review_collector.set('reviews', reviews)
        self.user.set('target_jid', user2)
        self.user.add_behaviour(UserAgent.ReviewsReqBehav())

        msg = wait_and_get(self.user, 'last_received_msg')

        self.assertEqual(json.loads(msg.body), reviews[user2])

    def test_reviews_inner(self):
        user0, user1, _, reviews = review_setup()
        review_collector = create_agent(ReviewCollectorAgent, 'review-collector-0')
        review_collector.set('reviews', reviews)
        reviews_user1 = review_collector.get_reviews(user1)
        self.assertEqual(reviews_user1, reviews[user1])
        self.assertNotEqual(reviews_user1, reviews[user0])

    @timeout_decorator.timeout(10)
    def test_reviews(self):
        user0, *_, reviews = review_setup()

        self.review_collector.set('reviews', reviews)
        self.user.set('target_jid', user0)
        self.user.add_behaviour(UserAgent.ReviewsReqBehav())

        msg = wait_and_get(self.user, 'last_received_msg')
        obj = json.loads(msg.body, object_hook=lambda d: Review(**d))
        self.assertEqual(obj, reviews[user0])

    @timeout_decorator.timeout(10)
    def test_first_create_review(self):
        user0, user1, *_ = review_setup()
        self.assertEqual(self.review_collector.get('reviews'), {})
        self.review_collector.create_review(
            contents='test', rating=5, request_id=0, from_=user1, to=user0
        )

        self.assertEqual(self.review_collector.get('reviews'), {
            user0: [Review('test', rating=5, request_id=0, from_=user1, to=user0)]
        })

    @timeout_decorator.timeout(10)
    def test_create_review(self):
        user0, *_, user2, reviews = review_setup()
        self.review_collector.set('reviews', reviews)

        self.assertEqual(len(self.review_collector.get_reviews(user0)), 3)
        self.review_collector.create_review(
            contents='testtest', rating=5, request_id=0, from_=user2, to=user0
        )

        self.assertEqual(len(self.review_collector.get_reviews(user0)), 4)
        self.assertEqual(self.review_collector.get_reviews(user0)[3].contents, 'testtest')

    @timeout_decorator.timeout(10)
    def test_review_creation(self):
        user0,  user1, *_, reviews = review_setup()
        self.review_collector.set('reviews', reviews)
        old_reviews = self.review_collector.get_reviews(user1)

        kwargs = {
            'contents': 'test', 'rating': 5, 'request_id': 1, 'from_': user0, 'to': user1
        }
        token = Token(request_id=1, from_=user0, to=user1)
        self.user.set('kwargs', kwargs)
        self.user.set('review_tokens', {1: token})
        self.review_collector.set('tokens', {1: token})
        self.user.add_behaviour(UserAgent.ReviewCreationReqBehav())

        new_review = Review(**kwargs)

        sleep(0.01)

        self.assertEqual(self.review_collector.get('reviews')[user1], old_reviews + [new_review])

    @timeout_decorator.timeout(10)
    def test_invalid_token(self):
        user0,  user1, *_ = review_setup()
        kwargs = {
            'contents': 'test', 'rating': 5, 'request_id': 1, 'from_': user0, 'to': user1
        }
        token = Token(request_id=10, from_=user0, to=user1)
        self.user.set('kwargs', kwargs)
        self.user.set('review_tokens', {1: token})
        self.user.add_behaviour(UserAgent.ReviewCreationReqBehav())

        sleep(0.01)

        self.assertEqual(self.review_collector.get('reviews'), {})

    # @timeout_decorator.timeout(10)
    # def test_token_is_burnt_after_review(self):
    #     user0,  user1, *_ = review_setup()
    #
    #     self.assertEqual(self.user.get('review_tokens'), {})
    #
    #     self.information_broker.set('tokens_to_issue', [{'from_': user0, 'to': user1, 'request_id': 0}])
    #     self.information_broker.add_behaviour(InformationBrokerAgent.ReviewTokenCreationReqBehav())
    #
    #     self.assertNotEqual(wait_and_get(self.user, 'review_tokens', value_to_check={}), {})
    #     self.assertNotEqual(wait_and_get(self.review_collector, 'tokens', value_to_check={}), {})
    #
    #     kwargs = {
    #         'contents': 'test', 'rating': 5, 'request_id': 0, 'from_': user0, 'to': user1
    #     }
    #     self.user.set('kwargs', kwargs)
    #     self.user.add_behaviour(UserAgent.ReviewCreationReqBehav())
    #
    #     sleep(0.01)
    #
    #     self.assertEqual(self.user.get('review_tokens'), {})
    #     self.assertEqual(self.review_collector.get('tokens'), {})


if __name__ == '__main__':
    unittest.main()
