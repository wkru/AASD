from dataclasses import dataclass
from typing import Union

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.template import Template


@dataclass
class ReviewToken:
    hash_: int
    timestamp: int


@dataclass
class Review:
    token: ReviewToken
    contents: str
    rating: int
    request_id: int


class ReviewCollectorAgent(Agent):
    def __init__(self, jid: str, password: str):
        super().__init__(jid, password)

        self.jid = jid
        self.reviews = []
        self.valid_tokens = []
        self.leaderboard = []

        print(self._get_behaviors())

    def __repr__(self):
        return str(self.__class__.__name__)

    def _get_behaviors(self) -> list[Union[CyclicBehaviour, OneShotBehaviour]]:
        return [
            cls_attr for cls_attr in self.__class__.__dict__.values()
            if 'Behav' in str(cls_attr)
        ]

    def update_leaderboard(self) -> None:
        # todo
        pass

    def clear_unused_tokens(self) -> None:
        # drop tokens older than 2 weeks
        # todo
        pass

    async def setup(self):
        print(f'{repr(self)} started')
        for behavior in self._get_behaviors():
            self.add_behaviour(behavior, behavior.template)

    class ReviewCreationBehav(CyclicBehaviour):
        template = Template(metadata={
            'performative': 'request',
            'protocol': ''
        })

        def __init__(self):
            super().__init__()

        async def run(self) -> None:
            # todo
            pass

    class SendTokenExpiredInfoBehav(OneShotBehaviour):
        template = Template(metadata={
            'performative': 'inform',
            'protocol': ''
        })

        async def run(self) -> None:
            # todo
            pass

    class LeaderboardBehav(CyclicBehaviour):
        template = Template(metadata={
            'performative': 'request',
            'protocol': ''
        })

        async def run(self) -> None:
            # todo
            pass

    class ReturnLeaderboardBehav(OneShotBehaviour):
        template = Template(metadata={
            'performative': 'inform',
            'protocol': ''
        })

        async def run(self) -> None:
            # todo
            pass

    class ReviewTokensCreation(CyclicBehaviour):
        template = Template(metadata={
            'performative': 'inform',
            'protocol': ''
        })

        async def run(self) -> None:
            # todo
            pass

    class ReturnReviewTokenBehav(OneShotBehaviour):
        template = Template(metadata={
            'performative': 'inform',
            'protocol': ''
        })

        async def run(self) -> None:
            # todo
            pass

    class UserReviewsBehav(CyclicBehaviour):
        template = Template(metadata={
            'performative': 'request',
            'protocol': ''
        })

        async def run(self) -> None:
            # todo
            pass

    class ReturnUserReviewsBehav(OneShotBehaviour):
        template = Template(metadata={
            'performative': 'inform',
            'protocol': ''
        })

        async def run(self) -> None:
            # todo
            pass
