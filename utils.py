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
