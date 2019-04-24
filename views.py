from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, parse_config


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
            "all_pay_cash": self.player.set_cumpay()*self.session.config['real_world_currency_per_point']
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
    Decision,
    ResultsWaitPage,
    Results
]
