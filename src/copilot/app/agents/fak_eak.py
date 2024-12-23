# see https://www.eak.admin.ch/eak/fr/home/dokumentation/pensionierung/reform-ahv21/kuerzungssaetze-bei-vorbezug.html
# see

from swarm import Agent

from tools import (
    calculate_reduction_rate_and_supplement,
    transfer_back_to_orchestrator,
)

FAK_EAK_agent = Agent(
    name="FAK-EAK Agent",
    instructions="You are a helpful and intelligent agent specialized in early retirement calculations.",
    functions=[
        calculate_reduction_rate_and_supplement,
        transfer_back_to_orchestrator,
    ],
)
