import streamlit as st
from datetime import date
from models.developer import (
    Developer,
    Skill,
    Education,
    Certification,
    Language,
    Achievement,
    ContactInfo,
    JobPreferences,
)
from models.work_experience import WorkExperience, Project


def cleanup_list(text: str) -> list[str]:
    """Convert comma-separated text into a cleaned list of strings.

    Args:
        text (str): Comma-separated text input

    Returns:
        list[str]: List of cleaned strings, or empty list if input is empty
    """
    return [item.strip() for item in text.split(",")] if text else []


def developer_profile_page():
    """Streamlit page for inputting developer profile information."""
    st.title("Your Developer Profile")

    # Get developer from session state if it exists
    developer = st.session_state.get('developer', None)

    # Personal Info
    st.header("Personal Information")
    name = st.text_input("Full Name", value=developer.name if developer else "")
    email = st.text_input("Email Address", value=developer.contact_info.email if developer else "")
    phone = st.text_input("Phone Number", value=developer.contact_info.phone if developer else "")
    linkedin_url = st.text_input("LinkedIn Profile URL", value=developer.linkedin_url if developer else "")
    github_url = st.text_input("GitHub Profile URL", value=developer.github_url if developer else "")
    website_url = st.text_input("Personal Website URL (optional)", value=developer.website_url if developer else "")
    address = st.text_area("Address (optional)", value=developer.contact_info.address if developer else "")

    # Professional Summary
    st.header("Professional Summary")
    professional_summary = st.text_area(
        "Professional Summary",
        value=developer.professional_summary if developer else "",
        help="Write a brief summary highlighting your key skills and career goals",
    )

    # Skills
    st.header("Skills")
    initial_skill_count = len(developer.technical_skills) if developer else 0
    skill_count = st.number_input(
        "How many skills do you want to add?", 
        min_value=0, 
        step=1,
        value=initial_skill_count
    )
    
    skills = []
    for i in range(int(skill_count)):
        default_skill = developer.technical_skills[i] if developer and i < len(developer.technical_skills) else None
        
        # Create two columns for skill name and level
        col1, col2 = st.columns([2, 1])
        with col1:
            skill_name = st.text_input(
                f"Skill {i + 1} Name",
                value=default_skill.name if default_skill else ""
            )
        with col2:
            skill_level = st.selectbox(
                f"Skill {i + 1} Proficiency Level",
                ["Beginner", "Intermediate", "Advanced", "Expert"],
                index=["Beginner", "Intermediate", "Advanced", "Expert"].index(default_skill.level.level) if default_skill else 0
            )
        skills.append(Skill(name=skill_name, level=skill_level))

    # Work Experience
    st.header("Work Experience")
    initial_mission_count = len(developer.work_experiences) if developer else 0
    mission_count = st.number_input(
        "How many missions do you want to add?", 
        min_value=0, 
        step=1,
        value=initial_mission_count
    )
    
    work_experience = []
    for i in range(int(mission_count)):
        default_mission = developer.work_experiences[i] if developer and i < len(developer.work_experiences) else None
        
        st.subheader(f"Mission {i + 1}")
        job_title = st.text_input(
            f"Mission {i + 1} Job Title",
            value=default_mission.mission.job_title if default_mission else ""
        )
        company_name = st.text_input(
            f"Mission {i + 1} Company Name",
            value=default_mission.mission.company_name if default_mission else ""
        )
        start_date = st.date_input(
            f"Mission {i + 1} Start Date",
            value=default_mission.mission.start_date if default_mission else date.today()
        )
        end_date = st.date_input(
            f"Mission {i + 1} End Date",
            value=default_mission.mission.end_date if default_mission else date.today(),
            key=f"end_date_{i}"
        )
        overall_summary = st.text_area(
            f"Mission {i + 1} Overall Summary",
            value=default_mission.mission.overall_summary if default_mission else ""
        )

        # Projects within mission
        initial_project_count = len(default_mission.projects) if default_mission else 0
        project_count = st.number_input(
            f"How many projects for Mission {i + 1}?",
            min_value=0,
            step=1,
            value=initial_project_count,
            key=f"project_count_{i}"
        )
        
        projects = []
        for j in range(int(project_count)):
            default_project = default_mission.projects[j] if default_mission and j < len(default_mission.projects) else None
            
            st.text(f"Project {j + 1} for Mission {i + 1}")
            project_name = st.text_input(
                f"Project {j + 1} Name",
                value=default_project.project_name if default_project else "",
                key=f"project_name_{i}_{j}"
            )
            
            # STAR Framework inputs
            situation = st.text_area(
                f"Project {j + 1} Situation (STAR Framework)",
                value=default_project.description.situation if default_project else "",
                key=f"situation_{i}_{j}"
            )
            task = st.text_area(
                f"Project {j + 1} Task (STAR Framework)",
                value=default_project.description.task if default_project else "",
                key=f"task_{i}_{j}"
            )
            action = st.text_area(
                f"Project {j + 1} Action (STAR Framework)",
                value=default_project.description.action if default_project else "",
                key=f"action_{i}_{j}"
            )
            result = st.text_area(
                f"Project {j + 1} Result (STAR Framework)",
                value=default_project.description.result if default_project else "",
                key=f"result_{i}_{j}"
            )
            
            # Technologies and achievements
            technologies = st.text_area(
                f"Project {j + 1} Technologies (comma-separated)",
                value=",".join(default_project.technologies) if default_project else "",
                key=f"tech_{i}_{j}"
            )
            achievements = st.text_area(
                f"Project {j + 1} Achievements (comma-separated)",
                value=",".join(default_project.achievements) if default_project else "",
                key=f"achievements_{i}_{j}"
            )

            projects.append(
                Project(
                    project_name=project_name,
                    description={
                        "situation": situation,
                        "task": task,
                        "action": action,
                        "result": result,
                    },
                    technologies=cleanup_list(technologies),
                    achievements=cleanup_list(achievements)
                )
            )

        work_experience.append(
            WorkExperience(
                mission={
                    "job_title": job_title,
                    "company_name": company_name,
                    "start_date": start_date,
                    "end_date": end_date,
                    "overall_summary": overall_summary,
                },
                projects=projects,
            )
        )

    # Education
    st.header("Education")
    initial_education_count = len(developer.education) if developer else 0
    education_count = st.number_input(
        "How many education entries do you want to add?",
        min_value=0,
        step=1,
        value=initial_education_count
    )
    
    education = []
    for i in range(int(education_count)):
        default_edu = developer.education[i] if developer and i < len(developer.education) else None
        
        institution_name = st.text_input(
            f"Education {i + 1} Institution Name",
            value=default_edu.institution_name if default_edu else ""
        )
        degree = st.text_input(
            f"Education {i + 1} Degree",
            value=default_edu.degree if default_edu else ""
        )
        field_of_study = st.text_input(
            f"Education {i + 1} Field of Study",
            value=default_edu.field_of_study if default_edu else ""
        )
        start_date = st.date_input(
            f"Education {i + 1} Start Date",
            value=default_edu.start_date if default_edu else date.today(),
            key=f"edu_start_date_{i}"
        )
        end_date = st.date_input(
            f"Education {i + 1} End Date",
            value=default_edu.end_date if default_edu else date.today(),
            key=f"edu_end_date_{i}"
        )
        education.append(
            Education(
                institution_name=institution_name,
                degree=degree,
                field_of_study=field_of_study,
                start_date=start_date,
                end_date=end_date,
            )
        )

    # Certifications
    st.header("Certifications")
    initial_cert_count = len(developer.certifications) if developer else 0
    certification_count = st.number_input(
        "How many certifications do you want to add?",
        min_value=0,
        step=1,
        value=initial_cert_count
    )
    
    certifications = []
    for i in range(int(certification_count)):
        default_cert = developer.certifications[i] if developer and i < len(developer.certifications) else None
        
        name = st.text_input(
            f"Certification {i + 1} Name",
            value=default_cert.name if default_cert else ""
        )
        issuing_organization = st.text_input(
            f"Certification {i + 1} Issuing Organization",
            value=default_cert.issuing_organization if default_cert else ""
        )
        issue_date = st.date_input(
            f"Certification {i + 1} Issue Date",
            value=default_cert.issue_date if default_cert else date.today(),
            key=f"cert_issue_date_{i}"
        )
        certifications.append(
            Certification(
                name=name,
                issuing_organization=issuing_organization,
                issue_date=issue_date,
                expiration_date=None  # Optional field
            )
        )

    # Languages
    st.header("Languages")
    initial_lang_count = len(developer.languages) if developer else 0
    language_count = st.number_input(
        "How many languages do you want to add?",
        min_value=0,
        step=1,
        value=initial_lang_count
    )
    
    languages = []
    for i in range(int(language_count)):
        default_lang = developer.languages[i] if developer and i < len(developer.languages) else None
        
        # Create two columns for language name and proficiency
        col1, col2 = st.columns([2, 1])
        with col1:
            language_name = st.text_input(
                f"Language {i + 1} Name",
                value=default_lang.name if default_lang else ""
            )
        with col2:
            proficiency = st.selectbox(
                f"Language {i + 1} Proficiency Level",
                ["Beginner", "Intermediate", "Fluent", "Native"],
                index=["Beginner", "Intermediate", "Fluent", "Native"].index(default_lang.proficiency.level) if default_lang else 0
            )
        languages.append(Language(name=language_name, proficiency=proficiency))

    # Achievements
    st.header("Achievements")
    initial_achievement_count = len(developer.achievements) if developer else 0
    achievement_count = st.number_input(
        "How many achievements do you want to add?",
        min_value=0,
        step=1,
        value=initial_achievement_count
    )
    
    achievements = []
    for i in range(int(achievement_count)):
        default_achievement = developer.achievements[i] if developer and i < len(developer.achievements) else None
        
        title = st.text_input(
            f"Achievement {i + 1} Title",
            value=default_achievement.title if default_achievement else ""
        )
        description = st.text_area(
            f"Achievement {i + 1} Description",
            value=default_achievement.description if default_achievement else ""
        )
        achievements.append(Achievement(title=title, description=description))

    # Hobbies and Interests
    st.header("Hobbies and Interests")
    hobbies_text = st.text_area(
        "Hobbies (comma-separated)",
        value=",".join(developer.hobbies) if developer else "",
        help="Enter your hobbies and interests separated by commas",
    )
    hobbies = cleanup_list(hobbies_text)

    # Job Preferences
    st.header("Job Preferences")
    default_prefs = developer.job_preferences if developer else None
    job_title = st.text_input(
        "Preferred Job Title",
        value=default_prefs.job_title if default_prefs else ""
    )
    location = st.text_input(
        "Preferred Location",
        value=default_prefs.location if default_prefs else ""
    )
    employment_type = st.selectbox(
        "Employment Type",
        ["Full-time", "Part-time", "Contract"],
        index=["Full-time", "Part-time", "Contract"].index(default_prefs.employment_type) if default_prefs else 0
    )
    remote_work = st.checkbox(
        "Open to Remote Work",
        value=default_prefs.remote_work if default_prefs else False
    )
    salary_expectation = st.text_input(
        "Salary Expectation",
        value=default_prefs.salary_expectation if default_prefs else ""
    )
    other_conditions_text = st.text_area(
        "Other Conditions (comma-separated)",
        value=",".join(default_prefs.other_conditions) if default_prefs else ""
    )
    other_conditions = cleanup_list(other_conditions_text)

    # Soft Skills
    st.subheader("Soft Skills")
    soft_skills_text = st.text_area(
        "Soft Skills (comma-separated)",
        value=",".join(developer.soft_skills) if developer else "",
        help="Enter your soft skills separated by commas (e.g., Leadership, Communication, Team Work)",
    )
    soft_skills = cleanup_list(soft_skills_text)

    # Submit
    if st.button("Submit"):
        contact_info = ContactInfo(email=email, phone=phone, address=address)
        job_preferences = JobPreferences(
            job_title=job_title,
            location=location,
            employment_type=employment_type,
            remote_work=remote_work,
            salary_expectation=salary_expectation,
            other_conditions=other_conditions,
        )
        developer = Developer(
            name=name,
            contact_info=contact_info,
            linkedin_url=linkedin_url,
            github_url=github_url,
            website_url=website_url,
            professional_summary=professional_summary,
            technical_skills=skills,
            soft_skills=soft_skills,
            work_experiences=work_experience,
            education=education,
            certifications=certifications,
            languages=languages,
            achievements=achievements,
            hobbies=hobbies,
            job_preferences=job_preferences,
        )
        st.session_state['developer'] = developer
        st.success("Developer Profile Saved!")

developer_profile_page()
