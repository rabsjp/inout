from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class MyPage(Page):
    def vars_for_template(self):
        return {
            "gameConstant": 120,        # Game constant to be determined by config file
            "treatment": 'U',           # Treatment to be decided by config file
            "tickLength": 2000,         # Length of tick (Miliseconds) read in by config   
            "a_sto": .5,                # Stochastic value A read in by config   
            "s_sto": 60,                # Stochastic value S read in by config   
            "x_0": 0
        }
    


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        pass


class Results(Page):
    pass


page_sequence = [
    MyPage,
    ResultsWaitPage,
    Results
]
