from DebateAgent import DebateAgent, DebateFoundation
from DebateFoundation import DebateLogger

class DebateModeration:
    def __init__(self, topic, persona, pro_context, against_context, pro_position, against_position, agentid_1, agentid_2):
        self.topic = topic
        self.pro_agent = DebateAgent(agentid_1, pro_context, pro_position, persona)
        self.against_agent = DebateAgent(agentid_2, against_context, against_position, persona)
        self.round=0

    def run_rounds(self):
        #pro intro argument
        pro_opening_argument = self.pro_agent.return_introduction(self.topic)
        #against intro argument (w/ context of pro's intro argument)
        against_opening_argument = self.against_agent.return_introduction(self.topic, pro_opening_argument)

        pro_last_argument = pro_opening_argument
        against_last_argument = against_opening_argument
        yield {
                "opening argument for pro agent": pro_opening_argument, 
                "\n\nopening argument for against agent": against_opening_argument
        }
        for _ in range(3):
            self.round +=1 
            pro_rebuttal_argument = self.pro_agent.return_rebuttal(against_last_argument)
            against_rebuttal_argument = self.against_agent.return_rebuttal(pro_rebuttal_argument)
            against_last_argument = against_rebuttal_argument

            yield {
                f'Round {self.round}': {f"{self.pro_agent.agentid}'s argument": pro_rebuttal_argument, 
            f"\n\n{self.against_agent.agentid}'s argument": against_rebuttal_argument}
            }
    def conclusion(self): 
            pro_argument_conclusion = self.pro_agent.return_conclusion()
            against_argument_conclusion = self.against_agent.return_conclusion()

            yield {
                 f'Concluding Arguments': {f"{self.pro_agent.agentid}'s argument": pro_argument_conclusion, 
            f"\n\n{self.against_agent.agentid}'s argument": against_argument_conclusion}
            }


    
     





