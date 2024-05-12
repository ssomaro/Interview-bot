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
from utils import *

from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI()





# Streamlit app layout
st.title("Interactive Q&A Application")

# Text to speech section
if st.button("Listen to Question"):
    question_text = "What are your thoughts on the future of AI technology?"
    file_path = text_to_speech(question_text)
    # st.audio(file_path)

wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    st.audio(wav_audio_data, format='audio/wav')

#save the audio file
if st.button("Save Response and Move to next Question"):
    st.balloons()
    file_path = "output.wav"
    with open(file_path, "wb") as f:
        f.write(wav_audio_data)
    response_text = speech_to_text(file_path)
    st.success("Response saved successfully!")