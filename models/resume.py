from typing import List, Tuple
from dataclasses import dataclass
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .developer import (
    Developer,
    Skill,
    Education,
    Certification,
    Language,
    Achievement,
    JobPreferences,
    ContactInfo,
)
from .work_experience import WorkExperience, Project, Mission
from .job_offer import JobOffer, JobRequirements, ExperienceRequirement

import os
from dotenv import load_dotenv


class ProjectMatchResponse(BaseModel):
    """Schema for the AI's response about project relevance."""

    is_match: bool = Field(
        description="Variable indicating if the project match the job requirements"
    )
    matching_reason: str = Field(
        description="Short explaination for why the project match or does not match the job requirement."
    )


def _create_project_matcher():
    """Create a LangChain chain for matching projects to requirements."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert AI recruiter analyzing the relevance of a developer's 
        project for a specific job position. Analyze the project details and job requirements 
        carefully and provide a structured evaluation of the match. If at least one of the 
        project's technologies is in the job requirements, the project is relevant.
        
        Focus on:
        1. Technical skills match
        2. Demonstrated experience
        3. Project complexity and scale
        """,
            ),
            (
                "human",
                """Project Details:
        {project_json}
        
        Job Requirements:
        {requirements_json}
        
        Evaluate the match between this project and the job requirements.""",
            ),
        ]
    )

    load_dotenv(".secrets")
    model = ChatOpenAI(
        model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(ProjectMatchResponse)

    return prompt | model


def _match_project_to_requirements(
    project: Project, requirements: JobRequirements
) -> Tuple[List[str], List[str], List[str]]:
    """Match a project against job requirements and return matching analysis.

    Args:
        project: Developer's project
        requirements: Job requirements

    Returns:
        Tuple containing:
        - List[str]: Matching reasons
        - List[str]: Matching skills
        - List[str]: Missing skills
    """
    # Convert project and requirements to dict for JSON serialization
    project_dict = {
        "name": project.project_name,
        "description": {
            "situation": project.description.situation,
            "task": project.description.task,
            "action": project.description.action,
            "result": project.description.result,
        },
        "technologies": project.technologies,
        "achievements": project.achievements,
    }

    requirements_dict = {
        "hard_skills": requirements.hard_skills,
        "soft_skills": requirements.soft_skills,
        "experience": {
            "years": requirements.experience.years_of_experience,
            "types": requirements.experience.relevant_experiences,
        },
    }

    chain = _create_project_matcher()
    response = chain.invoke(
        {
            "project_json": project_dict,
            "requirements_json": requirements_dict,
        }
    )
    return (response.is_match, response.matching_reason)


class BackgroundMatchResponse(BaseModel):
    """Schema for the AI's response about developer background relevance."""

    relevant_skills: List[str] = Field(
        description="List of developer's skills that are relevant for the job"
    )
    relevant_education: List[str] = Field(
        description="List of relevant education entries that match job requirements"
    )
    match_explanation: str = Field(
        description="Explanation of how the background matches the job requirements"
    )


def _create_background_matcher():
    """Create a LangChain chain for matching developer background to requirements."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert AI recruiter analyzing a developer's background 
        for a specific job position. Analyze their skills, education, and experience 
        against the job requirements and identify the most relevant elements.
        
        Focus on:
        1. Skills that directly match or are transferable
        2. Education that meets or exceeds requirements        
        Provide your response in a structured format with lists of relevant items.""",
            ),
            (
                "human",
                """Developer Background:
        {background_json}
        
        Job Requirements:
        {requirements_json}
        
        Evaluate which elements of the developer's background are most relevant for this position.""",
            ),
        ]
    )

    if "OPENAI_API_KEY" not in os.environ:
        load_dotenv(".secrets")
    model = ChatOpenAI(
        model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY")
    ).with_structured_output(BackgroundMatchResponse)

    return prompt | model


def _match_developer_background(
    developer: Developer,
    experience_req: ExperienceRequirement,
    requirements: JobRequirements,
) -> Tuple[List[Skill], List[Education], List[WorkExperience], float]:
    """Match developer's background against job requirements.

    Args:
        developer: Developer profile
        experience_req: Experience requirements
        requirements: Overall job requirements

    Returns:
        Tuple containing:
        - List[Skill]: Relevant skills
        - List[Education]: Relevant education
        - List[WorkExperience]: Relevant work experiences
        - float: Overall match score (0-1)
    """
    # Convert developer background to dict for JSON serialization
    background_dict = {
        "skills": [
            {"name": skill.name, "proficiency": skill.level}
            for skill in developer.technical_skills
        ],
        "education": [
            {
                "degree": edu.degree,
                "field": edu.field_of_study,
                "institution": edu.institution_name,
                "graduation_date": edu.end_date.isoformat(),
            }
            for edu in developer.education
        ],
        "work_experience": [
            {
                "title": exp.mission.job_title,
                "company": exp.mission.company_name,
                "duration": f"{exp.mission.start_date.isoformat()} to {exp.mission.end_date.isoformat()}",
                "summary": exp.mission.overall_summary,
            }
            for exp in developer.work_experiences
        ],
    }

    requirements_dict = {
        "hard_skills": requirements.hard_skills,
        "soft_skills": requirements.soft_skills,
        "education_level": requirements.education_level,
        "experience": {
            "years": experience_req.years_of_experience,
            "types": experience_req.relevant_experiences,
        },
    }

    chain = _create_background_matcher()
    response = chain.invoke(
        {
            "background_json": background_dict,
            "requirements_json": requirements_dict,
        }
    )
    # Convert response back to appropriate objects
    relevant_skills = [
        skill
        for skill in developer.technical_skills
        if skill.name in response.relevant_skills
    ]

    relevant_education = [
        edu
        for edu in response.relevant_education
    ]
    return (
        relevant_skills,
        relevant_education,
    )


@dataclass
class Resume:
    developer: Developer  # The developer's full profile
    job_offer: JobOffer  # The job offer details
    professional_summary: str  # Tailored summary for the resume
    relevant_skills: List[Skill]  # Skills selected based on the job offer
    relevant_experience: List[WorkExperience]  # Tailored work experiences
    relevant_certifications: List[Certification]  # Certifications matching the job offer
    relevant_education: List[Education]  # Education entries relevant to the job offer
    relevant_languages: List[Language]  # Languages matching the job offer requirements
    highlighted_achievements: List[Achievement]  # Relevant achievements

    @classmethod
    def generate_resume(cls, developer: Developer, job_offer: JobOffer) -> "Resume":
        """Generate a tailored resume based on developer profile and job requirements.
        
        Args:
            developer: Developer's full profile
            job_offer: Target job offer
            
        Returns:
            Resume: Tailored resume for the job
        """
        # Match developer's background
        relevant_skills, relevant_education = _match_developer_background(
            developer,
            job_offer.requirements.experience,
            job_offer.requirements
        )
        
        # Match projects and get best matches
        relevant_projects = []
        relevant_work_experiences = []
        for exp in developer.work_experiences:
            for project in exp.projects:
                is_match, matching_reasons = _match_project_to_requirements(
                    project, job_offer.requirements
                )
                if is_match:
                    relevant_projects.append((project, matching_reasons))
                    relevant_work_experiences.append(exp)
        
        # Generate professional summary based on matches
        summary_parts = []
        if relevant_skills:
            skills_str = ", ".join(skill.name for skill in relevant_skills[:3])  # Top 3 skills
            summary_parts.append(f"Experienced in {skills_str}")
        
        if relevant_education:
            edu = relevant_education[0]  # Most recent/relevant education
            summary_parts.append(f"with {edu}")
        
        years_exp = sum(
                (exp.mission.end_date.year - exp.mission.start_date.year) 
                for exp in developer.work_experiences
            )
        summary_parts.append(f"and {years_exp}+ years of relevant experience")
        
        summary_parts.append(f"seeking {job_offer.job_title} position at {job_offer.company_name}")
        professional_summary = " ".join(summary_parts)
        
        # Filter certifications based on job requirements
        relevant_certifications = [
            cert for cert in developer.certifications
            if cert.name in job_offer.requirements.certifications
        ]
        
        # Filter languages based on job requirements
        relevant_languages = [
            lang for lang in developer.languages
            if lang.name in job_offer.requirements.languages
        ]
        
        # Select achievements related to the job requirements
        relevant_achievements = []
        for achievement in developer.achievements:
            # Check if achievement relates to required skills or experience
            achievement_text = f"{achievement.title} {achievement.description}".lower()
            is_relevant = any(
                skill.lower() in achievement_text 
                for skill in job_offer.requirements.hard_skills + job_offer.requirements.soft_skills
            )
            if is_relevant:
                relevant_achievements.append(achievement)
        
        return cls(
            developer=developer,
            job_offer=job_offer,
            professional_summary=professional_summary,
            relevant_skills=relevant_skills,
            relevant_experience=relevant_work_experiences,
            relevant_certifications=relevant_certifications,
            relevant_education=relevant_education,
            relevant_languages=relevant_languages,
            highlighted_achievements=relevant_achievements
        )

    def generate_markdown(self) -> str:
        """Generate a professional markdown resume using LangChain.
        
        Returns:
            str: Markdown formatted resume
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional resume writer. Create a polished markdown resume 
            based on the provided information. Use a clean, modern format with clear sections.
            
            Focus on:
            1. Strong professional summary
            2. Relevant skills and experience
            3. Quantifiable achievements
            4. Clear, concise descriptions so that the resume is only one page long.
            
            The work experience section should be structured as a single paragraph for each mission, with the projects integrated naturally into the mission description.
            For each project, start with the impact of the project, then how the impact was achieved, then the technologies used.
            Use markdown formatting to create a professional layout.
            Integrate **keywords** and phrases from the job description naturally to optimize for ATS (Applicant Tracking Systems)."""),
            ("human", """Resume Information:
            {resume_json}
            Create a professional markdown resume tailored for this job application. Return only the markdown content, no other text or comments, without a markdown balise."""),
        ])

        # Convert resume data to JSON-serializable format
        resume_data = {
            "job_target": {
                "title": self.job_offer.job_title,
                "company": self.job_offer.company_name,
                "description": self.job_offer.description
            },
            "professional_summary": self.professional_summary,
            "contact_info": {
                "name": self.developer.name,
                "email": self.developer.contact_info.email,
                "phone": self.developer.contact_info.phone,
                "location": self.developer.contact_info.address,
                "linkedin": self.developer.linkedin_url,
                "github": self.developer.github_url,
                "website": self.developer.website_url
            },
            "skills": [
                {"name": skill.name, "level": skill.level}
                for skill in self.relevant_skills
            ],
            "experience": [
                {
                    "title": exp.mission.job_title,
                    "company": exp.mission.company_name,
                    "duration": f"{exp.mission.start_date.strftime('%b %Y')} - {exp.mission.end_date.strftime('%b %Y')}",
                    "summary": exp.mission.overall_summary,
                    "projects": [
                        {
                            "name": proj.project_name,
                            "description": {
                                "situation": proj.description.situation,
                                "task": proj.description.task,
                                "action": proj.description.action,
                                "result": proj.description.result
                            },
                            "technologies": proj.technologies,
                            "achievements": proj.achievements
                        }
                        for proj in exp.projects
                    ]
                }
                for exp in self.relevant_experience
            ],
            "education": [
                {
                    "degree": edu.degree,
                    "field": edu.field_of_study,
                    "institution": edu.institution_name,
                    "graduation": edu.end_date.strftime('%Y')
                }
                for edu in self.developer.education
            ],
            "certifications": [
                {
                    "name": cert.name,
                    "issuer": cert.issuing_organization,
                    "date": cert.issue_date.strftime('%b %Y'),
                    "expiry": cert.expiration_date.strftime('%b %Y')
                }
                for cert in self.relevant_certifications
            ],
            "languages": [
                {"name": lang.name, "level": lang.proficiency}
                for lang in self.relevant_languages
            ],
            "achievements": [
                {
                    "title": ach.title,
                    "description": ach.description
                }
                for ach in self.highlighted_achievements
            ]
        }

        load_dotenv(".secrets")
        model = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,  # Slightly higher temperature for more creative writing
        )
        
        chain = prompt | model
        
        response = chain.invoke({
            "resume_json": resume_data
        })
        
        return response.content

if __name__ == "__main__":
    # Toggle individual tests
    RUN_PROJECT_MATCHING_TEST = False
    RUN_BACKGROUND_MATCHING_TEST = False
    RUN_RESUME_GENERATION_TEST = False
    RUN_MARKDOWN_GENERATION_TEST = True

    from datetime import date
    from .work_experience import STARDescription, Mission, WorkExperience

    # Create common test data
    def create_test_data():
        """Create basic test data needed by all tests."""
        # First project (e-commerce platform)
        test_project1 = Project(
            project_name="E-commerce Platform Redesign",
            description=STARDescription(
                situation="Legacy e-commerce platform needed modernization",
                task="Lead developer responsible for frontend redesign",
                action="Implemented new React.js architecture, introduced TypeScript, and set up automated testing",
                result="Improved load times by 40%, increased mobile conversion by 25%"
            ),
            technologies=["React.js", "TypeScript", "Jest", "Redux", "Node.js"],
            achievements=[
                "Reduced bundle size by 60%",
                "Implemented CI/CD pipeline",
                "Led team of 3 developers"
            ]
        )

        # Second project (cloud migration)
        test_project2 = Project(
            project_name="Cloud Infrastructure Migration",
            description=STARDescription(
                situation="Company needed to migrate on-premise services to cloud infrastructure",
                task="Technical lead for the AWS migration project",
                action="Architected and implemented cloud-native solutions using AWS services, Python for automation, and established CI/CD pipelines",
                result="Successfully migrated 15 services with zero downtime, reduced infrastructure costs by 35%"
            ),
            technologies=["Python", "AWS", "Docker", "Terraform", "GitHub Actions"],
            achievements=[
                "Implemented infrastructure as code using Terraform",
                "Created automated deployment pipelines",
                "Trained team of 5 developers in cloud-native development"
            ]
        )

        # Third project (irrelevant mobile game)
        test_project3 = Project(
            project_name="Retro Mobile Game",
            description=STARDescription(
                situation="Personal project to learn game development",
                task="Solo developer creating a simple 2D mobile game",
                action="Used Unity engine and C# to create a classic arcade-style game",
                result="Published on Google Play Store with 1000+ downloads"
            ),
            technologies=["Unity", "C#", "Blender", "Android SDK"],
            achievements=[
                "Learned 3D modeling basics",
                "Implemented touch controls",
                "Published on app store"
            ]
        )

        # Main work experience with relevant projects
        test_work_experience1 = WorkExperience(
            mission=Mission(
                job_title="Senior Frontend Developer",
                company_name="Tech Corp",
                start_date=date(2020, 1, 1),
                end_date=date(2023, 1, 1),
                overall_summary="Led frontend development team in modernizing e-commerce platform"
            ),
            projects=[test_project1, test_project2]
        )

        # Separate work experience for game development
        test_work_experience2 = WorkExperience(
            mission=Mission(
                job_title="Game Developer",
                company_name="Indie Games Studio",
                start_date=date(2019, 6, 1),
                end_date=date(2019, 12, 1),
                overall_summary="Developed mobile games using Unity engine"
            ),
            projects=[test_project3]
        )

        # Create job offer first, then use its requirements
        test_job_offer = JobOffer(
            job_title="Senior Frontend Developer",
            company_name="Tech Innovators Inc.",
            location="Remote",
            employment_type="Full-time",
            description="Looking for an experienced frontend developer to lead our e-commerce platform modernization",
            requirements=JobRequirements(
                hard_skills=["React.js", "TypeScript", "Python", "AWS"],
                soft_skills=["Leadership", "Communication", "Problem Solving"],
                education_level="Bachelor's",
                certifications=["AWS Certified"],
                experience=ExperienceRequirement(
                    years_of_experience=3,
                    relevant_experiences=[
                        "Frontend development",
                        "Team leadership",
                        "E-commerce platforms"
                    ]
                ),
                languages=["English"],
                other_conditions=["Remote work possible"]
            ),
            perks=["Health insurance", "Remote work", "Flexible hours", "Learning budget"],
            application_deadline=date(2024, 12, 31)
        )

        test_developer = Developer(
            name="John Doe",
            contact_info=ContactInfo(
                email="john@example.com",
                phone="123-456-7890",
                address="123 Tech Street"
            ),
            linkedin_url="linkedin.com/in/johndoe",
            github_url="github.com/johndoe",
            website_url="johndoe.dev",
            professional_summary="Senior developer with 5 years of experience in web development",
            technical_skills=[
                Skill(name="React.js", level="Expert"),
                Skill(name="TypeScript", level="Advanced"),
                Skill(name="Python", level="Intermediate"),
                Skill(name="Docker", level="Beginner"),
            ],
            soft_skills=["Leadership", "Communication", "Problem Solving"],
            work_experiences=[test_work_experience1, test_work_experience2],
            education=[
                Education(
                    institution_name="Tech University",
                    degree="Bachelor's",
                    field_of_study="Computer Science",
                    start_date=date(2015, 9, 1),
                    end_date=date(2019, 6, 1)
                )
            ],
            certifications=[
                Certification(
                    name="AWS Certified Developer",
                    issuing_organization="Amazon Web Services",
                    issue_date=date(2021, 1, 1),
                    expiration_date=date(2024, 1, 1)
                )
            ],
            languages=[
                Language(name="English", proficiency="Native"),
                Language(name="French", proficiency="Intermediate")
            ],
            achievements=[
                Achievement(
                    title="Best Team Lead",
                    description="Led team to successful delivery of major project"
                )
            ],
            hobbies=["Open Source Contributing", "Tech Blogging"],
            job_preferences=JobPreferences(
                job_title="Senior Software Engineer",
                location="Remote",
                employment_type="Full-time",
                remote_work=True,
                salary_expectation="Competitive",
                other_conditions=["Flexible hours", "Health insurance"]
            )
        )

        return (
            test_project1, 
            test_project2, 
            test_project3, 
            test_work_experience1, 
            test_work_experience2, 
            test_job_offer, 
            test_developer
        )

    # Create test data once
    test_project1, test_project2, test_project3, test_work_experience1, test_work_experience2, test_job_offer, test_developer = create_test_data()

    if RUN_PROJECT_MATCHING_TEST:
        print("\n=== Testing Project Matching ===")
        print("\nProject details:")
        print(f"Name: {test_project1.project_name}")
        print(f"Technologies: {', '.join(test_project1.technologies)}")
        print("\nJob requirements:")
        print(f"Required skills: {', '.join(test_job_offer.requirements.hard_skills)}")
        print(f"Required experience: {', '.join(test_job_offer.requirements.experience.relevant_experiences)}")

        is_match, matching_reasons = _match_project_to_requirements(
            test_project1, test_job_offer.requirements
        )

        print("\nMatching Results:")
        print(f"Is Match: {is_match}")
        print("\nMatching Reasons:")
        for reason in matching_reasons:
            print(f"- {reason}")

    if RUN_BACKGROUND_MATCHING_TEST:
        print("\n=== Testing Background Matching ===")
        print("\nDeveloper Profile:")
        print(f"Name: {test_developer.name}")
        print(f"Skills: {', '.join(skill.name for skill in test_developer.technical_skills)}")
        print(f"Education: {test_developer.education[0].degree} in {test_developer.education[0].field_of_study}")

        relevant_skills, relevant_education = _match_developer_background(
            test_developer,
            test_job_offer.requirements.experience,
            test_job_offer.requirements
        )

        print("\nMatching Results:")
        print("\nRelevant Skills:")
        for skill in relevant_skills:
            print(f"- {skill.name} ({skill.level})")
        print("\nRelevant Education:")
        for edu in relevant_education:
            print(f"- {edu}")

    if RUN_RESUME_GENERATION_TEST:
        print("\n=== Testing Resume Generation ===")
        test_job_offer = JobOffer(
            job_title="Senior Frontend Developer",
            company_name="Tech Innovators Inc.",
            location="Remote",
            employment_type="Full-time",
            description="Looking for an experienced frontend developer to lead our e-commerce platform modernization",
            requirements=test_job_offer.requirements,
            perks=["Health insurance", "Remote work", "Flexible hours", "Learning budget"],
            application_deadline=date(2024, 12, 31)
        )

        print("\nGenerating tailored resume...")
        print(f"Job Title: {test_job_offer.job_title}")
        print(f"Company: {test_job_offer.company_name}")
        
        tailored_resume = Resume.generate_resume(test_developer, test_job_offer)
        
        print("\nGenerated Resume:")
        print("\nProfessional Summary:")
        print(tailored_resume.professional_summary)
        
        print("\nRelevant Skills:")
        for skill in tailored_resume.relevant_skills:
            print(f"- {skill.name} ({skill.level})")
        
        print("\nRelevant Experience:")
        for exp in tailored_resume.relevant_experience:
            print(f"\n{exp.mission.job_title} at {exp.mission.company_name}")
            print(f"Duration: {exp.mission.start_date} to {exp.mission.end_date}")
            print("Projects:")
            for project in exp.projects:
                print(f"  - {project.project_name}")
                print(f"    Technologies: {', '.join(project.technologies)}")
        
        if tailored_resume.relevant_certifications:
            print("\nRelevant Certifications:")
            for cert in tailored_resume.relevant_certifications:
                print(f"- {cert.name} (expires: {cert.expiry_date})")
        
        if tailored_resume.relevant_languages:
            print("\nRelevant Languages:")
            for lang in tailored_resume.relevant_languages:
                print(f"- {lang.name}: {lang.proficiency}")
        
        if tailored_resume.highlighted_achievements:
            print("\nHighlighted Achievements:")
            for achievement in tailored_resume.highlighted_achievements:
                print(f"- {achievement.title}: {achievement.description}")

    if RUN_MARKDOWN_GENERATION_TEST:
        print("\n=== Testing Markdown Resume Generation ===")
        
        # Create job offer for the test
        test_job_offer = JobOffer(
            job_title="Senior Frontend Developer",
            company_name="Tech Innovators Inc.",
            location="Remote",
            employment_type="Full-time",
            description="Looking for an experienced frontend developer to lead our e-commerce platform modernization",
            requirements=test_job_offer.requirements,
            perks=["Health insurance", "Remote work", "Flexible hours", "Learning budget"],
            application_deadline=date(2024, 12, 31)
        )

        print("\nGenerating resume for:")
        print(f"Developer: {test_developer.name}")
        print(f"Position: {test_job_offer.job_title} at {test_job_offer.company_name}")
        
        # First generate the resume
        resume = Resume.generate_resume(test_developer, test_job_offer)
        
        # Then generate the markdown
        print("\nGenerating markdown format...")
        markdown_content = resume.generate_markdown()
        
        print("\nGenerated Markdown Resume:")
        print("=" * 50)
        print(markdown_content)
        print("=" * 50)
        
        # Optionally save to file
        output_file = "generated_resume.md"
        with open(output_file, "w") as f:
            f.write(markdown_content)
        print(f"\nResume saved to {output_file}")
