from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, parse_config
import math

class Introduction(Page):

    def is_displayed(self):
        return self.round_number == 1
    
    def vars_for_template(self):
        return {
            'instructions_link': self.session.config['instructions_link'],
        }
    
class Questions(Page):
    def is_displayed(self):
        return self.round_number == 1
        
    form_model = 'player'
    form_fields = [
        'question_1','question_2','question_3','question_4'
    ]
    
    def error_message(self, values):
        print('your answer is ', values)
        if values["question_1"]  !=4 or values["question_2"]  !=4  or values["question_3"]  !=1 or values["question_4"]  !=1:
            return 'Fix your answers'
    
class InitialWaitPage(WaitPage):

    def is_displayed(self):
        return self.round_number ==1
    
class Decision(Page):

    def is_displayed(self):
        return self.round_number <= self.group.num_rounds()

    def vars_for_template(self):
        return {
            "gameConstant": self.group.game_constant(), # Game constant to be determined by config file
            "treatment": self.group.treatment(),        # Treatment to be decided by config file 
        }
    

class ResultsWaitPage(WaitPage):

    def is_displayed(self):
        return self.round_number <= self.group.num_rounds()


class Results(Page):
    def is_displayed(self):
        return self.round_number <= self.group.num_rounds()
     
    def vars_for_template(self):
        
        
        return {
            "cumulative_pay": self.player.get_payoff(),
             "all_pay": self.player.set_cumpay(),
            "all_pay_cash": math.floor(self.player.set_cumpay()*self.session.config['real_world_currency_per_point'])
        }

def get_output_table_header(groups):
    header = [
        'session_id',
        'round_number',
        'group_num',
        'tick',
        'x_t'
    ]
    for player in groups[0].get_players():
        header.append('p{}_decision'.format(player.id_in_group))

    return header

def get_output_table(events):
    if not events:
        return []
    group = events[0].group
    players = group.get_players()
    rows = []
    tick = 1
    for event in events:
        if event.channel != 'tick':
            continue
        row = [
            group.session.code,
            group.round_number,
            group.id_in_subsession,
            tick,
            next(iter(event.value.values()))['x_t'],
        ]
        for player in players:
            row.append(event.value[player.participant.code]['decision'])
        tick += 1
        rows.append(row)
    return rows


page_sequence = [
    Introduction,
    Questions,
    InitialWaitPage,
    Decision,
    ResultsWaitPage,
    Results
]
