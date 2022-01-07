import copy
import json

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.template import Template

from messages import requestManagement


class UserAgent(Agent):
    class RecvRequestListBehav(CyclicBehaviour):
        async def run(self):
            print(f"RecvRequestListBehav jid: {str(self.agent.jid)} running")

            if (msg := await self.receive(timeout=1000)) is not None:
                if str(msg.sender) == 'information-broker-1@localhost':
                    if msg.metadata['performative'] == 'inform':
                        msg_json = json.loads(msg.body)
                        for product in msg_json:
                            print('ID:', product['id'])
                            print('Category:', product['category'])
                            print('Comment:', product['comment'])
                print(f"jid: {str(self.agent.jid)} Message received with content: {msg.body}")
            else:
                print("Did not receive any message after 1000 seconds")

            # stop agent from behaviour
            # await self.agent.stop()

    class AskForRequestsBehav(OneShotBehaviour):
        async def run(self):
            print(f"AskForRequestsBehav jid:{str(self.agent.jid)} running")
            msg = requestManagement.ListRetrieve(to='information-broker-1@localhost')

            await self.send(msg)
            print("Message sent!")

    class AddRequestBehav(OneShotBehaviour):
        async def run(self):
            print(f"AddRequestBehav jid:{str(self.agent.jid)} running")

            if self.agent.get("new_request") is not None:
                msg = requestManagement.Addition(to='information-broker-1@localhost', data=self.agent.get("new_request"))
                # print(self.agent.get("new_request"))
                self.agent.set("new_request", None)
                # print(self.agent.get("new_request"))
                await self.send(msg)
                print("Message sent!")

    class IncomingRequestBehav(CyclicBehaviour):
        async def run(self):
            print(f"IncomingRequestBehav jid:{str(self.agent.jid)} running")

            if (msg := await self.receive(timeout=1000)) is not None:
                if str(msg.sender) == 'information-broker-1@localhost':
                    if msg.metadata['performative'] == 'inform':
                        msg_json = json.loads(msg.body)
                        if msg_json['username'] != str(self.agent.jid):
                            print('ID:', msg_json['id'])
                            print('Category:', msg_json['category'])
                            print('Comment:', msg_json['comment'])
                            del msg_json["username"]
                            self.agent.set("notifications", self.agent.get("notifications") + [msg_json])
                            print(f'cache {self.agent.jid}: {self.agent.get("notifications")}')
                print(f"jid: {str(self.agent.jid)} Message received with content: {msg.body}")
            else:
                print("Did not receive any message after 1000 seconds")

    class AcceptBehav(OneShotBehaviour):
        async def run(self):
            print(f"AcceptBehav jid:{str(self.agent.jid)} running")
            data = {"id": self.agent.get("request_to_accept"),
                    "contact": self.agent.get("contact_data")}
            msg = requestManagement.Acceptance(to='information-broker-1@localhost', data=data)

            await self.send(msg)

    class CancelBehav(OneShotBehaviour):
        async def run(self):
            print(f"CancelBehav jid:{str(self.agent.jid)} running {self.agent.get('request_to_cancel')}")
            data = {"id": self.agent.get("request_to_cancel")}
            msg = requestManagement.Cancellation(to='information-broker-1@localhost', data=data)

            await self.send(msg)

    class RecvAcceptBehav(CyclicBehaviour):
        async def run(self):
            print(f"RecvAcceptBehav jid:{str(self.agent.jid)} running")

            if (msg := await self.receive(timeout=1000)) is not None:
                if str(msg.sender) == 'information-broker-1@localhost':
                    if msg.metadata['performative'] == 'inform':
                        msg_json = json.loads(msg.body)
                        print("accepted")
                        print('ID:', msg_json['accepted_request']['id'])
                        print('Category:', msg_json['accepted_request']['category'])
                        print('Comment:', msg_json['accepted_request']['comment'])
                        print('Username:', msg_json['accepted_request']['username'])
                        print('contact_info:', msg_json['contact'])
                print(f"jid: {str(self.agent.jid)} Message received with content: {msg.body}")
            else:
                print("Did not receive any message after 1000 seconds")

    class RecvCancelBehav(CyclicBehaviour):
        async def run(self):
            print(f"RecvCancelBehav jid:{str(self.agent.jid)} running")

            if (msg := await self.receive(timeout=1000)) is not None:
                if str(msg.sender) == 'information-broker-1@localhost':
                    if msg.metadata['performative'] == 'inform':
                        msg_json = json.loads(msg.body)
                        # print("cancelled")
                        print('ID:', msg_json['id'])
                        self.agent.set("notifications", [x for x in self.agent.get("notifications") if x['id'] != msg_json['id']])
                        print(self.agent.get("notifications"))
                print(f"jid: {str(self.agent.jid)} Message received with content: {msg.body}")
            else:
                print("Did not receive any message after 1000 seconds")

    async def setup(self):
        # self.set("new_request", {'category': 'salt', 'comment': 'Himalaya salt'})
        self.set("contact_data", {'phone': "000-000-000", "email": "test@test.pl"})
        self.set("notifications", [{'id': 'f9a4be60598dac4d8c28157c2a342cff4e3caed484fc27bab97be2790d75caa5',
                                    'category': 'salt', 'comment': 'Himalaya salt'}])

        print("SenderAgent started")

        incoming_request = self.IncomingRequestBehav()
        incoming_request_template = Template()
        incoming_request_template.set_metadata("performative", "inform")
        incoming_request_template.set_metadata("protocol", "addition")
        self.add_behaviour(incoming_request, incoming_request_template)

        recv_request_list = self.RecvRequestListBehav()
        recv_request_list_template = Template()
        recv_request_list_template.set_metadata("performative", "inform")
        recv_request_list_template.set_metadata("protocol", "user_requests")
        self.add_behaviour(recv_request_list, recv_request_list_template)

        recv_accept = self.RecvAcceptBehav()
        recv_accept_template = Template()
        recv_accept_template.set_metadata("performative", "inform")
        recv_accept_template.set_metadata("protocol", "acceptance")
        self.add_behaviour(recv_accept, recv_accept_template)

        recv_cancel = self.RecvCancelBehav()
        recv_cancel_template = Template()
        recv_cancel_template.set_metadata("performative", "inform")
        recv_cancel_template.set_metadata("protocol", "cancellation")
        self.add_behaviour(recv_cancel, recv_cancel_template)


