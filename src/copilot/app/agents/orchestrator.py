from swarm import Agent

from functions import transfer_to_fak_eak

orchestrator_agent = Agent(
    name="Orchestrator triage Agent",
    instructions="Determine which agent is best suited to handle the user's request, and transfer the conversation to that agent.",
    functions=[transfer_to_fak_eak],
)