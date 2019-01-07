from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

from otree_redwood.models import DecisionGroup
from otree_redwood.utils import DiscreteEventEmitter

author = 'Your name here'

doc = """
Your app description
"""

def parse_config(config):
    # parsingmethod for the config files

    configs = {
        'period_length': 60,
        'num_rounds': 1,

    }

    return configs


class Constants(BaseConstants):
    name_in_url = 'inout'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(DecisionGroup):
    def placeholder_callback(self):
        return {'msg': "test"}

    def period_start(self, current_interval, intervals):
        pass

    def period_length(self):
        return parse_config("placeholder")["period_length"]

    def when_all_players_ready(self):
        super().when_all_players_ready()

        
        print("started")

    def tick(self, interval):
        pass


class Player(BasePlayer):
    payoff = models.IntegerField()

    def initial_decision(self):
        return 0
