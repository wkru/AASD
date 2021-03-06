import json
from queue import Queue
import logging

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.template import Template

from src.messages import requestManagement, productVaultServices, serviceDiscovery, userRegistration, reviewManagement
from src.misc.review import Token
from src.config import BROKER_DIRECTORY_JID


class UserAgent(Agent):
    review_collector_key = 'review_collector'

    async def setup(self):
        self.set(self.review_collector_key, 'review-collector-1@localhost')
        self.set('review_tokens', {})

        # self.set("new_request", {'category': 'salt', 'comment': 'Himalaya salt'})
        self.set("notifications", [])
        self.set('queue', Queue(1))

        incoming_request = self.IncomingRequestBehav()
        incoming_request_template = Template()
        incoming_request_template.set_metadata("performative", "propagate")
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
        recv_cancel_template.set_metadata("performative", "propagate")
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

        user_list_resp_b = self.UserListRespBehav()
        self.add_behaviour(
            user_list_resp_b,
            Template(metadata=requestManagement.UserListResponse.metadata),
        )

    class RecvBehav(CyclicBehaviour):
        async def run(self):

            if (msg := await self.receive(timeout=1000)) is not None:
                msg_json = json.loads(msg.body)
                queue = self.agent.get('queue')
                queue.put_nowait(msg_json)

    class AskForRequestsBehav(OneShotBehaviour):
        async def run(self):
            msg = requestManagement.ListRetrieve(to=self.agent.get('information_broker_jid'))

            await self.send(msg)

    class AddRequestBehav(OneShotBehaviour):
        async def run(self):
            if self.agent.get("new_request") is not None:
                msg = requestManagement.Addition(to=self.agent.get('information_broker_jid'), data=self.agent.get("new_request"))
                self.agent.set("new_request", None)
                await self.send(msg)

    class IncomingRequestBehav(CyclicBehaviour):
        async def run(self):
            if (msg := await self.receive(timeout=1000)) is not None:
                msg_json = json.loads(msg.body)
                if msg_json['username'] != str(self.agent.jid):
                    del msg_json["username"]
                    notifications = self.agent.get("notifications")
                    notifications.append(msg_json)
                    self.agent.set("notifications", notifications)

    class AcceptBehav(OneShotBehaviour):
        async def run(self):
            data = {"id": self.agent.get("request_to_accept"),
                    "contact": self.agent.get("contact_data")}
            msg = requestManagement.Acceptance(to=self.agent.get('information_broker_jid'), data=data)

            await self.send(msg)

    class CancelBehav(OneShotBehaviour):
        async def run(self):
            data = {"id": self.agent.get("request_to_cancel")}
            msg = requestManagement.Cancellation(to=self.agent.get('information_broker_jid'), data=data)

            await self.send(msg)

    class RecvAcceptBehav(CyclicBehaviour):
        async def run(self):
            if (msg := await self.receive(timeout=1000)) is not None:
                msg_json = json.loads(msg.body)
                logging.info("Twoje zg??oszenie zosta??o zaakceptowane!")
                logging.info('ID:', msg_json['accepted_request']['id'])
                logging.info('Category:', msg_json['accepted_request']['category'])
                logging.info('Comment:', msg_json['accepted_request']['comment'])
                logging.info('Username:', msg_json['accepted_request']['username'])
                logging.info('Contact info:', msg_json['contact'])
                print("Twoje zg??oszenie zosta??o zaakceptowane!")

                notifications = self.agent.get("notifications")
                notifications.append(msg_json)
                self.agent.set("notifications", notifications)

    class RecvCancelBehav(CyclicBehaviour):
        async def run(self):

            if (msg := await self.receive(timeout=1000)) is not None:
                msg_json = json.loads(msg.body)
                self.agent.set("notifications", [x for x in self.agent.get("notifications") if x['id'] != msg_json['id']])

    class CategoriesReqBehav(OneShotBehaviour):
        async def run(self):
            msg = requestManagement.CategoriesRetrieve(to=self.agent.get('information_broker_jid'))
            await self.send(msg)

    class CategoriesRespBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)
            if msg:
                msg_body = json.loads(msg.body)
                queue = self.agent.get('queue')
                queue.put_nowait(msg_body)

    class VaultOffersReqBehav(OneShotBehaviour):
        async def run(self):
            msg = productVaultServices.OffersRetrieve(to=self.agent.get('product_vault_jid'))
            await self.send(msg)

    class VaultOffersRespBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)
            if msg:
                msg_body = json.loads(msg.body)
                queue = self.agent.get('queue')
                queue.put_nowait(msg_body)

    class VaultCategoriesReqBehav(OneShotBehaviour):
        async def run(self):
            msg = productVaultServices.CategoriesRetrieve(to=self.agent.get('product_vault_jid'))
            await self.send(msg)

    class VaultCategoriesRespBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)
            if msg:
                msg_body = json.loads(msg.body)
                queue = self.agent.get('queue')
                queue.put_nowait(msg_body)

    class VaultAddBehav(OneShotBehaviour):
        async def run(self):
            msg = productVaultServices.AddProductRequest(to=self.agent.get('product_vault_jid'),
                                                         data=self.agent.get('vault_add_product_data'))
            await self.send(msg)

    class VaultGetReqBehav(OneShotBehaviour):
        async def run(self):
            msg = productVaultServices.GetProductRequest(to=self.agent.get('product_vault_jid'),
                                                         data={'id': self.agent.get('vault_get_product_data')})
            await self.send(msg)

    class VaultGetRespBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)
            if msg:
                logging.info("Message received with content: {}".format(msg.body))

    class ServicesReqBehav(OneShotBehaviour):
        async def run(self):
            msg = serviceDiscovery.ServicesRetrieve(to=BROKER_DIRECTORY_JID,
                                                    data=(self.agent.get('location').x,
                                                          self.agent.get('location').y))
            await self.send(msg)

    class ServicesRespBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)
            if msg:
                try:
                    msg_contents = json.loads(msg.body)
                    self.agent.set('information_broker_jid', msg_contents['information-broker'])
                    self.agent.set('review_collector_jid', msg_contents['review-collector'])
                    self.agent.set('product_vault_jid', msg_contents['product-vault'])
                    self.agent.add_behaviour(self.agent.Register())
                except:
                    logging.error('Malformed ServicesRespond message received')

    class Register(OneShotBehaviour):
        async def run(self):
            msg = userRegistration.RegistrationRequest(to=self.agent.get('information_broker_jid'))
            await self.send(msg)

    class Deregister(OneShotBehaviour):
        async def run(self):
            msg = userRegistration.DeregistrationRequest(to=self.agent.get('information_broker_jid'))
            await self.send(msg)

    class LeaderboardReqBehav(OneShotBehaviour):
        async def run(self):
            logging.info(f'{repr(self)} running')
            msg = reviewManagement.Leaderboard(to=self.agent.get(self.agent.review_collector_key))
            await self.send(msg)
            logging.info('Message sent!')

    class LeaderboardRespBehav(CyclicBehaviour):
        async def run(self):
            logging.info(f'{repr(self)} running')
            if (msg := await self.receive(timeout=1000)) is not None:
                logging.info(f'Message received: {msg.body}')
                self.agent.set('last_received_msg', msg)
                leaderboard = json.loads(msg.body)
                queue = self.agent.get('queue')
                queue.put_nowait(leaderboard)

    class ReviewsReqBehav(OneShotBehaviour):
        async def run(self) -> None:
            logging.info(f'{repr(self)} running')
            target_jid = self.agent.get('target_jid')
            self.agent.set('target_jid', None)
            msg = reviewManagement.Reviews(to=self.agent.get(self.agent.review_collector_key), data=target_jid)
            await self.send(msg)
            logging.info('Message sent!')

    class ReviewsRespBehav(CyclicBehaviour):
        async def run(self) -> None:
            logging.info(f'{repr(self)} running')
            if (msg := await self.receive(timeout=1000)) is not None:
                logging.info(f'Message received: {msg.body}')
                self.agent.set('last_received_msg', msg)
                reviews = json.loads(msg.body)
                queue = self.agent.get('queue')
                queue.put_nowait(reviews)

    class ReviewCreationReqBehav(OneShotBehaviour):
        async def run(self) -> None:
            logging.info(f'{repr(self)} running')
            kwargs = self.agent.get('kwargs')

            logging.info(self.agent.get('review_tokens'))
            logging.info(self.agent.get('kwargs'))
            if (token := self.agent.get('review_tokens').get(kwargs.get('request_id'))) is not None:
                msg = reviewManagement.ReviewCreation(
                    to=self.agent.get(self.agent.review_collector_key),
                    kwargs=kwargs,
                    token=token,
                )
                await self.send(msg)
                logging.info('Message sent!')
                tokens = self.agent.get('review_tokens')
                del tokens[kwargs.get('request_id')]
                self.agent.set('kwargs', None)
                self.agent.set('review_tokens', tokens)
                logging.info(f'Token deleted: {token}')

    class ReviewTokenRespBehav(CyclicBehaviour):
        async def run(self) -> None:
            logging.info(f'{repr(self)} running')
            if (msg := await self.receive(timeout=1000)) is not None:
                logging.info(f'Message received: {msg.body}')
                dct = json.loads(msg.body)
                token = Token.from_dict(dct)
                tokens = self.agent.get('review_tokens')
                tokens.update({token.request_id: token})
                self.set('review_tokens', tokens)
                self.agent.set('last_received_msg', msg)

    class UserListReqBehav(OneShotBehaviour):
        async def run(self):
            logging.info(f'{repr(self)} running')
            msg = requestManagement.UserListRetrieve(to=self.agent.get('information_broker_jid'))
            await self.send(msg)

    class UserListRespBehav(CyclicBehaviour):
        async def run(self):
            logging.info(f'{repr(self)} running')
            if (msg := await self.receive(timeout=1000)) is not None:
                logging.info(f'Message received: {msg.body}')
                user_list = json.loads(msg.body)
                queue = self.agent.get('queue')
                queue.put_nowait(user_list)
