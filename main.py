from DebateAgent import DebateAgent
from DebateFoundation import DebateFoundation
from DebateOrchestration import DebateModeration
from DebateLogger import DebateLogger

def main():
    #initialize foundation variables
    logger = DebateLogger()
    topic = "Should population control be part of world governments sustainability policy?" 
    pro_position = "Yes, population control should be part of world governments sustainability policy."
    against_position = "No, population control should not be part of world governments sustainability policy."
    agentid_1 = "OpenAI #1"
    agentid_2 = "OpenAI #2"
    persona = "You are a logical, intellectually honest, and truth-seeking academic scholar. A frequent and passionate debater, you are disciplined in rigorous \
    reasoning. Your expertise spans environmental science, economics, political philosophy, bioethics, and public policy. You are strong-minded in your view, but you\
    reject ideological bias in favor of evidence-based, nuanced discourse."  
    pro_context_gathering_prompt = f"Use all of the resources at your disposal to generate a 2-page sheet of information that will serve as context for your argument. \
    Do not formally state your argument at this point. Simply gather the resources/information that you would use to evaluate and substantiate an argument for your assigned debate position ({pro_position})"
    against_context_gathering_prompt = f"Use all of the resources at your disposal to generate a 2-page sheet of information that will serve as context for your argument. \
    Do not formally state your argument at this point. Simply gather the resources/information that you would use to evaluate and substantiate an argument for your assigned debate position ({against_position})"
    #initialize debater context instance
    context_instance = DebateFoundation()
    pro_context = context_instance.query_llm(pro_context_gathering_prompt)
    against_context = context_instance.query_llm(against_context_gathering_prompt)
    #initialize Debate Moderator instance and debate agents
    Debate = DebateModeration(topic, persona, pro_context, against_context, pro_position, against_position, agentid_1, agentid_2)
    agent1_initialize = Debate.pro_agent.intialization_conf()
    agent2_initialize = Debate.pro_agent.intialization_conf()
    print(agent1_initialize)
    logger.write_entry(agent1_initialize)
    print(agent2_initialize)
    logger.write_entry(agent2_initialize)

#initialization confirmation
    print("\n=== Debate Initialization ===")
    print(f"Pro Agent Initialization: {Debate.pro_agent.intialization_conf()}")
    print(f"Against Agent Initialization: {Debate.against_agent.intialization_conf()}")

    # debate rounds w/ print results
    print("\n=== Debate Begins ===")
    for round_data in Debate.run_rounds():
        for round_name, arguments in round_data.items():
            print(f"\n{round_name}:")
            for speaker, argument in arguments.items():
                print(f"{speaker}: {argument}")

    # conclusion
    print("\n=== Debate Conclusion ===")
    for conclusion_data in Debate.conclusion():
        for conclusion_name, arguments in conclusion_data.items():
            print(f"\n{conclusion_name}:")
            for speaker, argument in arguments.items():
                print(f"{speaker}: {argument}")

if __name__ == "__main__":
    main()