import streamlit as st
import openai
from pydub import AudioSegment
from pydub.playback import play
from tempfile import NamedTemporaryFile
import os
import speech_recognition as sr



# Streamlit App
st.title("Voice Chatbot")

recognizer = sr.Recognizer()

def get_text_from_voice():
    """Capture voice and convert to text using OpenAI Whisper"""
    st.write("Say something... (Recording)")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=5)
    
    # Save the audio to a temporary WAV file
    with NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio.get_wav_data())
        temp_audio.close()
    
    # Transcribe the audio using OpenAI Whisper
    with open(temp_audio.name, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
    
    os.remove(temp_audio.name)
    return transcript["text"]

def text_to_speech(text):
    """Convert text to speech using OpenAI TTS"""
    speech_file_path = NamedTemporaryFile(delete=False, suffix=".mp3")
    
    response = openai.Audio.synthesize(
        model="text-davinci-002-render",
        voice="davinci-v2",
        input=text
    )
    speech_file_path.write(response["audio_content"])
    speech_file_path.close()
    
    audio = AudioSegment.from_mp3(speech_file_path.name)
    play(audio)
    os.remove(speech_file_path.name)

def get_chatbot_response(prompt):
    """Generate response using GPT-4"""
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message["content"].strip()

# Streamlit form
st.write("Click the 'Record' button below to start the conversation.")
if st.button("Record"):
    user_input = get_text_from_voice()
    if user_input:
        st.write(f"You said: {user_input}")
        chatbot_response = get_chatbot_response(user_input)
        st.write(f"Chatbot: {chatbot_response}")
        text_to_speech(chatbot_response)
