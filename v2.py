import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import openai
import os
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
from openai import OpenAI
from utils import *
import json
# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Streamlit App
st.title("Interview Bot - SAIB")

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Section 1: Resume and Job Description Input
if st.session_state.get('is_data_uploaded', 0) == 0:
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
            st.session_state['current_question_index'] = 0
            st.session_state['responses'] = []
            st.session_state['is_data_uploaded'] = 2
            st.write("Resume and Job Description successfully uploaded.")
            st.write("Questions generated:")
            st.write(questions)
        else:
            st.write("Please provide both Resume and Job Description.")

# Section 2: Voice Chatbot
# Section 2: Voice Chatbot
if st.session_state.get('is_data_uploaded', False) == 2:
    st.write("### Lets begin your interview. Click on the 'Begin' button to start.")
    
    # Get current question index and responses
    question_index = st.session_state.get('current_question_index', 0)
    questions = st.session_state.get('questions', {}).get('questions', [])
    responses = st.session_state.get('responses', [])

    if st.button("Begin") and question_index == 0:
        current_question = questions[question_index]
        st.write(f"Interview Question {question_index + 1}: {current_question}")
        text_to_speech(current_question)

    if question_index < len(questions):
        current_question = questions[question_index]
        st.write(f"Interview Question {question_index + 1}: {current_question}")

        if st.button("Record Answer"):
            user_input = get_text_from_voice()
            if user_input:
                st.write(f"You said: {user_input}")
                responses.append({
                    "question": current_question,
                    "answer": user_input
                })
                st.session_state['responses'] = responses
                st.session_state['current_question_index'] = question_index + 1
                save_responses_to_file(responses)
                text_to_speech("Thank you for your answer.")

        if st.button("Next Question"):
            if question_index + 1 < len(questions):
                next_question = questions[question_index + 1]
                st.write(f"Interview Question {question_index + 2}: {next_question}")
                text_to_speech(next_question)

    else:
        st.write("You have answered all the questions. Thank you!")



# if st.session_state.get('is_data_uploaded', False):
#     st.write("### Step 2: Start Conversation")
    
#     # Get current question index and responses
#     question_index = st.session_state.get('current_question_index', 0)
#     questions = st.session_state.get('questions', {}).get('questions', [])
#     responses = st.session_state.get('responses', [])

#     if question_index < len(questions):
#         current_question = questions[question_index]
#         st.write(f"Interview Question {question_index + 1}: {current_question}")
        
#         if st.button("Record Answer"):
#             user_input = get_text_from_voice()
#             if user_input:
#                 st.write(f"You said: {user_input}")
#                 responses.append({
#                     "question": current_question,
#                     "answer": user_input
#                 })
#                 st.session_state['responses'] = responses
#                 st.session_state['current_question_index'] = question_index + 1
#                 save_responses_to_file(responses)
#                 text_to_speech(f"Thank you for your answer. Moving on to the next question.")

#     else:
#         st.write("You have answered all the questions. Thank you!")
