import json
import logging
import collections

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from src.messages import reviewManagement
from src.misc.review import Review, Token


class ReviewCollectorAgent(Agent):
    def init(self):
        # request_id -> token
        self.set('tokens', {})

        if self.get('reviews') is None:
            self.set('reviews', {})
        self.set('leaderboard', [])

    def __repr__(self):
        return str(self.__class__.__name__)

    def update_leaderboard(self):
        def count_ratings(_reviews: list) -> dict:
            counts = {}
            for review in _reviews:
                rating = review.rating
                counts[rating] = counts.get(rating, 0) + 1
            return counts

        def calculate_final_rating(rating_counts: dict) -> float:
            # map ratings [1, 2, 3, 4, 5] to [-2, -1, 0, 1, 2] and sum them
            final_rating = 0
            for rating, count in rating_counts.items():
                final_rating += (rating - 3) * count
            return final_rating

        reviews = self.get('reviews')
        user_ratings = {}
        for user, review_list in reviews.items():
            user_ratings[user] = calculate_final_rating(count_ratings(review_list))
        ordered = collections.OrderedDict(sorted(user_ratings.items(), key=lambda t: t[1], reverse=True))
        self.set('leaderboard', list(ordered.keys())[:25])

    async def setup(self):
        logging.info(f'{repr(self)} started')
        self.init()

        leaderboard_b = self.LeaderboardBehav()
        self.add_behaviour(
            leaderboard_b,
            Template(metadata=reviewManagement.Leaderboard.metadata),
        )

        users_reviews_b = self.ReviewsBehav()
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

    class LeaderboardBehav(CyclicBehaviour):
        async def run(self) -> None:
            logging.info(f'{repr(self)} started')
            if (msg := await self.receive(timeout=1000)) is not None:
                logging.info(f'Message received: {msg.body}')
                resp = reviewManagement.LeaderboardResponse(to=str(msg.sender), data=self.agent.get('leaderboard'))
                await self.send(resp)

    def get_reviews(self, jid: str) -> list[Review]:
        reviews = self.get('reviews')
        for k in reviews.keys():
            if jid in k:
                return reviews[k]
        # return self.get('reviews').get(jid, [])

    class ReviewsBehav(CyclicBehaviour):
        async def run(self) -> None:
            logging.info(f'{repr(self)} started')
            if (msg := await self.receive(timeout=1000)) is not None:
                logging.info(f'Message received: {msg.body}')
                target_jid = json.loads(msg.body)
                resp = reviewManagement.ReviewsResponse(to=str(msg.sender), data=self.agent.get_reviews(target_jid))
                await self.send(resp)

    def create_review(self, contents: str, rating: int, request_id: int, from_: str, to: str) -> None:
        if rating not in [1, 2, 3, 4, 5]:
            logging.info(f'Invalid rating: {rating}')
            return
        new_review = Review(contents, rating, request_id, from_, to)
        reviews = self.get('reviews')
        reviews[to] = reviews.get(to, []) + [new_review]
        self.set('reviews', reviews)

    class ReviewCreationBehav(CyclicBehaviour):
        def are_valid_kwargs(self, kwargs, token: Token) -> bool:
            can_create_review = {'contents', 'rating', 'request_id', 'from_', 'to'}.issubset(kwargs.keys())
            request_id = kwargs.get('request_id')
            valid = self.agent.get('tokens').get(request_id, None) == token
            return can_create_review and valid

        async def run(self) -> None:
            logging.info(f'{repr(self)} started')
            if (msg := await self.receive(timeout=1000)) is not None:
                logging.info(f'Message received: {msg.body}')
                kwargs, token_dct = json.loads(msg.body)
                token = Token.from_dict(token_dct)
                if self.are_valid_kwargs(kwargs, token):
                    self.agent.create_review(**kwargs)
                    logging.info(f'Review created: {kwargs}')

                    self.agent.update_leaderboard()
                    logging.info('Leaderboard updated')

                    tokens = self.agent.get('tokens')
                    del tokens[token.request_id]
                    self.agent.set('tokens', tokens)
                    logging.info(f'Token deleted: {token}')
                else:
                    logging.info(f'Review creation failed: {kwargs}')

    class ReviewTokenCreationBehav(CyclicBehaviour):
        async def send_tokens(self, token: Token, jids: list[str]) -> None:
            for jid in jids:
                msg = reviewManagement.ReviewToken(to=jid, token=token)
                await self.send(msg)

        async def run(self) -> None:
            logging.info(f'{repr(self)} started')
            if (msg := await self.receive(timeout=1000)) is not None:
                logging.info(f'Message received: {msg.body}')

                token_data = json.loads(msg.body)
                request_id = token_data.get('request_id')
                from_ = token_data.get('from_')
                to = token_data.get('to')

                token = Token(request_id, from_, to)

                tokens = self.get('tokens')
                if tokens.get(request_id) is None:
                    tokens[request_id] = token
                    self.set('tokens', tokens)
                    logging.info('Token list updated')
                    await self.send_tokens(token, [from_, to])
                    logging.info(f'Tokens are sent to {[from_, to]}')
