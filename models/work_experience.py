from dataclasses import dataclass
from typing import List, Optional
from datetime import date, datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv


@dataclass
class STARDescription:
    situation: str  # Situation: The context or problem being addressed
    task: str  # Task: The responsibility or role the developer took on
    action: str  # Action: The steps taken to solve the problem or fulfill the task
    result: str  # Result: The outcome or impact of the developer's actions


@dataclass
class Project:
    project_name: str  # Name or identifier for the project
    description: STARDescription  # STAR-based description of the project
    technologies: List[str]  # Technologies used during the project
    achievements: List[str]  # Specific measurable accomplishments


@dataclass
class Mission:
    job_title: str  # Job title (e.g., Software Engineer)
    company_name: str  # Company name
    start_date: date  # Start date of the mission
    end_date: date  # End date of the mission (or 'Present')
    overall_summary: str  # High-level summary of the mission (optional)


@dataclass
class WorkExperience:
    mission: Mission  # Overall mission details (e.g., job title, company name)
    projects: List[Project]  # List of smaller projects within the mission

    @classmethod
    def _create_work_experiences_parser(cls):
        """Create a LangChain chain for parsing work experience information."""
        
        class STARModel(BaseModel, extra='forbid'):
            situation: str = Field(description="Context or background of the project/task")
            task: str = Field(description="Specific responsibility or challenge")
            action: str = Field(description="Steps taken to address the task")
            result: str = Field(description="Measurable outcomes and impacts")

        class ProjectModel(BaseModel):
            project_name: str = Field(description="Name of the project")
            description: STARModel = Field(description="STAR-format description of the project")
            technologies: List[str] = Field(description="Technologies and tools used")
            achievements: List[str] = Field(description="Measurable achievements and impacts")

        class MissionModel(BaseModel):
            job_title: str = Field(description="Job title/position")
            company_name: str = Field(description="Name of the company")
            start_date: str = Field(description="Start date in YYYY-MM-DD format")
            end_date: str = Field(description="End date in YYYY-MM-DD format")
            overall_summary: str = Field(description="High-level summary of the role")

        class WorkExperienceModel(BaseModel):
            mission: MissionModel = Field(description="Overall mission details")
            projects: List[ProjectModel] = Field(description="List of projects completed during the mission")

        class WorkExperienceListModel(BaseModel):
            work_experiences: List[WorkExperienceModel] = Field(description="List of work experiences")

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert at analyzing work experience in STAR format 
                (Situation, Task, Action, Result). Extract detailed work experience 
                information from the given text, ensuring each project is described 
                using the STAR method. Format all dates as YYYY-MM-DD.
                
                For each project:
                - Break down the description into STAR components
                - List specific technologies used
                - Include measurable achievements
                
                For the mission:
                - Extract precise dates
                - Create a concise overall summary
                - Identify the exact job title and company name
                """,
            ),
            (
                "human",
                """Work experience text:
                {text}
                """,
            ),
        ])

        # Setup the language model
        load_dotenv(".secrets")
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        ).with_structured_output(WorkExperienceListModel)

        return prompt | model

    @classmethod
    def from_text(cls, text: str) -> 'WorkExperience':
        """Extract work experience information from text."""
        # Create and use the parser
        chain = cls._create_work_experiences_parser()
        response = chain.invoke({"text": text})
        
        # Parse dates
        work_experiences = []
        for experience in response.work_experiences:
            print(experience)
            def parse_date(date_str: str) -> date:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
        
            # Create Mission instance
            mission = Mission(
                job_title=experience.mission.job_title,
                company_name=experience.mission.company_name,
                start_date=parse_date(experience.mission.start_date),
                end_date=parse_date(experience.mission.end_date),
                overall_summary=experience.mission.overall_summary
            )
        
            # Create Project instances
            projects = [
                Project(
                    project_name=proj.project_name,
                    description=STARDescription(
                        situation=proj.description.situation,
                        task=proj.description.task,
                        action=proj.description.action,
                        result=proj.description.result
                    ),
                    technologies=proj.technologies,
                    achievements=proj.achievements
                )
                for proj in experience.projects
            ]
            work_experiences.append(cls(mission=mission, projects=projects))
        
        return work_experiences


def test_work_experience():
    """Test the WorkExperience.from_text method with dummy data."""
    # Sample work experience text
    dummy_experience = """
    Senior Software Engineer
    TechCorp Solutions
    2021-01-15 to 2023-12-31
    
    Led the development of multiple high-impact projects while mentoring junior developers
    and implementing best practices across the team.
    
    Project: Cloud Migration Initiative
    We needed to modernize our legacy infrastructure to improve scalability.
    I was tasked with leading the migration of our monolithic application to a microservices architecture.
    I designed the microservices architecture, implemented containerization using Docker, and orchestrated 
    the deployment using Kubernetes on AWS.
    The migration resulted in 40% improved system performance, 60% reduced deployment time, 
    and 30% cost savings in infrastructure.
    
    Technologies: AWS, Docker, Kubernetes, Python, Terraform
    Achievements:
    - Reduced system latency by 40%
    - Achieved 99.99% uptime after migration
    - Decreased deployment time from 2 hours to 20 minutes
    
    Project: Analytics Dashboard Redesign
    The existing dashboard was slow and difficult to maintain.
    I was responsible for rebuilding the analytics dashboard to improve performance and user experience.
    I implemented a React frontend with server-side rendering, optimized database queries, 
    and introduced caching mechanisms.
    The new dashboard handled 3x more concurrent users and reduced page load time by 65%.
    
    Technologies: React, Node.js, PostgreSQL, Redis
    Achievements:
    - Increased dashboard response speed by 65%
    - Reduced customer complaints by 80%
    - Implemented real-time analytics processing
    """
    
    try:
        # Create work experience instance from text
        work_exp = WorkExperience.from_text(dummy_experience)[0]
        
        # Test mission details
        assert work_exp.mission.job_title == "Senior Software Engineer", \
            f"Expected 'Senior Software Engineer', got {work_exp.mission.job_title}"
        assert work_exp.mission.company_name == "TechCorp Solutions", \
            f"Expected 'TechCorp Solutions', got {work_exp.mission.company_name}"
        assert work_exp.mission.start_date == date(2021, 1, 15), \
            f"Expected date(2021, 1, 15), got {work_exp.mission.start_date}"
        
        # Test projects
        assert len(work_exp.projects) >= 2, \
            f"Expected at least 2 projects, got {len(work_exp.projects)}"
        
        # Test first project details
        project = work_exp.projects[0]
        assert project.project_name == "Cloud Migration Initiative", \
            f"Expected 'Cloud Migration Initiative', got {project.project_name}"
        assert len(project.technologies) >= 4, \
            f"Expected at least 4 technologies, got {len(project.technologies)}"
        assert len(project.achievements) >= 3, \
            f"Expected at least 3 achievements, got {len(project.achievements)}"
        
        # Test STAR description
        assert all(hasattr(project.description, attr) for attr in ['situation', 'task', 'action', 'result']), \
            "Project description missing STAR components"
        
        print("✅ All work experience tests passed successfully!")
        return work_exp  # Return for manual inspection if needed
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    import asyncio
    
    # Run the test
    asyncio.run(test_work_experience())
