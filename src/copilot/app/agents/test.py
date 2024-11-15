from swarm import Swarm, Agent
from swarm.repl import run_demo_loop

#from fak_eak import FAK_EAK_agent
#from orchestrator import orchestrator_agent

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = Swarm()

def transfer_back_to_orchestrator():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return orchestrator_agent

def transfer_to_fak_eak():
    return FAK_EAK_agent

def transfer_to_rag():
    return RAG_agent

def execute_rag():
    return "I am the RAG agent."

from functions import calculate_reduction_rate_and_supplement

FAK_EAK_agent = Agent(
    name="FAK-EAK Agent",
    instructions="You are a helpful and intelligent agent specialized in early retirement calculations such as reduction rate and pension supplement.",
    functions=[calculate_reduction_rate_and_supplement,
               transfer_back_to_orchestrator],
)

RAG_agent = Agent(
    name="RAG Agent",
    instructions="You are a helpful and intelligent agent specialized in general question answering.",
    functions=[execute_rag,
               transfer_back_to_orchestrator],
)

orchestrator_agent = Agent(
    name="Orchestrator triage Agent",
    instructions="Determine which agent is best suited to handle the user's request, and transfer the conversation to that agent.",
    functions=[transfer_to_fak_eak,
               transfer_to_rag],
)

if __name__ == "__main__":

    run_demo_loop(FAK_EAK_agent, debug=True)

    # params = {
    #     "date_of_birth": "1960-12-01",
    #     "retirement_date": "2026-12-01",
    #     "average_annual_income": "80200",
    # }

    # messages = [{"role": "user", "content": f"Calculate my reduction rate. I was born in on {params['date_of_birth']}, I plan to retire on {params['retirement_date']}, and my average annual income is {params['average_annual_income']}."}]

    # #messages = [{"role": "user", "content": f"quelle est la capitale de la france?"}]

    # response = client.run(agent=orchestrator_agent, messages=messages, debug=True)
    # print(response.messages[-1]["content"])
