#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from market_update.crew import LatestMarketNewsTrendCrew
#from crew import LatestMarketNewsTrendCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'stock_symbol': 'NVS',
        'current_datetime': str(datetime.now())
    }
    print("********* MAIN - *********")
    try:
        LatestMarketNewsTrendCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == "__main__":
    print("********* MAIN - OUTSIDE *********")
    run()
    print("*********AFTER RUN -- MAIN - OUTSIDE *********")
