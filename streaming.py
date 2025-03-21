'''
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: Install Libraries                                                   │
│ ────────────────────────────────────────────────────────────────────────── │
│ pip install pyyaml ollama elevenlabs pydub gtts SpeechRecognition pyaudio   │
│ streamlit matplotlib                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 2: Run Streamlit Command                                               │
│ ────────────────────────────────────────────────────────────────────────── │
│ streamlit run streaming.py                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 3: Convert Speech to Text using SpeechRecognition                      │
│ ────────────────────────────────────────────────────────────────────────── │
│ - Record audio input from microphone                                        │
│ - Use recognizer.recognize_google(audio) to get text                        │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 4: Transcribe User Audio Text and Send as Input to LLM                 │
│ ────────────────────────────────────────────────────────────────────────── │
│ - Pass transcribed text to Ollama (Llama3)                                 │
│ - Get response text from LLM                                                │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 5: Convert LLM Response to Audio (MP3) with gTTS                      │
│ ────────────────────────────────────────────────────────────────────────── │
│ - Use gTTS to convert the LLM text response to audio                        │
│ - Save as "response.mp3" or directly play                                  │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 6: Play Converted Audio Response                                        │
│ ────────────────────────────────────────────────────────────────────────── │
│ - Play the MP3 file using a player or system command                        │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 7: Repeat Cycle Until 5-Minute Session Time is Reached                 │
│ ────────────────────────────────────────────────────────────────────────── │
│ - Track elapsed time, repeat steps 3–6 until time is up                     │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 8: Evaluate Conversation History with Different Ollama Agent            │
│ ────────────────────────────────────────────────────────────────────────── │
│ - Collect conversation history                                              │
│ - Send history to another Ollama agent for evaluation                       │
│ - Get evaluation score                                                       │
└─────────────────────────────────────────────────────────────────────────────┘

'''
import streamlit as st
import yaml
import ollama
import os
import re
import matplotlib.pyplot as plt
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
import time

image_path = 'personality_donut_chart.png'
# Check if the file exists
if os.path.exists(image_path):
    os.remove(image_path)

# Load config
def load_config(path="config.yaml"):
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config

config = load_config()

# Functions
def listen_to_microphone():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.write("🎙 Listening... Please speak.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.warning("❗ Sorry, I couldn't understand. Please try again.")
        return None
    except sr.RequestError as e:
        st.error(f"Speech recognition error: {e}")
        return None

def text_to_speech(text):
    if text.strip() == "":
        return None
    tts = gTTS(text=text, lang="en", slow=False)
    output_audio_path = "output_speech.mp3"
    tts.save(output_audio_path)
    return output_audio_path

def play_mp3(file_path):
    audio = AudioSegment.from_mp3(file_path)
    play(audio)

def plot_personality_donut_chart(traits: dict, filename: str):
    fig, axes = plt.subplots(1, len(traits), figsize=(len(traits)*3, 4))
    if len(traits) == 1:
        axes = [axes]  # Ensure axes is iterable if there's only one trait

    colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336']

    for ax, (trait, value), color in zip(axes, traits.items(), colors):
        ax.pie([value, 100 - value],
               startangle=90,
               colors=[color, '#E0E0E0'],
               wedgeprops={'width': 0.4, 'edgecolor': 'white'})

        ax.set(aspect="equal")
        ax.set_title(f"{trait}\n{value}%", fontsize=10)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def extract_and_plot_traits(response_text):
    pattern = r"Extraversion\s*:\s*(\d+)%\s*Openness\s*:\s*(\d+)%\s*Conscientiousness\s*:\s*(\d+)%\s*Agreeableness\s*:\s*(\d+)%\s*Neuroticism\s*:\s*(\d+)%"
    match = re.search(pattern, response_text)
    if match:
        traits = {
            "Extraversion": int(match.group(1)),
            "Openness": int(match.group(2)),
            "Conscientiousness": int(match.group(3)),
            "Agreeableness": int(match.group(4)),
            "Neuroticism": int(match.group(5))
        }
        chart_file = "personality_donut_chart.png"
        plot_personality_donut_chart(traits, chart_file)

def preprocess(conversation: list):
    # Process the conversation as described
    result = []
    # Keep the first element as is
    result.append(conversation[0])

    # Combine user and assistant content
    combined_content = ""
    for i in range(1, len(conversation), 2):
        combined_content += f"user: {conversation[i]['content']}\n "
        if i + 1 < len(conversation):
            combined_content += f"assistant: {conversation[i+1]['content']}\n "

    # Append the combined content
    result.append({'role': 'user', 'content': combined_content.strip()})
    return result

# Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = [{"role": "system", "content": config["prompt"]}]
if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "session_active" not in st.session_state:
    st.session_state.session_active = False

st.title("🧠 AI-Based Personality Test")
st.write("#### Please ensure you're in a quiet place for the most accurate results.")

# Countdown Timer Display
if st.session_state.session_active:
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, 300 - int(elapsed))
    minutes, seconds = divmod(remaining, 60)
    st.info(f"⏳ Time Remaining: {minutes:02d}:{seconds:02d}")

    if remaining <= 0:

        conversation = st.session_state.conversation
        conversation[0] = {"role": "system", "content": config["prompt_eval"]}
        # st.markdown(str(conversation))
        st.session_state.session_active = False
        st.write("✅ Time is up! Sending conversation for final evaluation...")

        final_eval = ollama.chat(
            model=config["ollama_model"],
            messages= preprocess(conversation)
        )

        final_summary = re.sub(r'(\([^)]*\)|\*)', '', final_eval['message']['content']).strip()

        # Clear button and previous response placeholders
        st.session_state.conversation = []
        st.session_state.ai_response = ""

        st.write("### 📝 Final Evaluation:")
        st.markdown(final_summary)

        extract_and_plot_traits(final_summary)
        if os.path.exists(image_path):
            st.image(image_path)

# Display last AI response if any
ai_response_placeholder = st.empty()
if st.session_state.ai_response:
    ai_response_placeholder.markdown(st.session_state.ai_response)

# Start/Continue Conversation Button
if st.button("🎤 Start / Continue Conversation"):
    if not st.session_state.session_active:
        st.session_state.start_time = time.time()
        st.session_state.session_active = True

    if st.session_state.session_active:
        user_input = listen_to_microphone()

        if user_input:
            st.session_state.conversation.append({"role": "user", "content": user_input})

            response = ollama.chat(
                model=config["ollama_model"],
                messages=st.session_state.conversation
            )

            ai_response = re.sub(r'(\([^)]*\)|\*)', '', response['message']['content']).strip()
            st.session_state.conversation.append({"role": "assistant", "content": ai_response})

            st.session_state.ai_response = ai_response
            ai_response_placeholder.markdown(ai_response)

            audio_path = text_to_speech(ai_response)
            if audio_path:
                st.write("🔊 Playing response...")
                play_mp3(audio_path)

            time.sleep(1)
            st.rerun()

st.info("Press the button above to let Sandy listen and respond!")
