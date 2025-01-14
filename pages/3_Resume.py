import streamlit as st
from datetime import date
from models.resume import Resume
from models.job_offer import JobOffer, JobRequirements, ExperienceRequirement
from models.developer import Developer, ContactInfo, Skill, Language, Achievement, Education, Certification, JobPreferences
from models.work_experience import WorkExperience, Mission, Project, STARDescription
from utils.md2pdf import markdown_to_pdf
from streamlit_pdf_viewer import pdf_viewer
import tempfile
import os

def create_dummy_developer():
    # Create projects with STAR descriptions
    project1 = Project(
        project_name="E-commerce Platform Redesign",
        description=STARDescription(
            situation="Legacy e-commerce platform needed modernization",
            task="Lead developer responsible for frontend redesign",
            action="Implemented new React.js architecture and set up automated testing",
            result="Improved load times by 40%, increased mobile conversion by 25%"
        ),
        technologies=["React", "TypeScript", "Node.js"],
        achievements=["Reduced bundle size by 60%", "Led team of 3 developers"]
    )

    project2 = Project(
        project_name="Cloud Migration Project",
        description=STARDescription(
            situation="On-premise infrastructure needed migration to cloud",
            task="Technical lead for cloud migration initiative",
            action="Designed and implemented AWS-based architecture",
            result="Achieved 99.9% uptime and 30% cost reduction"
        ),
        technologies=["AWS", "Docker", "Python"],
        achievements=["Zero-downtime migration", "Implemented CI/CD pipeline"]
    )

    # Create work experiences with missions
    work_exp1 = WorkExperience(
        mission=Mission(
            job_title="Senior Software Engineer",
            company_name="Tech Corp",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            overall_summary="Led frontend development team in modernizing e-commerce platform"
        ),
        projects=[project1, project2]
    )

    return Developer(
        name="John Doe",
        contact_info=ContactInfo(
            email="john.doe@example.com",
            phone="+1 234 567 890",
            address="San Francisco, CA"
        ),
        linkedin_url="linkedin.com/in/johndoe",
        github_url="github.com/johndoe",
        website_url="johndoe.dev",
        professional_summary="Senior developer with 5 years of experience in web development",
        technical_skills=[
            Skill(name="Python", level="Expert"),
            Skill(name="React", level="Advanced"),
            Skill(name="AWS", level="Intermediate")
        ],
        soft_skills=["Leadership", "Communication", "Problem Solving"],
        work_experiences=[work_exp1],
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
                issue_date=date(2022, 1, 1),
                expiration_date=date(2025, 1, 1)
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

def create_dummy_job_offer():
    return JobOffer(
        job_title="Senior Full Stack Developer",
        company_name="Innovation Inc",
        location="San Francisco, CA",
        employment_type="Full-time",
        description="Looking for an experienced full-stack developer to lead our product development team",
        requirements=JobRequirements(
            hard_skills=["Python", "React", "AWS"],
            soft_skills=["Leadership", "Communication"],
            education_level="Bachelor's",
            certifications=["AWS Certified Developer"],
            experience=ExperienceRequirement(
                years_of_experience=5,
                relevant_experiences=[
                    "Full-stack development",
                    "Team leadership",
                    "Cloud architecture"
                ]
            ),
            languages=["English"],
            other_conditions=["Remote work possible"]
        ),
        perks=["Health insurance", "Remote work", "Flexible hours"],
        application_deadline=date(2024, 12, 31)
    )

def display_resume_generation():
    st.title("Resume Generator")
    
    # Get the developer and job offer from session state or create dummy values
    developer = st.session_state.get('developer')
    job_offer = st.session_state.get('job_offer')
    
    if not developer:
        developer = create_dummy_developer()
        st.warning("⚠️ Using dummy developer profile. Please complete your profile for a personalized resume!")
    
    if not job_offer:
        job_offer = create_dummy_job_offer()
        st.warning("⚠️ Using dummy job offer. Please add a real job offer for better targeting!")
    
    # Display current profile and job offer summaries
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Developer Profile")
        st.write(f"Name: {developer.name}")
        st.write(f"Current Role: {developer.work_experiences[-1].mission.job_title}")
        st.write(f"Skills: {', '.join(skill.name for skill in developer.technical_skills[:3])}")
        if not st.session_state.get('developer'):
            st.info("👆 This is sample data. Go to the Profile page to add your information.")
    
    with col2:
        st.subheader("Target Position")
        st.write(f"Role: {job_offer.job_title}")
        st.write(f"Company: {job_offer.company_name}")
        st.write(f"Required Skills: {', '.join(job_offer.requirements.hard_skills[:3])}")
        if not st.session_state.get('job_offer'):
            st.info("👆 This is sample data. Go to the Job Offer page to add the real position.")

    if st.button("Generate Resume"):
        with st.spinner("Generating your tailored resume..."):
            # Generate the resume
            resume = Resume.generate_resume(developer, job_offer)
            
            # Generate markdown
            markdown_content = resume.generate_markdown()
            
            # Save to session state
            st.session_state['generated_resume'] = resume
            st.session_state['resume_markdown'] = markdown_content
            
            # Display success message
            st.success("Resume generated successfully!")
    
    # Display the generated resume if available
    if 'resume_markdown' in st.session_state:
        st.subheader("Generated Resume")
        
        # Create tabs for different views and formats
        tab1, tab2, tab3, tab4 = st.tabs(["Preview", "Edit", "PDF Export", "Statistics"])
        
        with tab1:
            # Display formatted markdown
            st.markdown(st.session_state['resume_markdown'])
        
        with tab2:
            # Editable markdown with preview
            edited_markdown = st.text_area(
                "Edit your resume",
                st.session_state['resume_markdown'],
                height=400
            )
            if edited_markdown != st.session_state['resume_markdown']:
                st.session_state['resume_markdown'] = edited_markdown
                st.markdown("Preview of edited version:")
                st.markdown(edited_markdown)
        
        with tab3:
            # PDF export options
            st.write("Export your resume to PDF")
            style = st.selectbox(
                "Choose style",
                ["professional", "compact", "modern"],
                index=0
            )
            
            if st.button("Generate PDF"):
                with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tmp_md:
                    tmp_md.write(st.session_state['resume_markdown'].encode('utf-8'))
                    md_path = tmp_md.name
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                    pdf_path = tmp_pdf.name
                
                try:
                    # Generate PDF
                    markdown_to_pdf(md_path, pdf_path, style)
                    
                    # Read the generated PDF
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_data = pdf_file.read()
                    
                    # Create download button
                    st.download_button(
                        label="Download PDF",
                        data=pdf_data,
                        file_name=f"resume_{style}.pdf",
                        mime="application/pdf"
                    )
                    
                finally:
                    # Cleanup temporary files
                    os.unlink(md_path)
                    os.unlink(pdf_path)
        
        with tab4:
            # Display matching statistics
            resume = st.session_state['generated_resume']
            
            # Create metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Skills Match", 
                    f"{len(resume.relevant_skills)}/{len(job_offer.requirements.hard_skills)}"
                )
            
            with col2:
                st.metric(
                    "Projects Match",
                    len([proj for exp in resume.relevant_experience for proj in exp.projects])
                )
            
            with col3:
                st.metric(
                    "Requirements Match",
                    f"{len(resume.relevant_certifications)}/{len(job_offer.requirements.certifications)}"
                )
            
            # Display detailed matches
            st.write("### Matched Skills")
            for skill in resume.relevant_skills:
                st.write(f"- {skill.name} ({skill.level})")
            
            st.write("### Relevant Projects")
            for exp in resume.relevant_experience:
                for proj in exp.projects:
                    st.write(f"- {proj.project_name}")
                    st.write(f"  Technologies: {', '.join(proj.technologies)}")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Resume Generator",
        page_icon="📄",
        layout="wide"
    )
    display_resume_generation()
