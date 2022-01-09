import json

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.template import Template

from src.messages import requestManagement, reviewManagement
from src.misc.review import Token


class UserAgent(Agent):
    review_collector_key = 'review_collector'

    async def setup(self):
        self.set(self.review_collector_key, 'review-collector-0@localhost')
        self.set('review_tokens', {})

        # print("SenderAgent started")
        # b = self.AskForRequestsBehav()
        # self.add_behaviour(b)
        # c = self.RecvBehav()
        # self.add_behaviour(c)
        leaderboard_resp_b = self.LeaderboardRespBehav()
        self.add_behaviour(
            leaderboard_resp_b,
            Template(metadata=reviewManagement.LeaderboardResponse.metadata),
        )

        reviews_b = self.ReviewsRespBehav()
        self.add_behaviour(
            reviews_b,
            Template(metadata=reviewManagement.ReviewsResponse.metadata),
        )

        review_token_resp_b = self.ReviewTokenRespBehav()
        self.add_behaviour(
            review_token_resp_b,
            Template(metadata=reviewManagement.ReviewToken.metadata),
        )

    class RecvBehav(OneShotBehaviour):
        async def run(self):
            print("RecvBehav (UserAgent) running")

            if (msg := await self.receive(timeout=1000)) is not None:
                if str(msg.sender) == 'information-broker-1@localhost':
                    if msg.metadata['performative'] == 'inform':
                        msg_json = json.loads(msg.body)
                        for product in msg_json:
                            print('ID:', product['id'])
                            print('Category:', product['category'])
                            print('Comment:', product['comment'])
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not receive any message after 1000 seconds")

            # stop agent from behaviour
            await self.agent.stop()

    class AskForRequestsBehav(OneShotBehaviour):
        async def run(self):
            print("AskForRequestsBehav running")

            msg = requestManagement.Retrieve(to='information-broker-1@localhost')

            await self.send(msg)
            print("Message sent!")

    class LeaderboardReqBehav(OneShotBehaviour):
        async def run(self):
            print(f'{repr(self)} running')
            msg = reviewManagement.Leaderboard(to=self.agent.get(self.agent.review_collector_key))
            await self.send(msg)
            print('Message sent!')

    class LeaderboardRespBehav(CyclicBehaviour):
        async def run(self):
            print(f'{repr(self)} running')
            if (msg := await self.receive(timeout=1000)) is not None:
                print(f'Message received: {msg.body}')
                self.agent.set('last_received_msg', msg)

    class ReviewsReqBehav(OneShotBehaviour):
        async def run(self) -> None:
            print(f'{repr(self)} running')
            target_jid = self.agent.get('target_jid')
            self.agent.set('target_jid', None)
            msg = reviewManagement.Reviews(to=self.agent.get(self.agent.review_collector_key), data=target_jid)
            await self.send(msg)
            print('Message sent!')

    class ReviewsRespBehav(CyclicBehaviour):
        async def run(self) -> None:
            print(f'{repr(self)} running')
            if (msg := await self.receive(timeout=1000)) is not None:
                print(f'Message received: {msg.body}')
                self.agent.set('last_received_msg', msg)

    class ReviewCreationReqBehav(OneShotBehaviour):
        async def run(self) -> None:
            print(f'{repr(self)} running')
            kwargs = self.agent.get('kwargs')
            self.agent.set('kwargs', None)

            if (token := self.agent.get('review_tokens').get(kwargs.get('request_id'))) is not None:
                msg = reviewManagement.ReviewCreation(
                    to=self.agent.get(self.agent.review_collector_key),
                    kwargs=kwargs,
                    token=token,
                )
                await self.send(msg)
                print('Message sent!')
                tokens = self.agent.get('review_tokens')
                del tokens[kwargs.get('request_id')]
                self.agent.set('review_tokens', tokens)
                print(f'Token deleted: {token}')

    class ReviewTokenRespBehav(CyclicBehaviour):
        async def run(self) -> None:
            print(f'{repr(self)} running')
            if (msg := await self.receive(timeout=1000)) is not None:
                print(f'Message received: {msg.body}')
                dct = json.loads(msg.body)
                token = Token.from_dict(dct)
                tokens = self.agent.get('review_tokens')
                tokens.update({token.request_id: token})
                self.set('review_tokens', tokens)
                self.agent.set('last_received_msg', msg)
