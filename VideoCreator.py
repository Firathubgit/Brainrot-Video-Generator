import os
from dotenv import load_dotenv
from elevenlabs import set_api_key, generate, save

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please add ELEVENLABS_API_KEY to your .env file.")

# Set the API key for ElevenLabs
set_api_key(api_key)

# Example usage: Generate and save an audio file
def generate_audio(text, output_file="output_audio.mp3"):
    audio = generate(
        text=text,
        voice="Rachel",  # Replace with your desired voice
        model="eleven_monolingual_v1"
    )
    save(audio, output_file)
    print(f"Audio saved to {output_file}")

# Generate an example audio file
generate_audio("Hello, this is a secure test using ElevenLabs!")
