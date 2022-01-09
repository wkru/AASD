from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.template import Template

from messages import requestManagement
from messages import reviewManagement


class InformationBrokerAgent(Agent):
    review_collector_key = 'review_collector'

    async def setup(self):
        self.set(self.review_collector_key, 'review-collector-0@localhost')
        self.set('requests', [{'id': 1, 'category': 'salt', 'comment': 'Himalaya salt', 'username': 'user1@localhost'}])
        # [('from_': 'user0', 'to': 'user1', 'request_id': 1), ('from_': 'user1', 'to': 'user0', 'request_id': 2)
        self.set('tokens_to_issue', [])
        print("ReceiverAgent started")
        b = self.UserRequestsBehav()
        template = Template()
        template.set_metadata("performative", "request")
        template.set_metadata("protocol", "user_requests")
        self.add_behaviour(b, template)

    class UserRequestsBehav(OneShotBehaviour):
        async def run(self):
            print("RecvBehav running")
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg:
                if msg.metadata['performative'] == 'request':
                    resp = requestManagement.Response(to=str(msg.sender), data=self.agent.requests)
                    await self.send(resp)
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not receive any message after 10 seconds")

            # stop agent from behaviour
            await self.agent.stop()

    class ReviewTokenCreationReqBehav(OneShotBehaviour):
        async def run(self) -> None:
            print(f'{repr(self)} running')
            tokens_to_issue = self.agent.get('tokens_to_issue')
            print('here', self.agent)
            if len(tokens_to_issue) and (token_data := tokens_to_issue.pop(0)):
                msg = reviewManagement.ReviewTokenCreation(
                    to=self.agent.get(self.agent.review_collector_key),
                    request_id=token_data.get('request_id'),
                    userids=[token_data.get('from_'), token_data.get('to')]
                )
                await self.send(msg)
                print('Message sent!')
                self.set('tokens_to_issue', tokens_to_issue)
            else:
                print('No tokens to issue')
