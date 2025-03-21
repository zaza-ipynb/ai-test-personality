# AI-test-personality
have a natural conversation with AI to asses users personality

## Project Setup

This guide will help you set up the Python virtual environment for the project, activate it, and install the required dependencies.

### Prerequisites

Ensure that Python 3.12 is installed on your system. You can download it from [python.org](https://www.python.org/downloads/). You should also have `pip` (Python's package installer) installed.

### Steps to Set Up the Project

1. **Create a Virtual Environment**

   Open a terminal and navigate to your project directory. Then, create the virtual environment by running the following command:

   ```
   python3.12 -m venv myenv
   source myenv/bin/activate
   ```
2. **Install Required Packages**

    With the virtual environment activated, run the following command to install the necessary packages,
    make sure install portaudio first before pyaudio using brew for mac or apt install for linux:
    ```
      pip install pyyaml ollama elevenlabs pydub gtts SpeechRecognition pyaudio streamlit matplotlib
    ```
3. **Run the command**
   ```
      python ai_personality_test.py --tts=1
   ```
   tts = 1 means using gtts (free but less optimized, not streamed), tts = 2 using elevenlabs which has limited free quota 10k credit per month but stream, just dont forget to set the api key of    elevenlabs in the config.yaml
4. **UI version**
   I also create the UI version using streamlit, can run using this command :
   ```
      streamlit run streaming.py
   ```

