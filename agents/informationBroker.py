from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.template import Template

from messages import requestManagement


class InformationBrokerAgent(Agent):
    async def setup(self):
        self.requests = [{'id': 1, 'category': 'salt', 'comment': 'Himalaya salt', 'username': 'user1@localhost'}]
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
