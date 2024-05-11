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
import time

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Streamlit App
st.title("Interview Bot - SAIB")

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Sidebar for uploading resume and job description
with st.sidebar:
    st.write("### Upload Resume and Job Description")
    if 'is_data_uploaded' not in st.session_state or st.session_state['is_data_uploaded'] == 0:
        resume_file = st.file_uploader("Upload your resume (PDF format)", type="pdf")
        job_description = st.text_area("Paste the Job Description here")

        if st.button("Click here to begin your interview!"):
            if resume_file and job_description:
                resume_content = extract_text_from_pdf(resume_file)
                st.session_state['resume'] = resume_content
                st.session_state['job_description'] = job_description
                questions = generate_interview_questions(resume_content, job_description)
                st.session_state['questions'] = questions
                st.session_state['current_question_index'] = 0
                st.session_state['responses'] = []
                st.session_state['is_data_uploaded'] = 2
                st.success("Resume and Job Description successfully uploaded.")
            else:
                st.error("Please provide both Resume and Job Description.")
    else:
        st.write("Data uploaded. Please proceed in the main panel and start your interview!.")


                
if 'is_data_uploaded' in st.session_state and st.session_state['is_data_uploaded'] == 2:
    question_index = st.session_state.get('current_question_index', 0)
    questions = st.session_state.get('questions', {}).get('questions', [])
    responses = st.session_state.get('responses', [])
    
    if question_index + 1 > 5:
        st.write(" ")
    else:
        st.markdown(f"### 📝 Question {question_index + 1}")
    
    if question_index < len(questions):
        with st.spinner('🔊 Listen to your question carefully and answer'):
            if st.button("🚀 Click here to attempt your question"):
                current_question = questions[question_index]
                time.sleep(1)
                text_to_speech(" <break time='1s'/> So please answer the following question")
                
                text_to_speech(f"... ...  {current_question}")
                st.markdown(f"<h3 style='font-weight: bold;'>{current_question}</h3>", unsafe_allow_html=True)

                # st.markdown(f"**Interview Question {question_index + 1}:** {current_question}")
                text_to_speech("... ...   Recording will start in 5 seconds")
                time.sleep(5)
                text_to_speech("... ...   Recording starts in 3 ... ... 2 ... ... 1 ... ...")
                
                with st.spinner('🎤 Recording ... ...'):
                    user_input = get_text_from_voice()
                    if user_input:
                        st.markdown(f"**You said:** {user_input}")
                        responses.append({"question": current_question, "answer": user_input})
                        st.session_state['responses'] = responses
                        st.session_state['current_question_index'] = question_index + 1
                        save_responses_to_file(responses)
                        text_to_speech(" ... ...   ... ... Thank you for your answer.")
                        st.balloons()

                if st.button("👉 Next Question"):
                    if question_index + 1 < len(questions):
                        question_index = st.session_state.get('current_question_index', 0) + 1
    else:
        st.markdown("### 🎉 You have answered all the questions. Thank you!")
        st.balloons()
        summary_text = generate_summary()
        st.download_button('Download Summary', summary_text, file_name='interview_summary.txt')
    
    
        

        
