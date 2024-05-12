import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import openai
import os
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
import pdfplumber
from openai import OpenAI

from old.utils import *
client = OpenAI()

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Streamlit App
st.title("Interview Bot - SAIB")

# Initialize speech recognizer
recognizer = sr.Recognizer()


# Section 1: Resume and Job Description Input
st.write("### Step 1: Provide Resume and Job Description")
resume_file = st.file_uploader("Upload your resume (PDF format)", type="pdf")
job_description = st.text_area("Paste the Job Description here")

if st.button("Submit"):
    if resume_file and job_description:
        st.write("Loading...")
        resume_content = extract_text_from_pdf(resume_file)
        st.session_state['resume'] = resume_content
        st.session_state['job_description'] = job_description
        questions = generate_interview_questions(resume_content, job_description)
        st.session_state['questions'] = questions
        st.session_state['is_data_uploaded'] = True
        st.write("Resume and Job Description successfully uploaded.")
        print(questions)
        
    
    else:
        st.write("Please provide both Resume and Job Description.")

# Section 2: Voice Chatbot
if st.session_state.get('is_data_uploaded', False):
    st.write("### Step 2: Start Conversation")
    st.write("Click the 'Record' button below to start the conversation.")
    
    if st.button("Record"):
        user_input = get_text_from_voice()
        if user_input:
            prompt = f"You are a career assistant. Here is the resume: {st.session_state['resume']}. Here is the job description: {st.session_state['job_description']}. Based on these, answer the following question: {user_input}"
            chatbot_response = get_chatbot_response(prompt)
            st.write(f"Chatbot: {chatbot_response}")
            text_to_speech(chatbot_response)
