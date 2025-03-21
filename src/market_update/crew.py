from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from datetime import datetime
from dotenv import load_dotenv

import os

from .tools.search_tool import DuckDuckGoSearchTool

from .other_tools.slack_messenger import SlackMessenger

# from crewai_tools import ScraperDevTool

load_dotenv()


# Create a tool with explicit name, func, and description
search_tool = Tool(
    name="duckduckgo_search",
    func=DuckDuckGoSearchRun().run,
    description="Useful for searching the internet and finding relevant information about various topics"
)

@CrewBase
class LatestMarketNewsTrendCrew():
    """LatestMarketNewsTrendCrew crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    slack_channel = os.getenv("SLACK_CHANNEL", "#general")
    inputs = {}
    output_filename = None

    @before_kickoff
    def before_kickoff_function(self, inputs):
        print(f"************************** Before kickoff function with inputs: {inputs}")
        self.inputs = inputs
        return inputs

    @after_kickoff
    def after_kickoff_function(self, result):
        #print(f"************************************* After kickoff function with result: {result}")
        
        # Get the output_filename from the reporting task
        output_filename = None
        print("Before kickoff function: Checking for output file in tasks")

        for task in self.tasks:
            if hasattr(task, 'output_file') and task.output_file:
                output_filename = task.output_file
                break
        print("After kickoff function: output_filename = ", output_filename)
        
        # If we found an output file, send it to Slack
        if output_filename and os.path.exists(output_filename):
            print(f"After kickoff - found output file: {output_filename}")
            try:
                # Initialize our Slack messenger and send the report
                slack = SlackMessenger()
                slack.send_report(self.slack_channel, output_filename)
            except Exception as e:
                print(f"Error in Slack integration: {str(e)}")
        else:
            print("No output file found or file does not exist. Nothing sent to Slack.")
            
        return result

    @agent
    def researcher(self) -> Agent:
        print("************************** Creating researcher agent")
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            tools=[DuckDuckGoSearchTool()],
            max_rpm=10
        )

    @agent
    def reporting_analyst(self) -> Agent:
        print("************************** Creating reporting analyst agent")
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True,
            max_rpm=10
        )

    @task
    def research_task(self) -> Task:
        print("************************** Creating research task")
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def reporting_task(self) -> Task:
        print("************************** Creating reporting task")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"########### reporting_task -  INPUT: {self.inputs.get('stock_symbol')} ##############")

        output_filename = f'output/{self.inputs.get('stock_symbol')}_report_{timestamp}.md'

        self.output_filename = output_filename

        return Task(
            config=self.tasks_config['reporting_task'],
            output_file=output_filename
        )

    @crew
    def crew(self) -> Crew:
        print("************************** Creating the LatestMarketNewsTrendCrew crew")
        """Creates the LatestMarketNewsTrendCrew crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            output_log_file = "crew_run.log"
        )