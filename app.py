from flask import Flask, request, render_template, jsonify, send_file
import os
import uuid
from storygenerator import generate_story
from audio_generator import generate_audio
from video_editor import create_video_with_synced_text, transcribe_audio_with_whisper

app = Flask(__name__)

# Output folder to store generated files
OUTPUT_FOLDER = "output"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        # Get user's input prompt and video selection from the request
        data = request.json
        user_prompt = data.get("prompt", "")
        video_choice = data.get("video_choice", "minecraft_gameplay1.mp4")  # Default video if none is selected

        if not user_prompt.strip():
            return jsonify({"error": "No prompt provided"}), 400

        # Step 1: Generate story text using ChatGPT
        story_text = generate_story(user_prompt)

        # Step 2: Convert story text to audio using ElevenLabs
        audio_filename = f"audio_{uuid.uuid4()}.mp3"
        audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)
        generate_audio(story_text, output_file=audio_path)

        # Step 3: Transcribe audio using Whisper
        text_segments = transcribe_audio_with_whisper(audio_path)

        # Step 4: Dynamically set video based on user choice
        video_filename = f"video_{uuid.uuid4()}.mp4"
        video_path = os.path.join(OUTPUT_FOLDER, video_filename)
        gameplay_path = os.path.join("content", video_choice)

        # Step 5: Create final video
        create_video_with_synced_text(
            video_path=gameplay_path,
            audio_path=audio_path,
            text_segments=text_segments,
            output_path=video_path
        )

        # Step 6: Return the video URL
        return jsonify({"video_url": f"/download/{video_filename}"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
