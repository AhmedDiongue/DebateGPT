from DebateFoundation import DebateFoundation

class DebateAgent:
    def __init__(self, agentid, memory, position, persona):
        self.agentid = agentid
        self.context = memory
        self.position = position
        self.persona = persona
        self.opponent_arguments = []
        self.foundation = DebateFoundation()
    def intialization_conf(self):
        return f"{self.agentid} has been intializated with the following position: {self.position}"
    def return_introduction(self, topic: str, opponent_argument=None):
        if opponent_argument:
            prompt = f"""
            [ROLE] Your guiding goal is to debate the {self.position} position for the topic provided below. 
            [STYLE] {self.persona}
            [CONTEXT] {self.context}
            [OPPONENT INTRODUCTION ARGUMENT] {opponent_argument}
            [TASK] Hello, {self.agentid}. Create a 2 paragraph opening argument according to your role for the following topic: {topic}. You may reason and posit regarding your opponent's
            introduction argument as shown above in your argument if you believe it maximizes your ability to convey a logical, influential opening argument. 
            """
            return self.foundation.query_llm(prompt)
        else: 
            prompt = f"""
            [ROLE] Your guiding goal is to debate the {self.position} position for the topic provided below. 
            [STYLE] {self.persona}
            [CONTEXT] {self.context}
            [TASK] Hello, {self.agentid}. Create a 2 paragraph opening argument according to your role for the following topic: {topic}. 
            """
            return self.foundation.query_llm(prompt)

    def return_rebuttal(self, opponent_argument: str): # later think of storing rebuttal reasoning as context and then conjoin all that to the self.context
        opponent_argument_num = 1
        self.opponent_arguments.append({f"opponent argument #{opponent_argument_num}: {opponent_argument}"})
        prompt = f"""
        [ROLE] Your guiding role is to debate the {self.position} position for the topic provided below. 
        [PERSONA] {self.persona}
        [CONTEXT] {self.context}
        [OPPONENT CONTENTIONS] {self.opponent_arguments}
        [TASK] Okay, {self.agentid}, you must now create a 2 paragraph maximum rebuttal argument for your opponent's contention provided above. First formulate a position on the flaws and merits of your opponents arguments using \
        sound and intellectually honest logical reasoning. Then formulate a position on their argument and produce your own reasoned response. Make sure that ultimately your reasoning leads towards your support of the position that {self.position}. Use \
        the context from the debate thus far as you see fit, and with respect to your PERSONA. 
        """
        opponent_argument_num += 1
        return self.foundation.query_llm(prompt)

    def return_conclusion(self):
        prompt = f"""
        [ROLE] Your guiding goal is to {self.position} position for the topic provided below. 
        [PERSONA] {self.persona}
        [CONTEXT] {self.context}
        [OPPONENT CONTENTIONS] {self.opponent_arguments}
        [TASK] Okay, {self.agentid}, you must now create a 3 paragraph concluding argument for your position: {self.position}. Please use the CONTEXT that has been collected \
            throughout the argument from both sides, alongside your persona, in the crafting of your final concluding argument. Be sure to drive home why your arguments to this point should prevail \
            compared to the contentions presented by your opponent, if at all.
        """
        return self.foundation.query_llm(prompt)
