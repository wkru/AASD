from factories.abstractFactory import AbstractFactory
from agents.reviewCollector import ReviewCollectorAgent


class ReviewCollectorFactory(AbstractFactory):
    jid_template = 'review-collector'
    agents: list[ReviewCollectorAgent] = []

    @classmethod
    def create_agent(cls) -> ReviewCollectorAgent:
        new_agent = cls._create_agent(ReviewCollectorAgent)
        return new_agent
