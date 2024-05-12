import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import openai
import os
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
from old.utils import extract_text_from_pdf, generate_interview_questions, get_text_from_voice, text_to_speech, save_responses_to_file

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Initialize Streamlit session state variables
if 'resume_content' not in st.session_state:
    st.session_state['resume_content'] = ''
if 'job_description' not in st.session_state:
    st.session_state['job_description'] = ''
if 'questions' not in st.session_state:
    st.session_state['questions'] = []
if 'current_question_index' not in st.session_state:
    st.session_state['current_question_index'] = 0
if 'responses' not in st.session_state:
    st.session_state['responses'] = []
if 'is_data_uploaded' not in st.session_state:
    st.session_state['is_data_uploaded'] = 1

# Streamlit App
st.title("Interview Bot - SAIB")

# Section 1: Resume and Job Description Input
if st.session_state['is_data_uploaded'] == 1:
    st.write("### Step 1: Provide Resume and Job Description")
    resume_file = st.file_uploader("Upload your resume (PDF format)", type="pdf")
    job_description = st.text_area("Paste the Job Description here")

    if st.button("Submit"):
        if resume_file and job_description:
            st.write("Processing...")
            resume_content = extract_text_from_pdf(resume_file)
            st.session_state['resume_content'] = resume_content
            st.session_state['job_description'] = job_description
            questions = generate_interview_questions(resume_content, job_description)
            st.session_state['questions'] = questions['questions']
            st.session_state['is_data_uploaded'] = 2
            st.session_state['current_question_index'] = 0
            st.session_state['responses'] = []
            st.write("Resume and Job Description successfully uploaded.")
        else:
            st.warning("Please provide both Resume and Job Description.")

# Section 2: Voice Chatbot
if st.session_state['is_data_uploaded'] == 2:
    if st.button("### Step 2: click begin to start your interview"):
        question_index = st.session_state['current_question_index']
        questions = st.session_state['questions']
        responses = st.session_state['responses']
        if question_index < len(questions):
            current_question = questions[question_index]
            st.write(f"Interview Question {question_index + 1}: {current_question}")
            text_to_speech(f"{current_question}")

            if st.button("Record Answer", key="record_answer"):
                user_input = get_text_from_voice()
                if user_input:
                    st.write(f"You said: {user_input}")
                    responses.append({
                        "question": current_question,
                        "answer": user_input
                    })
                    st.session_state['responses'] = responses
                    st.session_state['current_question_index'] += 1
                    save_responses_to_file(responses)
                    text_to_speech("Thank you for your answer.")
                    # st.experimental_rerun()

            if st.button("Next Question", key="next_question"):
                st.session_state['current_question_index'] += 1
                st.experimental_rerun()

        else:
            st.write("You have answered all the questions. Thank you!")
