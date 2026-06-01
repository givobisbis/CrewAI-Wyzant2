import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task







@CrewBase
class WyzantTutoringResponseGeneratorCrew:
    """WyzantTutoringResponseGenerator crew"""

    
    @agent
    def wyzant_ad_analyst(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["wyzant_ad_analyst"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    
    @agent
    def wyzant_response_copywriter_for_bruno(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["wyzant_response_copywriter_for_bruno"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    
    @agent
    def wyzant_response_quality_controller(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["wyzant_response_quality_controller"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="anthropic/claude-sonnet-4-20250514",
                
                
            ),
            
        )
        
    
    @agent
    def wyzant_response_error_memory_bank(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["wyzant_response_error_memory_bank"],
            
            
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    

    
    @task
    def load_error_memory(self) -> Task:
        return Task(
            config=self.tasks_config["load_error_memory"],
            markdown=False,
            
            
        )
    
    @task
    def analyze_the_wyzant_ad(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_the_wyzant_ad"],
            markdown=False,
            
            
        )
    
    @task
    def draft_the_response(self) -> Task:
        return Task(
            config=self.tasks_config["draft_the_response"],
            markdown=False,
            
            
        )
    
    @task
    def verify_and_validate_the_response(self) -> Task:
        return Task(
            config=self.tasks_config["verify_and_validate_the_response"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the WyzantTutoringResponseGenerator crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,

            chat_llm=LLM(model="openai/gpt-4o-mini"),
        )


