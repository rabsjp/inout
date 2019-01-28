from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

from otree_redwood.models import DecisionGroup
from otree_redwood.utils import DiscreteEventEmitter

import numpy as np
import csv
import math

author = 'Your name here'

doc = """
Your app description
"""

def parse_config(config):
    # parsingmethod for the config files
    with open( 'inout/configs/' +  config) as config_file:
        data = list(csv.DictReader(config_file))


    configs = {
        'period_length': float(data[0]['period_length']),
        'tick_length': float(data[0]['tick_length']),
        'game_constant': float(data[0]['game_constant']),
        'a_sto': float(data[0]['a_sto']),
        's_sto': float(data[0]['s_sto']),
        'x_0': float(data[0]['x_0']),
        'treatment': data[0]['treatment']
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
        return parse_config(self.session.config['config_file'])["period_length"]
    
    def tick_length(self):
        return parse_config(self.session.config['config_file'])["tick_length"]

    def game_constant(self):
        return parse_config(self.session.config['config_file'])["game_constant"]

    def a_sto(self):
        return parse_config(self.session.config['config_file'])["a_sto"]        
    
    def s_sto(self):
        return parse_config(self.session.config['config_file'])["s_sto"]        

    def x_0(self):
        return parse_config(self.session.config['config_file'])["x_0"]
    
    def treatment(self):
        return parse_config(self.session.config['config_file'])["treatment"]        


    def when_all_players_ready(self):
        super().when_all_players_ready()

        self.x_t = None

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

        # For a randomly generated initial uncommment the generate below and the comment the other generate
        self.generate_x_t()

        # Message to channel, Include x_t value for treatment
        msg = {}

        for player in self.get_players():
            playerCode = player.participant.code
            print("player code: " + playerCode)
            if self.group_decisions[playerCode] is 1:
                # player is in, send stochastic value
                print("Decision is true")
                player.update_payoff(self.x_t)
                print(player.get_payoff())
                msg[playerCode] = {
                    'interval': current_interval * self.tick_length(),
                    'value': self.x_t,
                    'payoff': player.get_payoff(),
                    'x_t': self.x_t
                }
            elif self.group_decisions[playerCode] is 0:
                # player is out, send constant C
                print("Decision is false")
                player.update_payoff(self.game_constant())       # Change to constant value
                msg[playerCode] = {
                    'interval': current_interval * self.tick_length(),
                    'value': self.game_constant(),
                    'payoff': player.get_payoff(),
                    'x_t': self.x_t
                }
            else:
                print("Decision is wrong")

        
        # Send message across channel
        self.send('tick', msg)

        

    def generate_x_t(self):
        if self.x_t is None:
            self.x_t = self.x_0()
            self.save()
            return self.x_t
        
        self.x_t = ( (self.a_sto() * self.x_t) + self.generate_noise())
        self.x_t = round(self.x_t, 2)

        self.save()     
        return self.x_t

    def generate_noise(self):
        e_t = np.random.normal(0,1)

        return (self.s_sto() * e_t)





class Player(BasePlayer):
    cumulative_pay = models.IntegerField(initial=0)
    payoff = models.CurrencyField(initial=0)
    def update_payoff(self, pay):
        self.payoff = self.payoff + pay
        self.payoff = round(self.payoff, 2)
        self.cumulative_pay = self.cumulative_pay + pay
        self.cumulative_pay = math.floor(self.cumulative_pay)

        self.save()

    def get_payoff(self):
        return self.cumulative_pay

    def initial_decision(self):
        return 1
