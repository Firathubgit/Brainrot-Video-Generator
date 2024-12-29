import requests
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")

if not api_key:
    raise ValueError("API key not found. Please add ELEVENLABS_API_KEY to your .env file.")

# ElevenLabs API URL
url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"

def generate_audio(text, output_file="content\output_audio.mp3"):
    """
    Generate audio using ElevenLabs API and save it to a file.
    Args:
        text (str): Text to convert to speech.
        output_file (str): Path to save the generated audio.
    Returns:
        str: Path to the generated audio file.
    """
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.85
        }
    }
    headers = {
        "accept": "audio/mpeg",
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        with open(output_file, "wb") as file:
            file.write(response.content)
        print(f"Audio saved as '{output_file}'")
        return output_file
    else:
        raise Exception(f"Failed to generate audio: {response.status_code} - {response.text}")

# Example usage (uncomment for testing)
text = input("Enter the text to convert to audio: ")
generate_audio(text)
