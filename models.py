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
        rows = list(csv.DictReader(config_file))

    # Single round implementation, for more rounds add more rows and
    # traverse them
    configs = []
    for row in rows:
        configs.append({
            'period_length': float(row['period_length']),
            'tick_length': float(row['tick_length']),
            'game_constant': float(row['game_constant']),
            'a_sto': float(row['a_sto']),
            'b_sto': float(row['b_sto']),
            's_sto': float(row['s_sto']),
            'x_0': float(row['x_0']),
            'treatment': row['treatment'],
            'num_practice_rounds': float(row['num_practice_rounds']),
            
        })
    return configs


class Constants(BaseConstants):
    name_in_url = 'inout'
    players_per_group = None
    num_rounds = 100


class Subsession(BaseSubsession):
    pass


class Group(DecisionGroup):
    interval = models.IntegerField(initial=0)
    x_t = models.IntegerField(initial=0) 
    # Getters for config values
    def period_length(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]["period_length"]
    
    def tick_length(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]["tick_length"]

    def game_constant(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]["game_constant"]

    def a_sto(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]["a_sto"]        
    
    def b_sto(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]["b_sto"]        
    
    def s_sto(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]["s_sto"]        

    def x_0(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]["x_0"]
    
    def treatment(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]["treatment"]        

    def num_rounds(self):
        return len(parse_config(self.session.config['config_file']))
    
    def num_practice_rounds(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]["num_practice_rounds"]  
    
    
    # oTree Redwood method
    def when_all_players_ready(self):
        super().when_all_players_ready()

        # Needed for first tick logic
        self.x_t = None

        emitter = DiscreteEventEmitter(
            self.tick_length(),
            self.period_length(),
            self,
            self.tick,
            True
        )
        emitter.start()

    # oTree Redwood tick
    def tick(self, current_interval, interval):
        self.refresh_from_db()

        # For a randomly generated initial uncommment the generate below and the comment the other generate
        self.generate_x_t()

        # Message to channel, Include x_t value for treatment
        msg = {}

        for player in self.get_players():
            playerCode = player.participant.code
            # print("player code: " + playerCode)
            if self.group_decisions[playerCode] is 1:
                # player is in, send stochastic value
                player.update_payoff(self.x_t+self.b_sto())
                msg[playerCode] = {
                    'interval': current_interval * self.tick_length(),
                    'value': self.x_t+self.b_sto(),
                    'payoff': player.get_payoff(),
                    'x_t': self.x_t+self.b_sto(), # change the x displayed
                    'decision': 1
                }
            elif self.group_decisions[playerCode] is 0:
                # player is out, send constant C
                player.update_payoff(self.game_constant())
                msg[playerCode] = {
                    'interval': current_interval * self.tick_length(),
                    'value': self.game_constant(),
                    'payoff': player.get_payoff(),
                    'x_t': self.x_t+self.b_sto(), # change the x displayed
                    'decision': 0
                }
            else:
                print("ERROR IN TICK PROCESSING!")

        # Send message across channel
        self.send('tick', msg)

        

    # Random value generator using formula in spec
    def generate_x_t(self):
        # First tick logic
        if self.x_t is None:
            # Set X_0 to value determined by config
            self.x_t = self.x_0()

            # Always save so database updates user values
            self.save()
            return self.x_t
        
        # Not first tick so follow forula specification
        self.x_t = ( (self.a_sto() * self.x_t) + self.generate_noise())
        
        # b offset value
        #self.x_t += self.b_sto()

        # round to .2f
        self.x_t = round(self.x_t, 2)

        # Always save so database updates user values
        self.save()     
        return self.x_t

    # Noise generation
    def generate_noise(self):
        # Genrate number on normal distribution using Numpy
        # Mean: 0 
        # Std. D: 1
        e_t = np.random.normal(0,1)

        # Multiply by s value (Determined by config)
        return (self.s_sto() * e_t)





class Player(BasePlayer):
    # total payoff
    cumulative_pay = models.IntegerField(initial=0)
    # oTree payoff (probably not needed just kept for redundancy)
    payoff = models.CurrencyField(initial=0)

    # Update both payoff values
    def update_payoff(self, pay):
        #self.payoff = self.payoff + pay
        #self.payoff = round(self.payoff, 2)
        #if self.round_number>0 : 
        self.cumulative_pay = self.cumulative_pay + pay
        self.cumulative_pay = math.floor(self.cumulative_pay)
        self.payoff = self.cumulative_pay
        #else: 
        #    self.cumulative_pay = 0 
        #    self.payoff = 0
        
        # Always save so database updates user values
        self.save()

    # Getter for payoff
    # Note: returniong cumulative payoff since payoff is of type
    #       Curreny(). Causes error with redwood messaging
    def get_payoff(self):
        return self.cumulative_pay
    
    def set_cumpay(self):    
        
        if self.round_number > self.group.num_practice_rounds(): 
            self.cum_payoff = sum([j.cumulative_pay for j in self.in_rounds(self.group.num_practice_rounds()+1, self.round_number)])
        else:
            self.cum_payoff = 0 
        
        return self.cum_payoff
    # Player starts in
    def initial_decision(self):
        return 1
    
    question_1 = models.IntegerField(
        label="What is the average payoff of the Value of IN",
        choices=[
            [1, 'x + 50'],
            [2, 'x - 50 '],
            [3, '0 '],
            [4, '100'],
            [5, '150'],
            [6, '200'],
        ])
     
    question_2 = models.IntegerField(
        label="If you select OUT, then you accumulate points according to ___________",
        choices=[
            [1, '0'],
            [2, 'x+100'],
            [3, 'x'],
            [4, 'a constant (92) depicted as horizontal line '],
            [5, 'a constant (100) depicted as horizontal line'],
            [6, 'None of above'],
        ])
        
    question_3 = models.IntegerField(
        label="If you switch from OUT to IN, can you switch again and go OUT? ",
        choices=[
            [1, 'Yes'],
            [2, 'No']
        ])
        
    question_4 = models.IntegerField(
        label="Does the current value of x affect the future value of x in the next period? ",
        choices=[
            [1, 'Yes'],
            [2, 'No']
        ])
        
        