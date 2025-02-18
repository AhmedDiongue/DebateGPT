DebateMate: AI-Powered Debate System

DebateMate is an advanced AI debate system that facilitates structured debates between two AI agents on configurable topics. The system includes real-time evaluation, fact-checking, and detailed argument analysis.

Features

- **Structured Debate Format**: Supports opening statements, multiple rebuttal rounds, and concluding arguments
- **Real-time Evaluation**: Comprehensive evaluation of arguments based on multiple criteria
- Fact-checking: Automated verification of factual claims
- **Argument Analysis**: Detailed tracking of key points, evidence, and argument progression
- **Logging**: Comprehensive logging of debate interactions and evaluations

Components

Core Classes

- `DebateModeration`: Orchestrates the debate, manages state, and coordinates agents
- `DebateAgent`: Represents individual debate participants with argument generation and analysis capabilities
- `DebateFoundation`: Handles LLM interactions and fact-checking
- `DebateLogger`: Manages logging of debate events and evaluations

Evaluation Framework

The system uses a comprehensive evaluation framework that assesses arguments across multiple dimensions:

1. Logical Structure
   - Argument coherence
   - Evidence quality

2. Engagement Quality
   - Rebuttal relevance
   - Counter-argument strength

3. Content Quality
   - Factual accuracy
   - Source credibility

4. Rhetorical Effectiveness
   - Persuasiveness
   - Clarity

5. Debate Ethics
   - Intellectual honesty
   - Fallacy avoidance

Usage

1. Configure the debate in main.py and then run the script:
```python
config = DebateConfig(
    topic="Should population control be part of world governments sustainability policy?",
    pro_position="Yes, population control should be part of world governments sustainability policy.",
    against_position="No, population control should not be part of world governments sustainability policy.",
    agent1_id="pro_agent",
    agent2_id="against_agent",
    rounds=3
)
```

Requirements

- Python 3.8+
- OpenAI API key
- Required packages:
  - openai
  - tenacity
  - python-dotenv

```
```

## Configuration

The system can be configured through the `DebateConfig` class, which includes:

- Model selection
- Temperature settings
- Token limits
- Number of debate rounds
- Custom agent personas

## Logging

Debates are logged in NDJSON format, including:
- Arguments and rebuttals
- Evaluations
- Fact-checking results
- Error events

