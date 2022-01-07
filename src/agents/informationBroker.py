import secrets
import json

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from messages import requestManagement


class InformationBrokerAgent(Agent):
    async def setup(self):
        self.set("requests", [{'id': 1, 'category': 'salt', 'comment': 'Himalaya salt', 'username': 'user1@localhost'},
                         {"id": "f9a4be60598dac4d8c28157c2a342cff4e3caed484fc27bab97be2790d75caa5",
                          "username": "user2@localhost", "category": "salt", "comment": "Himalaya salt"}
                         ])
        self.set("users",  ['user1@localhost', 'user2@localhost'])

        print("ReceiverAgent started")

        user_requests = self.UserRequestsBehav()
        template = Template()
        template.set_metadata("performative", "request")
        template.set_metadata("protocol", "user_requests")
        self.add_behaviour(user_requests, template)

        add_request = self.AddRequestBehav()
        add_request_template = Template()
        add_request_template.set_metadata("performative", "request")
        add_request_template.set_metadata("protocol", "addition")
        self.add_behaviour(add_request, add_request_template)

        accepted_request = self.AcceptedBehav()
        accepted_request_template = Template()
        accepted_request_template.set_metadata("performative", "request")
        accepted_request_template.set_metadata("protocol", "acceptance")
        self.add_behaviour(accepted_request, accepted_request_template)

        cancelled_request = self.CancelledBehav()
        cancelled_request_template = Template()
        cancelled_request_template.set_metadata("performative", "request")
        cancelled_request_template.set_metadata("protocol", "cancellation")
        self.add_behaviour(cancelled_request, cancelled_request_template)

    class UserRequestsBehav(CyclicBehaviour):
        async def run(self):
            print("UserRequestsBehav running")
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg and msg.metadata['performative'] == 'request':
                resp = requestManagement.ListResponse(to=str(msg.sender), data=self.agent.get("requests"))
                await self.send(resp)
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not receive any message after 10 seconds")

            # stop agent from behaviour
            # await self.agent.stop()

    class AddRequestBehav(CyclicBehaviour):
        async def run(self):
            print("AddRequestBehav running")
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg:
                if msg.metadata['performative'] == 'request':
                    body = json.loads(msg.body)
                    request = {"id": secrets.token_hex(nbytes=32),
                               "username": str(msg.sender),
                               "category": body["category"],
                               "comment": body["comment"]}
                    self.agent.set("requests", self.agent.get("requests").append(request))
                    for user in self.agent.get("users"):
                        resp = requestManagement.BroadcastNew(to=user, data=request)
                        await self.send(resp)
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not receive any message after 10 seconds")

    class AcceptedBehav(CyclicBehaviour):
        async def run(self):
            print("AcceptedBehav running")
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg and msg.metadata['performative'] == 'request':
                data = json.loads(msg.body)
                request_valid = False
                for request in self.agent.get("requests"):
                    if request["id"] == data["id"]:
                        request_valid = True
                        request_to_forward = request
                        self.agent.set("requests", [x for x in self.agent.get("requests") if x["id"] != data["id"]])
                        print(self.agent.get("requests"))
                        break
                if request_valid:
                    new_data = {"accepted_request": request_to_forward,
                                "contact": data["contact"]}
                    # send acceptance message to user who issued the request
                    forward_msg = requestManagement.AcceptanceForward(to=request_to_forward["username"], data=new_data)

                    # cancel request for other users apart from issuer and acceptor
                    for user in self.agent.get("users"):
                        if user != request_to_forward["username"] and user != str(msg.sender):
                            cancel_msg = requestManagement.CancellationForward(to=user, data=data)["id"]
                            await self.send(cancel_msg)
                    await self.send(forward_msg)

                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not receive any message after 10 seconds")

    class CancelledBehav(CyclicBehaviour):
        async def run(self):
            print("CancelledBehav running")
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg and msg.metadata['performative'] == 'request':
                data = json.loads(msg.body)
                request_valid = False
                for request in self.agent.get("requests"):
                    if request['id'] == data['id'] and request['username'] == str(msg.sender):
                        request_valid = True
                        self.agent.set("requests", [x for x in self.agent.get("requests") if x["id"] != data["id"]])
                        break
                if request_valid:
                    # send cancellation message to all users except issuer
                    for user in self.agent.get("users"):
                        if user != str(msg.sender):
                            forward_msg = requestManagement.CancellationForward(to=user, data=data)
                            await self.send(forward_msg)

                print("Cancel Message received with content: {} {}".format(msg.body, str(msg.sender)))
            else:
                print("Did not receive any message after 10 seconds")
