import os
import whisper
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# Set the ImageMagick binary explicitly (update this path on your own machine)
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

# Define font name or path (if it's installed)
CUSTOM_FONT = "Winter_Minie"  # Use installed font
# CUSTOM_FONT = "C:/path/to/Winter_Minie.ttf"  # Uncomment if using a custom font file


def transcribe_audio_with_whisper(audio_path):
    """
    Transcribes the audio file using Whisper and returns *word-level* timestamps.
    """
    print("Transcribing audio with Whisper...")
    model = whisper.load_model("base")  # Choose model size: "tiny", "base", "small", "medium", or "large"
    
    result = model.transcribe(audio_path, word_timestamps=True)

    # Collect word-by-word segments
    word_segments = []
    for segment in result["segments"]:
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
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")

    grouped_segments = []
    for i in range(0, len(word_segments), chunk_size):
        chunk = word_segments[i: i + chunk_size]
        combined_text = " ".join(w["text"] for w in chunk).strip()
        start_time = chunk[0]["start"]
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
    video_with_audio = video.set_audio(audio)

    # ---2. Create Text Clips---
    text_clips = []
    for segment in text_segments:
        try:
            txt_clip = (
                TextClip(
                    txt=segment["text"],
                    fontsize=50,
                    font=CUSTOM_FONT,  # Apply custom font
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
    - Prompts user for video path and audio path.
    - Runs Whisper to get word-level timestamps.
    - Optionally groups words into larger chunks if desired.
    - Generates the final video with synced text.
    """
    video_path = input("Enter the path to your video file: ")
    audio_path = input("Enter the path to your audio file: ")

    try:
        chunk_size = int(input("Enter how many words per text clip (1 for single words): "))
    except ValueError:
        chunk_size = 1

    word_segments = transcribe_audio_with_whisper(audio_path)
    text_segments = group_words_into_chunks(word_segments, chunk_size=chunk_size)
    create_video_with_synced_text(video_path, audio_path, text_segments)


if __name__ == "__main__":
    main()
