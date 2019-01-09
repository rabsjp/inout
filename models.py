from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

from otree_redwood.models import DecisionGroup
from otree_redwood.utils import DiscreteEventEmitter

import numpy as np

author = 'Your name here'

doc = """
Your app description
"""

def parse_config(config):
    # parsingmethod for the config files

    # Hard Coded now but will change to be from config
    configs = {
        'period_length': 60,
        'tick_length': 2,
        'num_rounds': 1,
        'constant': 120,
        'a_sto': .5,
        's_sto': .5

    }

    return configs


class Constants(BaseConstants):
    name_in_url = 'inout'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(DecisionGroup):
    interval = models.IntegerField(initial=0)
    x_t = models.IntegerField(initial=0) 

    def placeholder_callback(self):
        return {'msg': "test"}

    def period_length(self):
        return parse_config("placeholder")["period_length"]
    
    def tick_length(self):
        return parse_config("placeholder")["tick_length"]

    def a_sto(self):
        return parse_config("placeholder")["a_sto"]        
    
    def s_sto(self):
        return parse_config("placeholder")["s_sto"]        

    def constant_payout(self):
        return parse_config("placeholder")["constant"]

    def when_all_players_ready(self):
        super().when_all_players_ready()
        print("started")

        emitter = DiscreteEventEmitter(
            self.tick_length(),
            self.period_length(),
            self,
            self.tick,
            True
        )
        emitter.start()

    def tick(self, current_interval, interval):
        self.refresh_from_db()


        # Message to channel, Include x_t value for treatment
        msg = {}

        for player in self.get_players():
            playerCode = player.participant.code
            if self.group_decisions[playerCode] is 1:
                # player is in, send stochastic value
                player.update_payoff(self.x_t)
                msg[playerCode] = {
                    'interval': current_interval * self.tick_length(),
                    'value': self.x_t,
                    'payoff': player.get_payoff(),
                    'x_t': self.x_t
                }
            elif self.group_decisions[playerCode] is 0:
                # player is out, send constant C
                player.update_payoff(100)       # Change to constant value
                msg[playerCode] = {
                    'interval': current_interval * self.tick_length(),
                    'value': 100,
                    'payoff': player.get_payoff(),
                    'x_t': self.x_t
                }
            else:
                print("Decision is wrong")

        
        # Send message across channel
        self.send('tick', msg)

        # For a hard coded initial value keep down here
        # For a randomly generated initial value move to before message generation
        self.generate_x_t()

    def generate_x_t(self):
        self.x_t = ( (self.a_sto() * self.x_t) + self.generate_noise())

        # print(self.x_t)            
        return self.x_t

    def generate_noise(self):
        e_t = np.random.normal(0,1)

        print( (self.s_sto() * e_t) )
        return (self.s_sto() * e_t)





class Player(BasePlayer):
    cumulative_pay = models.IntegerField(initial=0)
    payoff = models.CurrencyField(initial=0)
    status = models.BooleanField()

    def initial_decision(self):
        return 0

    def get_status(self):
        return self.status

    def set_status(self):
        self.status = not self.status

    def update_payoff(self, pay):
        self.payoff = self.payoff + pay
        self.cumulative_pay = self.cumulative_pay + pay

    def get_payoff(self):
        return self.cumulative_pay
