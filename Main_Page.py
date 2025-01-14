import streamlit as st
import pdfplumber
import tempfile
from pathlib import Path
from models.developer import Developer
from models.work_experience import WorkExperience
import os

def parse_pdf(uploaded_file):
    """Parse uploaded PDF and return its content as string."""
    text_content = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        # Write PDF content to temporary file
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # Parse PDF using pdfplumber
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                text_content += page.extract_text() or ""
    finally:
        # Clean up temporary file
        Path(tmp_path).unlink()
    
    return text_content

def check_api_key():
    """Check if OpenAI API key exists in .secrets file or environment"""
    secrets_path = Path('.secrets')
    if secrets_path.exists():
        with open(secrets_path) as f:
            if 'OPENAI_API_KEY' in f.read():
                return True
    return 'OPENAI_API_KEY' in os.environ

st.title("Resume Updater")
st.write("This app allows you to update your resume to a job offer by finding the most relevant experiences and skills.")
if not check_api_key():
        warn = st.warning("⚠️ OpenAI API key not found")
        api_key = st.text_input(
            "Please enter your OpenAI API key",
            type="password",
            help="Your API key will be saved in the .secrets file"
        )
        
        if api_key:
            try:
                # Save to .secrets file
                with open('.secrets', 'w') as f:
                    f.write(f'OPENAI_API_KEY={api_key}')
                os.environ['OPENAI_API_KEY'] = api_key
                st.success("✅ API key saved successfully!")
                warn.empty()
            except Exception as e:
                st.error(f"Error saving API key: {str(e)}")

# File uploader
uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=['pdf'])

if uploaded_file is not None:
    # Create a container to show the parsing status
    with st.spinner('Parsing PDF...'):
        try:
            # Parse the PDF
            text_content = parse_pdf(uploaded_file)
            
            # Show success message
            st.success('PDF successfully parsed!')
            
            # Display the parsed content in an expandable section
            with st.expander("View Raw Content"):
                st.text_area("Content", text_content, height=300)
        except Exception as e:
            st.error(f'Error parsing PDF: {str(e)}')            
    # Create developer profile
   
    with st.spinner('Creating personal profile...'):
        developer = Developer.from_text(text_content)
    with st.spinner('Creating work experience...'):
        work_experiences = WorkExperience.from_text(text_content)
    developer.work_experiences = work_experiences
    if developer:
        st.success('Developer profile created successfully! Click on the next page (left column) to review and edit your profile.')                     
        # Store the developer instance in session state
        st.session_state['developer'] = developer
                    
        # Add a button to navigate to the profile page
    else:
        st.error('Error creating developer profile. Please try again.')
