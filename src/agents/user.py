import json
import logging

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.template import Template

from messages import requestManagement, reviewManagement


class UserAgent(Agent):
    def __init__(self, jid: str, password: str):
        super().__init__(jid, password)
        self._review_collector_jid = 'review-collector-0@localhost'

    async def setup(self):
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
            logging.info(f'{repr(self)} running')
            msg = reviewManagement.Leaderboard(to=self.agent._review_collector_jid)
            await self.send(msg)
            logging.info('Message sent!')

    class LeaderboardRespBehav(CyclicBehaviour):
        async def run(self):
            logging.info(f'{repr(self)} running')
            if (msg := await self.receive(timeout=1000)) is not None:
                logging.info(f'Message received: {msg.body}')
                self.agent.set('last_received_msg', msg)
