from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class MyPage(Page):
    def vars_for_template(self):
        return {
            "data": [
                [0,1],
                [1,2],
                [2,3],
                [3,4],
                [4,5],
                [5,6],
                [6,7],
                [7,8],
                [8,9],
                [9,10]
            ],
            "gameConstant": 120, # Game constant to be determined by config file
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
