from typing import List, Optional
from dataclasses import dataclass
from datetime import date, datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import os

@dataclass
class ExperienceRequirement:
    years_of_experience: int  # Minimum years of experience required
    relevant_experiences: List[
        str
    ]  # Specific types of experience required (e.g., "experience with large-scale web applications")


@dataclass
class JobRequirements:
    hard_skills: List[str]  # Required technical skills (e.g., Python, React)
    soft_skills: List[str]  # Required soft skills (e.g., teamwork, communication)
    education_level: str  # Minimum education level required (e.g., Bachelor's)
    certifications: List[
        str
    ]  # Certifications required or preferred (e.g., AWS Certified)
    experience: ExperienceRequirement  # Experience requirements
    languages: List[str]  # Languages required and proficiency levels (if applicable)
    other_conditions: List[
        str
    ]  # Additional conditions (e.g., availability to travel, specific legal requirements)


def _create_job_offer_parser():
    """Create a LangChain chain for parsing developer information."""
    # Define the Pydantic models for structured output
    class ExperienceRequirementModel(BaseModel, extra="forbid"):
        years_of_experience: int = Field(description="Minimum years of experience required")
        relevant_experiences: List[str] = Field(description="Specific types of experience required (e.g., 'experience with large-scale web applications')")

    class JobRequirementsModel(BaseModel):
        hard_skills: List[str] = Field(description="Required technical skills (e.g., Python, React)")
        soft_skills: List[str] = Field(description="Required soft skills (e.g., teamwork, communication)")
        education_level: str = Field(description="Minimum education level required (e.g., Bachelor's)")
        certifications: List[str] = Field(description="Certifications required or preferred (e.g., AWS Certified)")
        experience: ExperienceRequirementModel = Field(description="Experience requirements")
        languages: List[str] = Field(description="Languages required and proficiency levels (if applicable)")
        other_conditions: List[str] = Field(description="Additional conditions (e.g., availability to travel, specific legal requirements)")

    class JobOfferModel(BaseModel):
        job_title: str = Field(description="Title of the job (e.g., Software Engineer)")  # Title of the job (e.g., Software Engineer)
        company_name: str = Field(description="Name of the hiring company")  # Name of the hiring company
        location: str = Field(description="Job location (e.g., city, remote, hybrid)")  # Job location (e.g., city, remote, hybrid)
        employment_type: str = Field(description="Employment type (e.g., Full-time, Part-time, Contract)")  # Employment type (e.g., Full-time, Part-time, Contract)
        description: str = Field(description="Full job description text")  # Full job description text
        requirements: JobRequirements = Field(description="Detailed requirements and qualifications") # Detailed requirements and qualifications
        perks: List[str] = Field(description="List of benefits and perks offered by the job")  # List of benefits and perks offered by the job
        application_deadline: str = Field(description="Optional deadline for applications (if provided)")  # Optional deadline for applications (if provided)
    

    prompt = ChatPromptTemplate.from_messages(
    [
            (
            "system",
            """You are an expert Job offer parser. Extract the Job offer information from the following Job offer text. 
            """,
            ),
            (
                "human",
                """Job offer text:
                {text}
                """,
            ),
        ]
    )

    # Setup the language model
    if "OPENAI_API_KEY" not in os.environ:
        load_dotenv(".secrets")
    model = ChatOpenAI(
        model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(JobOfferModel)
    return prompt | model


@dataclass
class JobOffer:
    job_title: str  # Title of the job (e.g., Software Engineer)
    company_name: str  # Name of the hiring company
    location: str  # Job location (e.g., city, remote, hybrid)
    employment_type: str  # Employment type (e.g., Full-time, Part-time, Contract)
    description: str  # Full job description text
    requirements: JobRequirements  # Detailed requirements and qualifications
    perks: List[str]  # List of benefits and perks offered by the job
    application_deadline: date  # Optional deadline for applications (if provided)
    
    @classmethod
    def from_text(cls, text: str) -> 'JobOffer':
        """Extract job offer information from text using LangChain."""
        # Generate the final prompt
        chain = _create_job_offer_parser()
        
        # Get the response
        response = chain.invoke({"text": text})

        experience_requirement = ExperienceRequirement( 
            years_of_experience=response.requirements.experience.years_of_experience,
            relevant_experiences=response.requirements.experience.relevant_experiences
        )
        job_requirements = JobRequirements(
            hard_skills=response.requirements.hard_skills,
            soft_skills=response.requirements.soft_skills,
            education_level=response.requirements.education_level,
            certifications=response.requirements.certifications,
            experience=experience_requirement,
            languages=response.requirements.languages,
            other_conditions=response.requirements.other_conditions
        )
            
        # Create and return JobOffer instance
        return cls(
            job_title=response.job_title,
            company_name=response.company_name,
            location=response.location,
            employment_type=response.employment_type,
            description=response.description,
            requirements=job_requirements,
            perks=response.perks,
            application_deadline=response.application_deadline  
        )


if __name__ == "__main__":
    # Test job offer text
    test_job_offer = """
    Senior Software Engineer
    Company: TechCorp Solutions
    Location: San Francisco, CA (Hybrid)
    
    About the Role:
    We're seeking an experienced Senior Software Engineer to join our growing team. The ideal candidate will help lead development of our core platform services.
    
    Requirements:
    - 5+ years of experience in software development
    - Expert in Python and JavaScript
    - Experience with cloud services (AWS/Azure)
    - Strong background in distributed systems
    - Bachelor's degree in Computer Science or related field
    - AWS certification preferred
    - Fluent in English, Spanish is a plus
    
    Soft Skills:
    - Strong communication and leadership abilities
    - Problem-solving mindset
    - Team player with mentoring experience
    
    What We Offer:
    - Competitive salary
    - Health and dental insurance
    - 401(k) matching
    - Flexible work hours
    - Professional development budget
    
    Employment Type: Full-time
    Application Deadline: 2024-12-31
    """
    
    try:
        # Test the parser
        job_offer = JobOffer.from_text(test_job_offer)
        
        # Print the parsed results
        print("\nParsed Job Offer:")
        print(f"Title: {job_offer.job_title}")
        print(f"Company: {job_offer.company_name}")
        print(f"Location: {job_offer.location}")
        print(f"Type: {job_offer.employment_type}")
        print("\nRequirements:")
        print(f"- Hard Skills: {', '.join(job_offer.requirements.hard_skills)}")
        print(f"- Soft Skills: {', '.join(job_offer.requirements.soft_skills)}")
        print(f"- Education: {job_offer.requirements.education_level}")
        print(f"- Experience: {job_offer.requirements.experience.years_of_experience} years")
        print(f"- Relevant Experience: {', '.join(job_offer.requirements.experience.relevant_experiences)}")
        print(f"- Certifications: {', '.join(job_offer.requirements.certifications)}")
        print(f"- Languages: {', '.join(job_offer.requirements.languages)}")
        print("\nPerks:")
        print(f"- {', '.join(job_offer.perks)}")
        print(f"\nDeadline: {job_offer.application_deadline}")
        
    except Exception as e:
        print(f"Error parsing job offer: {str(e)}")




