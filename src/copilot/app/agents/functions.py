import logging

from datetime import date
from dateutil.relativedelta import relativedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#from fak_eak import FAK_EAK_agent
#from orchestrator import orchestrator_agent

# ORCHESTRATOR
# def transfer_back_to_orchestrator():
#     """Call this function if a user is asking about a topic that is not handled by the current agent."""
#     return orchestrator_agent

# def transfer_to_fak_eak():
#     return FAK_EAK_agent

# FAK-EAK
def calculate_reduction_rate_and_supplement(date_of_birth, retirement_date, average_annual_income):
    """
    Calculate the reduction rate or pension supplement for women of the transitional generation.

    Parameters:
    - date_of_birth (datetime.date): The birth date of the woman (should be between 1961 and 1969).
    - retirement_date (datetime.date): The planned retirement date.
    - average_annual_income (float): The average annual income in CHF.

    Returns:
    - str: A message indicating the reduction rate or the supplement amount.
    - str: A message if the inputs do not meet the eligibility criteria, with a link for more information.
    """
    date_of_birth = date.fromisoformat(date_of_birth)
    retirement_date = date.fromisoformat(retirement_date)
    average_annual_income = float(average_annual_income)

    # Get the year of birth
    year_of_birth = date_of_birth.year

    # Check if the woman is part of the transitional generation
    if not (1961 <= year_of_birth <= 1969):
        logger.info("------NOT ELIGIBLE")
        return "You do not meet the eligibility criteria. For more information, please visit: [Taux de réduction favorable en cas d’anticipation de la rente](https://www.eak.admin.ch/eak/fr/home/dokumentation/pensionierung/reform-ahv21/kuerzungssaetze-bei-vorbezug.html)"

    # Calculate the age at retirement in years and months
    age_delta = relativedelta(retirement_date, date_of_birth)
    age_years = age_delta.years
    age_months = age_delta.months
    age_total_months = age_years * 12 + age_months

    # Reference ages for each year of birth (in months)
    reference_ages_months = {
        1961: (64 * 12) + 3,   # 64 years + 3 months
        1962: (64 * 12) + 6,   # 64 years + 6 months
        1963: (64 * 12) + 9,   # 64 years + 9 months
        1964: 65 * 12,         # 65 years
        1965: 65 * 12,         # 65 years
        1966: 65 * 12,         # 65 years
        1967: 65 * 12,         # 65 years
        1968: 65 * 12,         # 65 years
        1969: 65 * 12,         # 65 years
    }

    reference_age_months = reference_ages_months[year_of_birth]

    # Determine income bracket and base supplement
    if average_annual_income <= 58800:
        income_bracket = 1
        base_supplement = 160
    elif 58801 <= average_annual_income <= 73500:
        income_bracket = 2
        base_supplement = 100
    elif average_annual_income >= 73501:
        income_bracket = 3
        base_supplement = 50
    else:
        logger.info("------INVALID INCOME")
        return ("The provided income is invalid. "
                "Please ensure the income is in the correct range.")

    # Check if retiring at or after the reference age
    if age_total_months >= reference_age_months:
        # Pension supplement percentages based on year of birth
        supplement_percentages = {
            1961: 25,
            1962: 50,
            1963: 75,
            1964: 100,
            1965: 100,
            1966: 81,
            1967: 63,
            1968: 44,
            1969: 25,
        }
        percentage = supplement_percentages[year_of_birth]
        supplement = base_supplement * (percentage / 100)
        logger.info("------PENSION SUPPLEMENT")
        return f"Your pension supplement is {supplement:.2f} CHF per month."
    else:
        # Calculate anticipation months
        anticipation_months = reference_age_months - age_total_months

        # Convert anticipation months to anticipation years
        anticipation_years = anticipation_months / 12

        # Round anticipation years to nearest integer
        anticipation_years_int = int(round(anticipation_years))

        if anticipation_years_int not in [1, 2, 3]:
            logger.info("------INVALID ANTICIPATION YEARS")
            return ("The person does not meet the eligibility criteria for an early retirement reduction. "
                    "For more information, please visit: "
                    "https://www.eak.admin.ch/eak/fr/home/dokumentation/pensionierung/reform-ahv21/kuerzungssaetze-bei-vorbezug.html")

        # Reduction rates table
        reduction_rates = {
            1: {1: 0.0, 2: 2.5, 3: 3.5},    # 1 year anticipation
            2: {1: 2.0, 2: 4.5, 3: 6.5},    # 2 years anticipation
            3: {1: 3.0, 2: 6.5, 3: 10.5},   # 3 years anticipation
        }

        # Retrieve the reduction rate
        reduction_rate = reduction_rates[anticipation_years_int][income_bracket]
        logger.info("------REDUCTION RATE")
        return f"Your reduction rate is {reduction_rate}%."

def calculate_reference_age():
    pass

def determine_parent_receiving_child_benefits():
    pass