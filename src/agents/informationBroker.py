import secrets
import json
import logging

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from src.messages import requestManagement
from src.messages import reviewManagement


class InformationBrokerAgent(Agent):
    review_collector_key = 'review_collector'

    async def setup(self):
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
        add_request_template.set_metadata("performative", "propagate")
        add_request_template.set_metadata("protocol", "addition")
        self.add_behaviour(add_request, add_request_template)

        accepted_request = self.AcceptedBehav()
        accepted_request_template = Template()
        accepted_request_template.set_metadata("performative", "proxy")
        accepted_request_template.set_metadata("protocol", "acceptance")
        self.add_behaviour(accepted_request, accepted_request_template)

        cancelled_request = self.CancelledBehav()
        cancelled_request_template = Template()
        cancelled_request_template.set_metadata("performative", "propagate")
        cancelled_request_template.set_metadata("protocol", "cancellation")
        self.add_behaviour(cancelled_request, cancelled_request_template)

        categories_request = self.CategoriesBehav()
        categories_request_template = Template()
        categories_request_template.set_metadata("performative", "request")
        categories_request_template.set_metadata("protocol", "categories")
        self.add_behaviour(categories_request, categories_request_template)

        register_request = self.RegisterBehav()
        register_request_template = Template()
        register_request_template.set_metadata("performative", "subscribe")
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
                body = json.loads(msg.body)
                request = {"id": secrets.token_hex(nbytes=32),
                           "username": str(msg.sender),
                           "category": body["category"],
                           "comment": body["comment"]}
                requests = self.agent.get("requests")
                requests.append(request)
                self.agent.set("requests", requests)
                for user in self.agent.get("users"):
                    if str(msg.sender) != user:
                        resp = requestManagement.BroadcastNew(to=user, data=request)
                        await self.send(resp)

    class AcceptedBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg:
                data = json.loads(msg.body)
                request_valid = False
                for request in self.agent.get("requests"):
                    # print('acceptedbehav loop')
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

                    # generate review tokens
                    token_to_issue = {'request_id': request_to_forward['id'],
                                        # 'from_': str(msg.sender),
                                        # 'to': request_to_forward['username']}
                                        'from_': request_to_forward['username'],
                                        'to': str(msg.sender)}
                    msg = reviewManagement.ReviewTokenCreation(
                            to=self.agent.get(self.agent.review_collector_key),
                            request_id=token_to_issue.get('request_id'),
                            from_to=(token_to_issue.get('from_'), token_to_issue.get('to'),)
                        )
                    await self.send(msg)

                    # cancel request for other users apart from issuer and acceptor
                    for user in self.agent.get("users"):
                        if user != request_to_forward["username"] and user != str(msg.sender):
                            cancel_msg = requestManagement.CancellationForward(to=user, data=data)
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
                    logging.error('User {} not in active users'.format(msg.sender))
