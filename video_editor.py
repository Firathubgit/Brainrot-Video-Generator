import os
import whisper
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# Set the ImageMagick binary explicitly (update this path on your own machine)
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"


def transcribe_audio_with_whisper(audio_path):
    """
    Transcribes the audio file using Whisper and returns *word-level* timestamps.
    Args:
        audio_path (str): Path to the audio file.
    Returns:
        list of dict: Each dict has { 'text', 'start', 'end' } for individual words.
    """
    print("Transcribing audio with Whisper...")
    model = whisper.load_model("base")  # Choose model size: "tiny", "base", "small", "medium", or "large"
    # Enable word-level timestamps
    result = model.transcribe(audio_path, word_timestamps=True)

    # Collect word-by-word segments
    word_segments = []
    for segment in result["segments"]:
        # Each segment might contain multiple words
        for w in segment["words"]:
            word_segments.append({
                "text": w["word"],
                "start": w["start"],
                "end": w["end"]
            })

    print("Transcription (word-level) completed.")
    return word_segments


def group_words_into_chunks(word_segments, chunk_size=1):
    """
    Groups words into chunks of 'chunk_size'.
    If chunk_size=1, this returns purely word-level segments.
    If chunk_size=2, each segment has two words, etc.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")

    grouped_segments = []
    for i in range(0, len(word_segments), chunk_size):
        chunk = word_segments[i : i + chunk_size]

        # Combine the words' text
        combined_text = " ".join(w["text"] for w in chunk).strip()

        # The start time for this chunk is the start of the first word
        start_time = chunk[0]["start"]
        # The end time for this chunk is the end of the last word
        end_time = chunk[-1]["end"]

        grouped_segments.append({
            "text": combined_text,
            "start": start_time,
            "end": end_time
        })

    return grouped_segments


def create_video_with_synced_text(video_path, audio_path, text_segments, output_path="final_video.mp4"):
    """
    Creates a video with text synchronized to the audio using Whisper-generated timestamps.
    Args:
        video_path (str): Path to the base video.
        audio_path (str): Path to the audio file.
        text_segments (list): List of text segments with timestamps { text, start, end }.
        output_path (str): Path to save the final video.
    """
    # ---1. Load Video & Audio---
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' does not exist.")
        return
    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{audio_path}' does not exist.")
        return

    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    # Attach audio to video
    video_with_audio = video.set_audio(audio)

    # ---2. Create Text Clips---
    text_clips = []
    for segment in text_segments:
        try:
            txt_clip = (
                TextClip(
                    txt=segment["text"],
                    fontsize=50,
                    color="white",
                    method="label"
                )
                .set_start(segment["start"])
                .set_end(segment["end"])
                .set_position("center")
            )
            text_clips.append(txt_clip)
        except Exception as e:
            print(f"Error creating TextClip for segment '{segment['text']}': {e}")

    # ---3. Combine Video + Text---
    final_video = CompositeVideoClip([video_with_audio, *text_clips])

    # ---4. Export Final Video---
    print("Rendering the final video. Please wait...")
    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac"
    )
    print(f"Video saved to '{output_path}'")


def main():
    """
    Main function:
    1) Prompts user for video path and audio path.
    2) Runs Whisper to get word-level timestamps.
    3) Optionally groups words into larger chunks if desired.
    4) Generates the final video with synced text.
    """
    video_path = input("Enter the path to your video file: ")
    audio_path = input("Enter the path to your audio file: ")

    # Let the user decide how many words per chunk
    # chunk_size = 1 means purely word-by-word.
    # chunk_size = 2 or 3 means 2 or 3 words at a time, etc.
    try:
        chunk_size = int(input("Enter how many words per text clip (1 for single words): "))
    except ValueError:
        chunk_size = 1

    # 1) Run Whisper transcription (word-level)
    word_segments = transcribe_audio_with_whisper(audio_path)

    # 2) Group words into chunks (if chunk_size=1, that means purely single words)
    text_segments = group_words_into_chunks(word_segments, chunk_size=chunk_size)

    # 3) Generate the video
    create_video_with_synced_text(video_path, audio_path, text_segments)


if __name__ == "__main__":
    main()
