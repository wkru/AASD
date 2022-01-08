import logging
from dataclasses import dataclass

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, PeriodicBehaviour
from spade.template import Template

from messages import reviewManagement


@dataclass
class ReviewToken:
    hash_: int
    timestamp: int


@dataclass
class Review:
    token: ReviewToken
    contents: str
    rating: int
    request_id: int


class ReviewCollectorAgent(Agent):
    def init(self):
        self.valid_tokens = []

        self.set('reviews', [])
        self.set('leaderboard', [])

    def __repr__(self):
        return str(self.__class__.__name__)

    def update_leaderboard(self) -> None:
        # todo
        pass

    def clear_unused_tokens(self) -> None:
        # drop tokens older than 2 weeks
        # todo
        pass

    async def setup(self):
        self.init()
        print(f'{repr(self)} started')

        review_creation_b = self.ReviewCreationBehav()
        self.add_behaviour(
            review_creation_b,
            Template(metadata={'performative': 'request'}),
        )
        leaderboard_b = self.LeaderboardBehav()

        # metadata = {'performative': 'request', 'protocol': 'review-collector-leaderboard'}
        t = Template()
        t.set_metadata('performative', 'request')
        t.set_metadata('protocol', 'review-collector-leaderboard')
        self.add_behaviour(
            leaderboard_b,
            t
        )
        review_tokens_creation_b = self.ReviewTokensCreationBehav()
        self.add_behaviour(
            review_tokens_creation_b,
            Template(metadata={'performative': 'request'})
        )
        users_reviews_b = self.UserReviewsBehav()
        self.add_behaviour(
            users_reviews_b,
            Template(metadata={'performative': 'request'})
        )

    class ReviewCreationBehav(CyclicBehaviour):
        def __init__(self):
            super().__init__()

        async def run(self) -> None:
            # todo
            pass

    # class SendTokenExpiredInfoBehav(OneShotBehaviour):
    #     async def run(self) -> None:
    #         # todo
    #         pass

    class LeaderboardBehav(CyclicBehaviour):
        async def run(self) -> None:
            logging.info(f'{repr(self)} started')
            if (msg := await self.receive(timeout=1000)) is not None:
                logging.info(f'Message received: {msg.body}')
                resp = reviewManagement.LeaderboardResponse(to=str(msg.sender), data=self.agent.get('leaderboard'))
                await self.send(resp)

    class ReviewTokensCreationBehav(CyclicBehaviour):
        async def run(self) -> None:
            # todo
            pass

    class UserReviewsBehav(CyclicBehaviour):
        async def run(self) -> None:
            # todo
            pass
