import json

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, PeriodicBehaviour
from spade.template import Template

from src.messages import reviewManagement
from src.misc.review import Review, ReviewToken


class ReviewCollectorAgent(Agent):
    def init(self):
        # request_id -> token
        self.set('tokens', {})

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

        leaderboard_b = self.LeaderboardBehav()
        self.add_behaviour(
            leaderboard_b,
            Template(metadata=reviewManagement.Leaderboard.metadata),
        )

        # review_tokens_creation_b = self.ReviewTokensCreationBehav()
        # self.add_behaviour(
        #     review_tokens_creation_b,
        #     Template(metadata={'performative': 'request'})
        # )

        users_reviews_b = self.UserReviewsBehav()
        self.add_behaviour(
            users_reviews_b,
            Template(metadata=reviewManagement.Reviews.metadata)
        )

        review_creation_b = self.ReviewCreationBehav()
        self.add_behaviour(
            review_creation_b,
            Template(metadata=reviewManagement.ReviewCreation.metadata)
        )

        review_token_creation_b = self.ReviewTokenCreationBehav()
        self.add_behaviour(
            review_token_creation_b,
            Template(metadata=reviewManagement.ReviewTokenCreation.metadata)
        )

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

    def create_review(self, contents: str, rating: int, request_id: int, from_: str, to: str) -> None:
        new_review = Review(contents, rating, request_id, from_, to)
        reviews = self.get('reviews')
        reviews[to] = reviews.get(to, []) + [new_review]
        self.set('reviews', reviews)

    class ReviewCreationBehav(CyclicBehaviour):
        async def run(self) -> None:
            print(f'{repr(self)} started')
            if (msg := await self.receive(timeout=1000)) is not None:
                print(f'Message received: {msg.body}')
                kwargs = json.loads(msg.body)
                if {'contents', 'rating', 'request_id', 'from_', 'to'}.issubset(kwargs.keys()):
                    self.agent.create_review(**kwargs)
                    print(f'Review created: {kwargs}')
                else:
                    print(f'Review creation failed: {kwargs}')

    class ReviewTokenCreationBehav(CyclicBehaviour):
        async def send_tokens(self, token: ReviewToken, jids: list[str]) -> None:
            for jid in jids:
                msg = reviewManagement.ReviewToken(to=jid, token=token)
                await self.send(msg)

        async def run(self) -> None:
            print(f'{repr(self)} started')
            if (msg := await self.receive(timeout=1000)) is not None:
                print(f'Message received: {msg.body}')

                token_data = json.loads(msg.body)
                request_id = token_data.get('request_id')
                user_ids = token_data.get('user_ids')

                token = ReviewToken(request_id, user_ids)

                tokens = self.get('tokens')
                if tokens.get(request_id) is None:
                    tokens[request_id] = token
                    self.set('tokens', tokens)
                    print('Token list updated')
                    await self.send_tokens(token, user_ids)
                    print(f'Tokens are sent to {user_ids}')
