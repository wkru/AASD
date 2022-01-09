import json

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.template import Template

from src.messages import requestManagement, productVaultServices, serviceDiscovery, userRegistration, reviewManagement
from src.misc.review import Token

from src.config import BROKER_DIRECTORY_JID

class UserAgent(Agent):
    review_collector_key = 'review_collector'

    async def setup(self):
        self.set(self.review_collector_key, 'review-collector-0@localhost')
        self.set('review_tokens', {})

        # self.set("new_request", {'category': 'salt', 'comment': 'Himalaya salt'})
        self.set("contact_data", {'phone': "000-000-000", "email": "test@test.pl"})
        self.set("notifications", [{'id': 'f9a4be60598dac4d8c28157c2a342cff4e3caed484fc27bab97be2790d75caa5',
                                    'category': 'salt', 'comment': 'Himalaya salt'}])

        incoming_request = self.IncomingRequestBehav()
        incoming_request_template = Template()
        incoming_request_template.set_metadata("performative", "inform")
        incoming_request_template.set_metadata("protocol", "addition")
        self.add_behaviour(incoming_request, incoming_request_template)

        recv_request_list = self.RecvBehav()
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

        categories_resp_b = self.CategoriesRespBehav()
        categories_resp_template = Template()
        categories_resp_template.set_metadata("performative", "inform")
        categories_resp_template.set_metadata("protocol", "categories")
        self.add_behaviour(categories_resp_b, categories_resp_template)

        vault_offers_resp_b = self.VaultOffersRespBehav()
        vault_offers_resp_template = Template()
        vault_offers_resp_template.set_metadata("performative", "inform")
        vault_offers_resp_template.set_metadata("protocol", "vault_offers")
        self.add_behaviour(vault_offers_resp_b, vault_offers_resp_template)

        vault_categories_resp_b = self.VaultCategoriesRespBehav()
        vault_categories_resp_template = Template()
        vault_categories_resp_template.set_metadata("performative", "inform")
        vault_categories_resp_template.set_metadata("protocol", "vault_categories")
        self.add_behaviour(vault_categories_resp_b, vault_categories_resp_template)

        vault_get_resp_b = self.VaultGetRespBehav()
        vault_get_resp_template = Template()
        vault_get_resp_template.set_metadata("performative", "inform")
        vault_get_resp_template.set_metadata("protocol", "vault_get")
        self.add_behaviour(vault_get_resp_b, vault_get_resp_template)

        services_resp_b = self.ServicesRespBehav()
        services_resp_template = Template()
        services_resp_template.set_metadata("performative", "inform")
        services_resp_template.set_metadata("protocol", "local_services")
        self.add_behaviour(services_resp_b, services_resp_template)

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
            print(f"RecvRequestListBehav jid: {str(self.agent.jid)} running")

            if (msg := await self.receive(timeout=1000)) is not None:
                msg_json = json.loads(msg.body)
                for product in msg_json:
                    print('ID:', product['id'])
                    print('Category:', product['category'])
                    print('Comment:', product['comment'])
                print(f"jid: {str(self.agent.jid)} Message received with content: {msg.body}")

    class AskForRequestsBehav(OneShotBehaviour):
        async def run(self):
            print(f"AskForRequestsBehav jid:{str(self.agent.jid)} running")
            msg = requestManagement.ListRetrieve(to=self.agent.get('information_broker_jid'))

            await self.send(msg)

    class AddRequestBehav(OneShotBehaviour):
        async def run(self):
            print(f"AddRequestBehav jid:{str(self.agent.jid)} running")

            if self.agent.get("new_request") is not None:
                msg = requestManagement.Addition(to=self.agent.get('information_broker_jid'), data=self.agent.get("new_request"))
                # print(self.agent.get("new_request"))
                self.agent.set("new_request", None)
                # print(self.agent.get("new_request"))
                await self.send(msg)

    class IncomingRequestBehav(CyclicBehaviour):
        async def run(self):
            print(f"IncomingRequestBehav jid:{str(self.agent.jid)} running")

            if (msg := await self.receive(timeout=1000)) is not None:
                msg_json = json.loads(msg.body)
                if msg_json['username'] != str(self.agent.jid):
                    print('ID:', msg_json['id'])
                    print('Category:', msg_json['category'])
                    print('Comment:', msg_json['comment'])
                    del msg_json["username"]
                    self.agent.set("notifications", self.agent.get("notifications") + [msg_json])
                    print(f'cache {self.agent.jid}: {self.agent.get("notifications")}')
                print(f"jid: {str(self.agent.jid)} Message received with content: {msg.body}")

    class AcceptBehav(OneShotBehaviour):
        async def run(self):
            print(f"AcceptBehav jid:{str(self.agent.jid)} running")
            data = {"id": self.agent.get("request_to_accept"),
                    "contact": self.agent.get("contact_data")}
            msg = requestManagement.Acceptance(to=self.agent.get('information_broker_jid'), data=data)

            await self.send(msg)

    class CancelBehav(OneShotBehaviour):
        async def run(self):
            print(f"CancelBehav jid:{str(self.agent.jid)} running {self.agent.get('request_to_cancel')}")
            data = {"id": self.agent.get("request_to_cancel")}
            msg = requestManagement.Cancellation(to=self.agent.get('information_broker_jid'), data=data)

            await self.send(msg)

    class RecvAcceptBehav(CyclicBehaviour):
        async def run(self):
            print(f"RecvAcceptBehav jid:{str(self.agent.jid)} running")

            if (msg := await self.receive(timeout=1000)) is not None:
                msg_json = json.loads(msg.body)
                print("accepted")
                print('ID:', msg_json['accepted_request']['id'])
                print('Category:', msg_json['accepted_request']['category'])
                print('Comment:', msg_json['accepted_request']['comment'])
                print('Username:', msg_json['accepted_request']['username'])
                print('contact_info:', msg_json['contact'])
                print(f"jid: {str(self.agent.jid)} Message received with content: {msg.body}")

    class RecvCancelBehav(CyclicBehaviour):
        async def run(self):
            print(f"RecvCancelBehav jid:{str(self.agent.jid)} running")

            if (msg := await self.receive(timeout=1000)) is not None:
                msg_json = json.loads(msg.body)
                # print("cancelled")
                print('ID:', msg_json['id'])
                self.agent.set("notifications", [x for x in self.agent.get("notifications") if x['id'] != msg_json['id']])
                print(self.agent.get("notifications"))
                print(f"jid: {str(self.agent.jid)} Message received with content: {msg.body}")

    class CategoriesReqBehav(OneShotBehaviour):
        async def run(self):
            print('CategoriesReqBehav running')

            msg = requestManagement.CategoriesRetrieve(to=self.agent.get('information_broker_jid'))
            await self.send(msg)

    class CategoriesRespBehav(CyclicBehaviour):
        async def run(self):
            print("CategoriesRespBehav running")
            msg = await self.receive(timeout=1000)
            if msg:
                print("Message received with content: {}".format(msg.body))

    class VaultOffersReqBehav(OneShotBehaviour):
        async def run(self):
            print('VaultOffersReqBehav running')

            msg = productVaultServices.OffersRetrieve(to=self.agent.get('product_vault_jid'))
            await self.send(msg)

    class VaultOffersRespBehav(CyclicBehaviour):
        async def run(self):
            print("VaultOffersRespBehav running")
            msg = await self.receive(timeout=1000)
            if msg:
                print("Message received with content: {}".format(msg.body))

    class VaultCategoriesReqBehav(OneShotBehaviour):
        async def run(self):
            print('VaultCategoriesReqBehav running')

            msg = productVaultServices.CategoriesRetrieve(to=self.agent.get('product_vault_jid'))
            await self.send(msg)

    class VaultCategoriesRespBehav(CyclicBehaviour):
        async def run(self):
            print("VaultCategoriesRespBehav running")
            msg = await self.receive(timeout=1000)
            if msg:
                print("Message received with content: {}".format(msg.body))

    class VaultAddBehav(OneShotBehaviour):
        async def run(self):
            print('VaultAddBehav running')

            msg = productVaultServices.AddProductRequest(to=self.agent.get('product_vault_jid'),
                                                         data=self.agent.get('vault_add_product_data'))
            await self.send(msg)

    class VaultGetReqBehav(OneShotBehaviour):
        async def run(self):
            print('VaultGetReqBehav running')

            msg = productVaultServices.GetProductRequest(to=self.agent.get('product_vault_jid'),
                                                         data=self.agent.get('vault_get_product_data'))
            await self.send(msg)

    class VaultGetRespBehav(CyclicBehaviour):
        async def run(self):
            print("VaultGetRespBehav running")
            msg = await self.receive(timeout=1000)
            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                pass

    class ServicesReqBehav(OneShotBehaviour):
        async def run(self):
            print("ServicesReqBehav running")

            msg = serviceDiscovery.ServicesRetrieve(to=BROKER_DIRECTORY_JID,
                                                    data=(self.agent.get('location').x,
                                                          self.agent.get('location').y))
            await self.send(msg)

    class ServicesRespBehav(CyclicBehaviour):
        async def run(self):
            print("ServicesRespBehav running")
            msg = await self.receive(timeout=1000)
            if msg:
                try:
                    msg_contents = json.loads(msg.body)
                    self.agent.set('information_broker_jid', msg_contents['information-broker'])
                    self.agent.set('review_collector_jid', msg_contents['review-collector'])
                    self.agent.set('product_vault_jid', msg_contents['product-vault'])
                except:
                    print('Malformed ServicesRespond message received')
                print("Message received with content: {}".format(msg.body))
            else:
                pass

    class Register(OneShotBehaviour):
        async def run(self):
            print("Register running")

            msg = userRegistration.RegistrationRequest(to=self.agent.get('information_broker_jid'))
            await self.send(msg)

    class Deregister(OneShotBehaviour):
        async def run(self):
            print("Deregister running")

            msg = userRegistration.DeregistrationRequest(to=self.agent.get('information_broker_jid'))
            await self.send(msg)

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
