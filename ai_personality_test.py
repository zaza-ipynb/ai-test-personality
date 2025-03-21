'''
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 1: Install Libraries                                                   │
│ ────────────────────────────────────────────────────────────────────────── │
│ pip install pyyaml ollama elevenlabs pydub gtts SpeechRecognition pyaudio   │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 2: Convert Speech to Text using SpeechRecognition                      │
│ ────────────────────────────────────────────────────────────────────────── │
│ - Record audio input from microphone                                        │
│ - Use recognizer.recognize_google(audio) to get text                        │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 3: Transcribe user audio text and send as input to LLM                 │
│ ────────────────────────────────────────────────────────────────────────── │
│ - Take transcribed text                                                     │
│ - Pass the text into your LLM (ex: ollama.generate(prompt))                 │
│ - Get response text                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Step 4: Text-to-Speech using gTTS                                           │
│ ────────────────────────────────────────────────────────────────────────── │
│ - Convert LLM response text to audio with gTTS                              │
│ - Play or save the audio output                                             │
└─────────────────────────────────────────────────────────────────────────────┘

'''

import yaml
import ollama
import os
from io import BytesIO
from typing import IO
import re
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import argparse
import speech_recognition as sr

# Parse command-line arguments
parser = argparse.ArgumentParser(description="AI personality assessor")
parser.add_argument("--tts", type=int, required=True, help="Choose model tts as defined in the config.yaml")
args = parser.parse_args()


def load_config(path="config.yaml"):
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config

config = load_config()


def listen_to_microphone():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Listening... (Speak now)")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        print("Transcribing...")
        text = recognizer.recognize_google(audio)
        print(f"You (transcribed): {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand. Please try again.")
        return None
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")
        return None

# Function to convert text to speech (TTS)

def text_to_speech(text):
    if not text.strip():
        return "Error: No text provided."
    
    tts = gTTS(text=text, lang="en", slow=False)
    output_audio_path = "output_speech.mp3"   # Change extension to .mp3
    tts.save(output_audio_path)

    return output_audio_path

def play_mp3(file_path):
    audio = AudioSegment.from_mp3(file_path)
    play(audio)



def text_to_speech_stream(text: str) -> IO[bytes]:
    ELEVENLABS_API_KEY = config['elevenlabs_api_key']  # load from config.yaml
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    response = client.text_to_speech.convert(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # James voice or any voice ID you prefer
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )

    audio_stream = BytesIO()
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)

    audio_stream.seek(0)
    return audio_stream

def play_audio_stream(audio_stream: IO[bytes]):
    temp_filename = "temp_audio.mp3"
    with open(temp_filename, "wb") as f:
        f.write(audio_stream.read())
    os.system(f"afplay {temp_filename}")  # 'afplay' works on macOS
    os.remove(temp_filename)



# --- Ollama chat with integrated TTS ---
class AI_Assistant_Ollama:
    def __init__(self):
        self.model_name = config['ollama_model']
        self.full_transcript = [
            {"role": "system", "content": config['prompt']},
        ]

    def chat(self):
        print("Type 'exit' to end the conversation.\n")
        while True:
            # user_input = input("You: ")
            user_input = listen_to_microphone()
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            self.full_transcript.append({"role": "user", "content": user_input})

            response = ollama.chat(
                model=self.model_name,
                messages=self.full_transcript
            )

            ai_response = re.sub(r'\([^)]*\)', '', response['message']['content']).strip()
            self.full_transcript.append({"role": "assistant", "content": ai_response})
            print(f"Sandy: {ai_response}\n")

            # Play AI response audio
            if args.tts == 1 :
                audio = text_to_speech(ai_response)
                play_mp3(audio)
            elif args.tts == 2:
                audio = text_to_speech_stream(ai_response)
                play_audio_stream(audio)
            else:
                print("choose a valid tts model first!")
                break



if __name__ == "__main__":
    ai_assistant = AI_Assistant_Ollama()
    greetings = "Hi, welcome to AI based personality test, please get a quiet place so we can achieve an accurate result!"
    print(greetings+"\n")
    if args.tts == 1 :
        audio = text_to_speech(greetings)
        play_mp3(audio)
    elif args.tts == 2:
        audio = text_to_speech_stream(greetings)
        play_audio_stream(audio)
    else:
        print("choose a valid tts model first!")
    ai_assistant.chat()
