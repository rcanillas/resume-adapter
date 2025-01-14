import streamlit as st
from datetime import date
from models.job_offer import JobOffer, JobRequirements, ExperienceRequirement

def job_offer_page():
    st.title("Job Offer Details")

    # Add text area for pasting job offer
    job_offer_text = st.text_area(
        "Paste Job Offer Text",
        height=300,
        help="Paste the complete job offer text here. The form below will be filled out automatically."
    )

    # Parse job offer text if provided
    job_offer = None
    if job_offer_text:
        try:
            with st.spinner("Parsing job offer..."):
                job_offer = JobOffer.from_text(job_offer_text)
            # Update session state
            st.session_state['job_offer'] = job_offer
            st.success("Job offer parsed successfully!")
        except Exception as e:
            st.error(f"Error parsing job offer: {str(e)}")

    # Get job offer from session state if it exists
    if not job_offer:
        job_offer = st.session_state.get('job_offer', None)

    # Separator for visual clarity
    st.divider()

    # Basic Job Info
    st.header("Basic Information")
    job_title = st.text_input(
        "Job Title",
        value=job_offer.job_title if job_offer else ""
    )
    company_name = st.text_input(
        "Company Name",
        value=job_offer.company_name if job_offer else ""
    )
    location = st.text_input(
        "Location",
        value=job_offer.location if job_offer else ""
    )
    employment_type = st.selectbox(
        "Employment Type",
        ["Full-time", "Part-time", "Contract", "Freelance","Non spécifié"],
        index=["Full-time", "Part-time", "Contract", "Freelance","Non spécifié"].index(job_offer.employment_type) if job_offer else 0
    )
    description = st.text_area(
        "Job Description",
        value=job_offer.description if job_offer else ""
    )

    # Requirements
    st.header("Job Requirements")
    
    # Hard Skills
    hard_skills_text = st.text_area(
        "Required Technical Skills (comma-separated)",
        value=", ".join(job_offer.requirements.hard_skills) if job_offer else "",
        help="Enter required technical skills separated by commas"
    )
    hard_skills = [s.strip() for s in hard_skills_text.split(",") if s.strip()]
    
    # Soft Skills
    soft_skills_text = st.text_area(
        "Required Soft Skills (comma-separated)",
        value=", ".join(job_offer.requirements.soft_skills) if job_offer else "",
        help="Enter required soft skills separated by commas"
    )
    soft_skills = [s.strip() for s in soft_skills_text.split(",") if s.strip()]
    
    # Education and Experience
    education_level = st.text_input(
        "Required Education Level",
        value= job_offer.requirements.education_level if job_offer else ""
    )

    years_experience = st.number_input(
        "Years of Experience Required",
        min_value=0,
        step=1,
        value=job_offer.requirements.experience.years_of_experience if job_offer else 0
    )
    
    # Relevant Experiences
    relevant_exp_text = st.text_area(
        "Relevant Experience Areas (comma-separated)",
        value=", ".join(job_offer.requirements.experience.relevant_experiences) if job_offer else "",
        help="Enter relevant experience areas separated by commas"
    )
    relevant_experiences = [s.strip() for s in relevant_exp_text.split(",") if s.strip()]
    
    # Other Requirements
    certifications_text = st.text_area(
        "Required Certifications (comma-separated)",
        value=", ".join(job_offer.requirements.certifications) if job_offer else "",
        help="Enter required certifications separated by commas"
    )
    certifications = [s.strip() for s in certifications_text.split(",") if s.strip()]
    
    languages_text = st.text_area(
        "Required Languages (comma-separated)",
        value=", ".join(job_offer.requirements.languages) if job_offer else "",
        help="Enter required languages separated by commas"
    )
    languages = [s.strip() for s in languages_text.split(",") if s.strip()]
    
    # Perks and Additional Info
    st.header("Additional Information")
    perks_text = st.text_area(
        "Perks and Benefits (comma-separated)",
        value=", ".join(job_offer.perks) if job_offer else "",
        help="Enter job perks separated by commas"
    )
    perks = [s.strip() for s in perks_text.split(",") if s.strip()]
    

    application_deadline = st.date_input(
        "Application Deadline",
        value=job_offer.application_deadline if job_offer and job_offer.application_deadline != "" else date.today()
    )

    if st.button("Save Job Offer"):
        # Create JobRequirements instance
        requirements = JobRequirements(
            hard_skills=hard_skills,
            soft_skills=soft_skills,
            education_level=education_level,
            certifications=certifications,
            experience=ExperienceRequirement(
                years_of_experience=years_experience,
                relevant_experiences=relevant_experiences
            ),
            languages=languages,
            other_conditions=[]
        )
        
        # Create JobOffer instance
        job_offer = JobOffer(
            job_title=job_title,
            company_name=company_name,
            location=location,
            employment_type=employment_type,
            description=description,
            requirements=requirements,
            perks=perks,
            application_deadline=application_deadline
        )
        
        # Save to session state
        st.session_state['job_offer'] = job_offer
        st.success("Job Offer Saved!")

if __name__ == "__main__":
    job_offer_page()
