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
import json
client = OpenAI()

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
recognizer = sr.Recognizer()

def get_text_from_voice():
    """Capture voice and convert to text"""
    with sr.Microphone() as source:
        st.write("Please speak into the microphone. give a pause of 3 seconds after speaking.")
        audio = recognizer.listen(source, timeout=20)
        try:
            text = recognizer.recognize_google(audio)
            st.write(f"Response: {text}")
            return text
        except sr.UnknownValueError:
            st.write("Sorry, could not recognize your speech.")
        except sr.RequestError as e:
            st.write(f"Could not request results from Google Speech Recognition service; {e}")

    return ""

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

    # Save to file
    response.stream_to_file(speech_file_path)
    # Play the audio file
    audio = AudioSegment.from_mp3(speech_file_path)
    play(audio)
    #delete the file
    os.remove(speech_file_path)


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
   
        
       