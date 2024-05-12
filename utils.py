import streamlit as st
import openai
import sounddevice as sd
import wavio
import numpy as np
from openai import OpenAI
import os
import base64
from pydub.playback import play
from pydub import AudioSegment
from st_audiorec import st_audiorec
import pdfplumber
import json

# from dotenv import load_dotenv
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# client = OpenAI()
# openai.api_key = OPENAI_API_KEY
openai.api_key = st.secrets.OPENAI_API_KEY

def autoplay_audio(data):
    b64 = base64.b64encode(data).decode()
    md = f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        Your browser does not support the audio element.
        </audio>
        """
    st.markdown(
        md,
        unsafe_allow_html=True,
    )

def text_to_speech(text):
    """Convert text to speech using OpenAI and play"""
    
    client = OpenAI()
    speech_file_path = "speech.mp3"

    # Generate speech with OpenAI API
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(speech_file_path)
    
    audio = AudioSegment.from_mp3(speech_file_path)
    play(audio)
    
def record_audio(state, fs=44100):
    """Continuously record audio from the microphone."""
    def _recording_loop():
        while state.recording:
            state.audio.append(sd.rec(int(fs), samplerate=fs, channels=2, dtype='int16'))
            sd.wait()

    state.audio = []
    state.recording = True
    thread = Thread(target=_recording_loop)
    thread.start()


def speech_to_text(file_path):
    """Convert speech to text using OpenAI"""
    client = OpenAI()
    audio_file = open(file_path, "rb")

    # Generate speech with OpenAI API
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    return transcription.text

def get_chatbot_response(prompt):
    """Generate response using GPT-4"""
    
    completion = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ])
    return completion.choices[0].message.content.strip()

def extract_text_from_pdf(pdf_file):
    """Extract text content from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    print(text)
    return text


def generate_interview_questions(resume_text, job_desc):
    """Generate five interview questions using GPT-3.5."""
    prompt = f"""
    I am sharing a resume and a job description with you.
    Your task is to generate five interview questions that would be suitable to ask the candidate.

    Resume: {resume_text}
    Job Description: {job_desc}

    Respond in JSON format only, with an array of five questions like this do not include annything else even the word json,just the dictionary, i should be able to convert it to json :

    {{
        "questions": [
            "Question 1",
            "Question 2",
            "Question 3",
            "Question 4",
            "Question 5"
        ]
    }}
    """
    completion = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ])
    try:
        response_text = completion.choices[0].message.content.strip()
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        st.write("Error parsing the response. Please try again.")
        st.write(f"Raw response: {response_text}")
        st.write(f"JSONDecodeError: {e}")
        return {"questions": []}
    # return json.loads(completion.choices[0].message.content.strip())

def save_responses_to_file(responses):
    """Save the responses to a text file."""
    file_path = "interview_responses.txt"
    with open(file_path, "w") as f:
        for response in responses:
            f.write(f"Question: {response['question']}\n")
            f.write(f"Answer: {response['answer']}\n\n")
    st.write(f"Responses saved to {file_path}")


def generate_summary():
    #read interview response .txt file
    with open('interview_responses.txt', 'r') as file:
        responses = file.read()

    prompt = f""" the following are inteview responses from a candidate, please generate an summary if the candidate is suitable for the job or not.
    and provide feedback on the responses. be very specific and provide feedback on each question. also you can be critical and provide feedback on the responses.{responses}
    """
    completion = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a critical evaluator."},
        {"role": "user", "content": prompt},
    ])
    response_text = completion.choices[0].message.content.strip()
    st.write(f"Raw response: {response_text}")
    return (response_text)
   
       