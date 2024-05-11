import base64
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import openai
import os
from dotenv import load_dotenv
import pdfplumber
from openai import OpenAI
import json
from utils2 import *
from st_audiorec import st_audiorec
from pydub import AudioSegment
from pydub.playback import play
# Load environment variables
load_dotenv()
from audio_recorder_streamlit import audio_recorder
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
client = OpenAI()

def handle_show_q():
    st.session_state['show_audio'] = True
    st.session_state['show_submit_b'] = True
      

def handle_submit():
    st.session_state.current_question_index +=1
    st.session_state['show_audio'] = False
    

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
    
    if question_index + 1 > 4:
        st.write("Congratulations! You have answered all the questions.")
    # else:
    #     st.markdown(f"### 📝 Question {question_index + 1}")
    
    if st.session_state.get('current_question_index', 0) < len(questions):
        current_question = questions[question_index]
        if st.button(f"### 📝 Listen to Question {question_index + 1}", on_click = handle_show_q):
            question_text = current_question
            file_path = text_to_speech(question_text)
            
            

        if 'show_audio' in st.session_state and st.session_state['show_audio']:
            st.markdown(f"<h3 style='font-weight: bold;'>{current_question}</h3>", unsafe_allow_html=True)
            st.session_state.wav_audio_data = st_audiorec()
            if st.session_state.wav_audio_data  is not None:
                st.audio(st.session_state.wav_audio_data , format='audio/wav')

        if st.session_state.get('current_question_index', 0) < len(questions) and st.session_state.get('show_submit_b', 0) :
            if st.button("Save Response and Move to next Question",on_click= handle_submit ):
                st.balloons()
                st.session_state['show_audio'] = False
                file_path = "output.wav"
                if st.session_state.wav_audio_data is not None:
                    with open(file_path, "wb") as f:
                        f.write(st.session_state.wav_audio_data )
                    response_text = speech_to_text(file_path)
                else:
                    response_text = "No response"
                st.success("Response saved successfully!")
                st.session_state['responses'] = responses
                # st.session_state['current_question_index'] = question_index + 1
                st.session_state['show_audio'] = False
                responses.append({"question": current_question, "answer": response_text})
                print(responses)
                st.session_state['show_submit_b'] = False

    else:
        st.markdown("### 🎉 You have answered all the questions. Thank you!")
        st.balloons()
        summary_text = generate_summary()
        st.download_button('Download Summary', summary_text, file_name='interview_summary.txt')
        
