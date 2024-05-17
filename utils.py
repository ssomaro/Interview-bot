import streamlit as st
import openai
from openai import OpenAI
import os
import base64
from pydub.playback import play
import pdfplumber
import json
# from dotenv import load_dotenv
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# MODEL_NAME = os.getenv("MODEL_NAME")
# openai.api_key = OPENAI_API_KEY

openai.api_key = st.secrets.OPENAI_API_KEY
MODEL_NAME = st.secrets.MODEL_NAME

from prompts.interview_prompts import generate_questions_prompt, generate_feedback_prompt
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = OpenAI(model_name= MODEL_NAME, temperature=0.9)



def autoplay_audio(file_path):
    with open(file_path, "rb") as audio_file:
        audio_data = audio_file.read()
    
    b64 = base64.b64encode(audio_data).decode()
    md = f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        Your browser does not support the audio element.
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)



def extract_text_from_pdf(pdf_file):
    """Extract text content from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    print(text)
    return text


def generate_interview_questions(resume_text, job_desc):
    """Generate three interview questions using GPT-3.5."""
    prompt = PromptTemplate.from_template(generate_questions_prompt())
    chain = LLMChain(llm=llm, prompt=prompt)
    response_text = chain.run({"resume_text": resume_text, "job_desc": job_desc})
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        st.write("Error parsing the response. Please try again.")
        # st.write(f"Raw response: {response_text}")
        st.write(f"JSONDecodeError: {e}")
        return {"questions": []}
    

def save_responses_to_file(responses):
    """Save the responses to a text file."""
    file_path = "interview_responses.txt"
    with open(file_path, "w") as f:
        for response in responses:
            f.write(f"Question: {response['question']}\n")
            f.write(f"Answer: {response['answer']}\n\n")
    st.write(f"Your responses have been saved successfully!")


def generate_summary():
    #read interview response .txt file
    with open('interview_responses.txt', 'r') as file:
        responses = file.read()
    prompt = PromptTemplate.from_template(generate_feedback_prompt())
    chain = LLMChain(llm=llm, prompt=prompt)
    response_text = chain.run({"responses": responses})
    
    text_to_speech("Thank you ! for taking time to attend the interview, we will get back to you soon. Have a great day!")
    # st.write(f"Raw response: {response_text}")
    return (response_text)
   
def text_to_speech(text):
    """Convert text to speech using OpenAI and play"""
    try:
        from openai import OpenAI
        client = OpenAI()
        speech_file_path = "speech.mp3"
    
        # Generate speech with OpenAI API
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
    
        response.stream_to_file(speech_file_path)
    
        # Play the audio using the updated autoplay_audio function
        autoplay_audio(speech_file_path)
    
    finally:
        # Clean up the file after playback
        if os.path.exists(speech_file_path):
            os.remove(speech_file_path)
    


def speech_to_text(file_path):
    """Convert speech to text using OpenAI"""
    from openai import OpenAI
    client = OpenAI()
    audio_file = open(file_path, "rb")

    # Generate speech with OpenAI API
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    return transcription.text
