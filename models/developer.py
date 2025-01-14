import os
from typing import List, Optional
from dataclasses import dataclass
from datetime import date, datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from .work_experience import WorkExperience

@dataclass
class Levels:
    Basic: str = "Basic"
    Intermediate: str = "Intermediate"
    Advanced: str = "Advanced"
    Expert: str = "Expert"

@dataclass
class ContactInfo:
    email: str  # Email address
    phone: str  # Phone number
    address: str  # Physical address (optional)


@dataclass
class Skill:
    name: str  # Name of the skill (e.g., Python, React)
    level: Levels   # Proficiency level (e.g., Beginner, Intermediate, Advanced, Expert)


@dataclass
class Education:
    institution_name: str  # Name of the institution
    degree: str  # Degree or certification earned
    field_of_study: str  # Major or area of study
    start_date: date  # Start date
    end_date: date  # End date


@dataclass
class Certification:
    name: str  # Name of the certification
    issuing_organization: str  # Organization that issued the certification
    issue_date: date  # Date of issuance
    expiration_date: date  # Expiration date (optional)


@dataclass
class Language:
    name: str  # Language name (e.g., English, French)
    proficiency: str  # Proficiency level (e.g., Native, Fluent, Intermediate)


@dataclass
class Achievement:
    title: str  # Title of the achievement
    description: str  # Brief description of the achievement


@dataclass
class JobPreferences:
    job_title: str  # Preferred job title
    location: str  # Preferred location
    employment_type: str  # Full-time, Part-time, Contract, etc.
    remote_work: bool  # Open to remote work
    salary_expectation: str  # Salary expectation (e.g., range or "Negotiable")
    other_conditions: List[
        str
    ]  # Additional conditions (e.g., work-life balance, benefits)


def _create_developer_parser():
    """Create a LangChain chain for parsing developer information."""
    # Define the Pydantic models for structured output
    class LevelsModel(BaseModel, extra='forbid'):
        level: str = Field(description="Proficiency level (Basic/Intermediate/Advanced/Expert)")

    class LanguageLevelsModel(BaseModel, extra='forbid'):
        level: str = Field(description="Proficiency level (Basic/Intermediate/Fluent/Native)")

    class SkillModel(BaseModel):
        name: str = Field(description="Name of the skill")
        level: LevelsModel

    class ContactModel(BaseModel):
        email: str = Field(description="Email address")
        phone: str = Field(description="Phone number")
        address: str = Field(description="Physical address")

    class EducationModel(BaseModel):
        institution_name: str = Field(description="Name of the educational institution")
        degree: str = Field(description="Degree or certification earned")
        field_of_study: str = Field(description="Major or area of study")
        start_date: str = Field(description="Start date in YYYY-MM-DD format")
        end_date: str = Field(description="End date in YYYY-MM-DD format")

    class CertificationModel(BaseModel):
        name: str = Field(description="Name of the certification")
        issuing_organization: str = Field(description="Organization that issued the certification")
        issue_date: str = Field(description="Issue date in YYYY-MM-DD format")
        expiration_date: Optional[str] = Field(description="Expiration date in YYYY-MM-DD format if applicable")

    class LanguageModel(BaseModel):
        name: str = Field(description="Language name")
        proficiency: LanguageLevelsModel 

    class AchievementModel(BaseModel):
        title: str = Field(description="Title of the achievement")
        description: str = Field(description="Brief description of the achievement")

    class DeveloperModel(BaseModel):
        name: str = Field(description="Full name of the developer")
        contact_info: ContactModel = Field(description="Contact information")
        linkedin_url: str = Field(description="LinkedIn profile URL")
        github_url: str = Field(description="GitHub profile URL")
        website_url: Optional[str] = Field(description="Personal website URL")
        professional_summary: str = Field(description="Professional summary")
        technical_skills: List[SkillModel] = Field(description="List of technical skills")
        soft_skills: List[str] = Field(description="List of soft skills")
        education: List[EducationModel] = Field(description="List of educational qualifications")
        certifications: List[CertificationModel] = Field(description="List of certifications")
        languages: List[LanguageModel] = Field(description="List of languages with proficiency")
        achievements: List[AchievementModel] = Field(description="List of achievements")
        hobbies: List[str] = Field(description="List of hobbies and interests")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert resume parser. Extract the developer information from the following resume text. 
        """,
            ),
            (
                "human",
                 """Resume text:
                 {text}
        """,
            ),
        ]
    )

    # Setup the language model
    load_dotenv(".secrets")
    model = ChatOpenAI(
            model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(DeveloperModel)

    return prompt | model

@dataclass
class Developer:
    # Personal information
    name: str  # Full name
    contact_info: ContactInfo  # Contact details
    linkedin_url: str  # LinkedIn profile URL
    github_url: str  # GitHub or portfolio URL
    website_url: str  # Personal website or blog (optional)

    # Professional summary
    professional_summary: str  # Short summary highlighting key skills and career goals

    # Skills and expertise
    technical_skills: List[Skill]  # List of technical skills with proficiency level
    soft_skills: List[str]  # List of soft skills

    # Work experience
    work_experiences: List[WorkExperience]  # Detailed list of past jobs and projects

    # Education
    education: List[Education]  # List of educational qualifications

    # Certifications
    certifications: List[Certification]  # List of certifications

    # Languages
    languages: List[Language]  # List of spoken languages with proficiency level

    # Awards & Achievements
    achievements: List[Achievement]  # Notable awards or recognitions

    # Hobbies and interests
    hobbies: List[str]  # Optional hobbies or personal interests

    # Job preferences (used for tailoring)
    job_preferences: JobPreferences  # Preferred job type, location, etc.

    @classmethod
    def from_text(cls, text: str) -> 'Developer':
        """Extract developer information from text using LangChain."""
        # Generate the final prompt
        chain = _create_developer_parser()
        
        # Get the response
        response = chain.invoke({"text": text})
        
        # Convert response data to Developer class format
        contact_info = ContactInfo(
            email=response.contact_info.email,
            phone=response.contact_info.phone,
            address=response.contact_info.address
        )
        
        technical_skills = [
            Skill(name=skill.name, level=skill.level)
            for skill in response.technical_skills
        ]
        
        education_list = [
            Education(
                institution_name=edu.institution_name,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                start_date=datetime.strptime(edu.start_date, "%Y-%m-%d").date(),
                end_date=datetime.strptime(edu.end_date, "%Y-%m-%d").date()
            )
            for edu in response.education
        ]
        
        certifications_list = [
            Certification(
                name=cert.name,
                issuing_organization=cert.issuing_organization,
                issue_date=datetime.strptime(cert.issue_date, "%Y-%m-%d").date(),
                expiration_date=datetime.strptime(cert.expiration_date, "%Y-%m-%d").date() if cert.expiration_date else None
            )
            for cert in response.certifications
        ]
        
        languages_list = [
            Language(name=lang.name, proficiency=lang.proficiency)
            for lang in response.languages
        ]
        
        achievements_list = [
            Achievement(title=ach.title, description=ach.description)
            for ach in response.achievements
        ]
        
        # Create a default JobPreferences since it's not in the parsed data
        job_preferences = JobPreferences(
            job_title="",
            location="",
            employment_type="Full-time",
            remote_work=True,
            salary_expectation="Negotiable",
            other_conditions=[]
        )
        
        return cls(
            name=response.name,
            contact_info=contact_info,
            linkedin_url=response.linkedin_url,
            github_url=response.github_url,
            website_url=response.website_url or "",
            professional_summary=response.professional_summary,
            technical_skills=technical_skills,
            soft_skills=response.soft_skills,
            work_experiences=[],  # Work experiences are not included in the parser
            education=education_list,
            certifications=certifications_list,
            languages=languages_list,
            achievements=achievements_list,
            hobbies=response.hobbies,
            job_preferences=job_preferences
        )

def test_from_text():
    """Test the from_text method with dummy resume data."""
    # Sample resume text
    dummy_resume = """
    John Doe
    Software Engineer
    Email: john.doe@email.com
    Phone: (555) 123-4567
    Address: 123 Tech Street, Silicon Valley, CA
    
    LinkedIn: https://linkedin.com/in/johndoe
    GitHub: https://github.com/johndoe
    Website: https://johndoe.dev
    
    Professional Summary:
    Experienced software engineer with 5 years of expertise in full-stack development. 
    Passionate about creating scalable web applications and mentoring junior developers.
    
    Education:
    - Master of Science in Computer Science
      Stanford University
      2018-09-01 to 2020-06-15
    
    - Bachelor of Science in Software Engineering
      MIT
      2014-09-01 to 2018-05-30
    
    Certifications:
    - AWS Certified Solutions Architect
      Amazon Web Services
      Issued: 2021-03-15
      Expires: 2024-03-15
    
    Languages:
    - English (Native)
    - Spanish (Intermediate)
    - Mandarin (Basic)
    
    Technical Skills:
    - Python (Advanced)
    - JavaScript (Expert)
    - Docker (Intermediate)
    - AWS (Advanced)
    
    Soft Skills:
    - Team Leadership
    - Problem Solving
    - Communication
    - Agile Methodology
    
    Achievements:
    - Best Innovation Award 2022
      Led team to develop an AI-powered code review system
    - Open Source Contributor of the Year
      Recognized for significant contributions to Django framework
    
    Hobbies:
    - Open source contributing
    - Tech blogging
    - Mountain biking
    """
    
    try:
        # Create developer instance from text
        developer = Developer.from_text(dummy_resume)
        
        # Basic assertions to verify the extraction
        assert developer.name == "John Doe", f"Expected 'John Doe', got {developer.name}"
        assert developer.contact_info.email == "john.doe@email.com", \
            f"Expected 'john.doe@email.com', got {developer.contact_info.email}"
        assert len(developer.technical_skills) >= 4, \
            f"Expected at least 4 technical skills, got {len(developer.technical_skills)}"
        assert len(developer.soft_skills) >= 3, \
            f"Expected at least 3 soft skills, got {len(developer.soft_skills)}"
        assert len(developer.education) >= 2, \
            f"Expected at least 2 education entries, got {len(developer.education)}"
        assert len(developer.certifications) >= 1, \
            f"Expected at least 1 certification, got {len(developer.certifications)}"
        assert len(developer.languages) >= 3, \
            f"Expected at least 3 languages, got {len(developer.languages)}"
        assert len(developer.achievements) >= 2, \
            f"Expected at least 2 achievements, got {len(developer.achievements)}"
        assert developer.linkedin_url == "https://linkedin.com/in/johndoe", \
            f"Expected 'https://linkedin.com/in/johndoe', got {developer.linkedin_url}"
        
        # Test specific field values
        assert developer.education[0].institution_name == "Stanford University", \
            f"Expected 'Stanford University', got {developer.education[0].institution_name}"
        assert developer.certifications[0].name == "AWS Certified Solutions Architect", \
            f"Expected 'AWS Certified Solutions Architect', got {developer.certifications[0].name}"
        assert developer.languages[0].name == "English", \
            f"Expected 'English', got {developer.languages[0].name}"
        
        print("✅ All tests passed successfully!")
        return developer  # Return for manual inspection if needed
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_from_text()
