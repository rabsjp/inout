from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, parse_config


class Decision(Page):
    def vars_for_template(self):
        return {
            "gameConstant": parse_config(self.session.config['config_file'])["game_constant"],        # Game constant to be determined by config file
            "treatment": parse_config(self.session.config['config_file'])["treatment"]       # Treatment to be decided by config file 
        }
    


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        pass


class Results(Page):
    pass


page_sequence = [
    Decision,
    ResultsWaitPage,
    Results
]
