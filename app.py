# import streamlit as st
# import speech_recognition as sr
# from gtts import gTTS
# from pydub import AudioSegment
# from pydub.playback import play
# import openai
# import os
# from dotenv import load_dotenv
# from tempfile import NamedTemporaryFile
# from openai import OpenAI
# from utils import *
# import json
# import time

# # Load environment variables
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# openai.api_key = OPENAI_API_KEY
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import openai
import os
# from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
import pdfplumber
from openai import OpenAI
import json
client = OpenAI()
import io
from pydub import AudioSegment
from pydub.playback import play
# Load environment variables
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# openai.api_key = OPENAI_API_KEY
openai.api_key = st.secrets.OPENAI_API_KEY
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

# def text_to_speech(text):
#     """Convert text to speech using OpenAI and play"""
#     client = OpenAI()

#     # Generate speech with OpenAI API
#     response = client.audio.speech.create(
#         model="tts-1",
#         voice="nova",
#         input=text
#     )
#     # Get the audio data from the response content
#     audio_bytes = io.BytesIO(response.content)
#     audio = AudioSegment.from_file(audio_bytes)
#     play(audio)

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
                
                text_to_speech("  So please answer the following question")
                
                text_to_speech(f"... ...  {current_question}")
                st.markdown(f"<h3 style='font-weight: bold;'>{current_question}</h3>", unsafe_allow_html=True)

                # st.markdown(f"**Interview Question {question_index + 1}:** {current_question}")
                # text_to_speech(" umm  ... ... Recording will start in 5 seconds")
            
                text_to_speech(" umm  ... ... Recording starts in 3 ... ... 2 ... ... 1 ... ... Go!")
                
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

# if 'is_data_uploaded' in st.session_state and st.session_state['is_data_uploaded'] == 2:
#     question_index = st.session_state.get('current_question_index', 0)
#     questions = st.session_state.get('questions', {}).get('questions', [])
#     responses = st.session_state.get('responses', [])
    
#     if question_index + 1 > 5:
#         st.write(" ")
#     else:
#         st.markdown(f"### 📝 Question {question_index + 1}")
    
#     if question_index < len(questions):
#         current_question = questions[question_index]
#         st.markdown(f"<h3 style='font-weight: bold;'>{current_question}</h3>", unsafe_allow_html=True)

#         if st.button("🔊 Hear the Question"):
#             with st.spinner('🔊 Listening to the question'):
            
#                 # text_to_speech(" Please listen to the question carefully.")
#                 text_to_speech(f"  {current_question}")
#                 # text_to_speech("um ... ... You will record your answer next.")
        
#         if st.button("🎤 Record Answer"):
#             with st.spinner('🎤 Recording...'):
#                 user_input = get_text_from_voice()
#                 if user_input:
#                     text_to_speech(" um ... ... Thank you for your answer.")
#                     st.balloons()
#                     responses.append({"question": current_question, "answer": user_input})
#                     st.session_state['responses'] = responses
#                     st.session_state['current_question_index'] = question_index + 1
#                     save_responses_to_file(responses)
            
#             if question_index + 1 < len(questions):
#                 st.button("👉 Next Question", on_click=lambda: st.session_state.update(current_question_index=question_index + 1))
#     else:
#         st.markdown("### 🎉 You have answered all the questions. Thank you!")
#         st.balloons()
#         summary_text = generate_summary()
#         st.download_button('Download Summary', summary_text, file_name='interview_summary.txt')

    
        

        
