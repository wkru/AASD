import json

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, PeriodicBehaviour
from spade.template import Template

from messages import reviewManagement
from misc.review import Review


class ReviewCollectorAgent(Agent):
    def init(self):
        self.tokens = []

        if self.get('reviews') is None:
            self.set('reviews', {})
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
        print(f'{repr(self)} started')
        self.init()

        review_creation_b = self.ReviewCreationBehav()
        self.add_behaviour(
            review_creation_b,
            Template(metadata={'performative': 'request'}),
        )

        leaderboard_b = self.LeaderboardBehav()
        self.add_behaviour(
            leaderboard_b,
            Template(metadata=reviewManagement.Leaderboard.metadata),
        )

        review_tokens_creation_b = self.ReviewTokensCreationBehav()
        self.add_behaviour(
            review_tokens_creation_b,
            Template(metadata={'performative': 'request'})
        )

        users_reviews_b = self.UserReviewsBehav()
        self.add_behaviour(
            users_reviews_b,
            Template(metadata=reviewManagement.Reviews.metadata)
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
            print(f'{repr(self)} started')
            if (msg := await self.receive(timeout=1000)) is not None:
                print(f'Message received: {msg.body}')
                resp = reviewManagement.LeaderboardResponse(to=str(msg.sender), data=self.agent.get('leaderboard'))
                await self.send(resp)

    class ReviewTokensCreationBehav(CyclicBehaviour):
        async def run(self) -> None:
            # todo
            pass

    def get_reviews(self, jid: str) -> list[Review]:
        return self.get('reviews').get(jid, [])

    class UserReviewsBehav(CyclicBehaviour):
        async def run(self) -> None:
            print(f'{repr(self)} started')
            if (msg := await self.receive(timeout=1000)) is not None:
                print(f'Message received: {msg.body}')
                target_jid = json.loads(msg.body)
                resp = reviewManagement.ReviewsResponse(to=str(msg.sender), data=self.agent.get_reviews(target_jid))
                await self.send(resp)
