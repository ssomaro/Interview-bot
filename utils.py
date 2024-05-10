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
        st.write("Say something...")
        audio = recognizer.listen(source, timeout=5)
        try:
            text = recognizer.recognize_google(audio)
            st.write(f"You said: {text}")
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

    # Remove the temporary file
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
    """Generate five interview questions using GPT-4."""
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