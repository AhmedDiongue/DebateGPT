from DebateAgent import DebateAgent
from DebateFoundation import DebateFoundation
from DebateOrchestration import DebateModeration
from DebateLogger import DebateLogger
from config import DebateConfig


def main():
    # Initialize configuration
    config = DebateConfig(
        topic="Should population control be part of world governments sustainability policy?",
        pro_position="Yes, population control should be part of world governments sustainability policy.",
        against_position="No, population control should not be part of world governments sustainability policy.",
        agent1_id="OpenAI #1",
        agent2_id="OpenAI #2"
    )

    # Initialize debate
    debate = DebateModeration(config)
    logger = DebateLogger()

    try:
        print("\n=== Debate Initialization ===")
        print(f"Topic: {config.topic}")
        print(f"Pro Position: {config.pro_position}")
        print(f"Against Position: {config.against_position}")

        print("\n=== Debate Begins ===")

        # Run debate rounds
        for round_result in debate.run_rounds():
            round_num = round_result['round']
            round_type = round_result['type']

            print(f"\n=== Round {round_num} ({round_type}) ===")
            print("\nPro Argument:")
            print(round_result['pro_argument'])
            print("\nAgainst Argument:")
            print(round_result['against_argument'])

            # Log round results
            logger.write_entry({
                'round': round_num,
                'type': round_type,
                'state': debate.get_debate_state().__dict__,
                'arguments': round_result
            })

        # Generate and display conclusions
        print("\n=== Concluding Arguments ===")
        conclusions = debate.conclusion()
        print("\nPro Conclusion:")
        print(conclusions['pro_argument'])
        print("\nAgainst Conclusion:")
        print(conclusions['against_argument'])

        # Log conclusions
        logger.write_entry({
            'type': 'conclusion',
            'state': debate.get_debate_state().__dict__,
            'arguments': conclusions
        })

    except Exception as e:
        logger.log_error("Debate execution", e)
        print(f"\nError occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()