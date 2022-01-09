import secrets
import json

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.template import Template

from src.messages import requestManagement
from src.messages import reviewManagement


class InformationBrokerAgent(Agent):
    review_collector_key = 'review_collector'

    async def setup(self):
        self.set(self.review_collector_key, 'review-collector-0@localhost')
        self.set("requests", [{'id': 1, 'category': 'salt', 'comment': 'Himalaya salt', 'username': 'user1@localhost'},
                         {"id": "f9a4be60598dac4d8c28157c2a342cff4e3caed484fc27bab97be2790d75caa5",
                          "username": "user2@localhost", "category": "salt", "comment": "Himalaya salt"}
                         ])
        self.set("users",  [])
        self.set("categories", ["salt", "pepper"])

        # [('from_': 'user0', 'to': 'user1', 'request_id': 1), ('from_': 'user1', 'to': 'user0', 'request_id': 2)
        self.set('tokens_to_issue', [])

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

        categories_request = self.CategoriesBehav()
        categories_request_template = Template()
        categories_request_template.set_metadata("performative", "request")
        categories_request_template.set_metadata("protocol", "categories")
        self.add_behaviour(categories_request, categories_request_template)

        register_request = self.RegisterBehav()
        register_request_template = Template()
        register_request_template.set_metadata("performative", "request")
        register_request_template.set_metadata("protocol", "register")
        self.add_behaviour(register_request, register_request_template)

        deregister_request = self.DeregisterBehav()
        deregister_request_template = Template()
        deregister_request_template.set_metadata("performative", "request")
        deregister_request_template.set_metadata("protocol", "deregister")
        self.add_behaviour(deregister_request, deregister_request_template)

    class UserRequestsBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg:
                resp = requestManagement.ListResponse(to=str(msg.sender), data=self.agent.get("requests"))
                await self.send(resp)

    class AddRequestBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg:
                if msg.metadata['performative'] == 'request':
                    body = json.loads(msg.body)
                    request = {"id": secrets.token_hex(nbytes=32),
                               "username": str(msg.sender),
                               "category": body["category"],
                               "comment": body["comment"]}
                    requests = self.agent.get("requests")
                    requests.append(request)
                    self.agent.set("requests", requests)
                    for user in self.agent.get("users"):
                        resp = requestManagement.BroadcastNew(to=user, data=request)
                        await self.send(resp)

    class AcceptedBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg:
                data = json.loads(msg.body)
                request_valid = False
                for request in self.agent.get("requests"):
                    if request["id"] == data["id"]:
                        request_valid = True
                        request_to_forward = request
                        self.agent.set("requests", [x for x in self.agent.get("requests") if x["id"] != data["id"]])
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

    class CancelledBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg:
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

    class CategoriesBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)
            if msg:
                resp = requestManagement.CategoriesResponse(to=str(msg.sender), data=self.agent.get('categories'))
                await self.send(resp)

    class RegisterBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg:
                users = self.agent.get('users')
                users.append(str(msg.sender))
                self.agent.set('users', users)

    class DeregisterBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg:
                try:
                    users = self.agent.get('users')
                    users.remove(str(msg.sender))
                    self.agent.set('users', users)
                except:
                    print('User {} not in active users'.format(msg.sender))



    class ReviewTokenCreationReqBehav(OneShotBehaviour):
        async def run(self) -> None:
            print(f'{repr(self)} running')
            tokens_to_issue = self.agent.get('tokens_to_issue')
            if len(tokens_to_issue) and (token_data := tokens_to_issue.pop(0)):
                msg = reviewManagement.ReviewTokenCreation(
                    to=self.agent.get(self.agent.review_collector_key),
                    request_id=token_data.get('request_id'),
                    user_ids=[token_data.get('from_'), token_data.get('to')]
                )
                await self.send(msg)
                print('Message sent!')
                self.set('tokens_to_issue', tokens_to_issue)
            else:
                print('No tokens to issue')
