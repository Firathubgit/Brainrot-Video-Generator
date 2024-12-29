import os

# 1. EXPLICITLY SET IMAGEMAGICK BINARY PATH
from moviepy.config import change_settings
# Update the path below to match your actual ImageMagick installation path
change_settings({
    "IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
})

# 2. IMPORT MOVIEPY
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


def calculate_word_timestamps(text, audio_duration):
    """
    Distributes each word in 'text' evenly across 'audio_duration'.
    Returns a list of dicts with { 'word', 'start', 'end' }.
    """
    words = text.split()
    if not words:
        return []

    word_count = len(words)
    time_per_word = audio_duration / word_count
    
    timestamps = []
    current_time = 0.0
    for word in words:
        start_time = current_time
        end_time = current_time + time_per_word
        timestamps.append({"word": word, "start": start_time, "end": end_time})
        current_time = end_time

    return timestamps


def create_video_with_synced_text(video_path, audio_path, text, output_path="final_video.mp4"):
    """
    1. Loads the video (video_path) and audio (audio_path).
    2. Attaches audio to the video using .set_audio().
    3. Splits the input 'text' into words and calculates timestamps for each.
    4. Creates a TextClip for each word and overlays it at the correct time.
    5. Exports final_video.mp4 with x264 + AAC.
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

    # ---2. Calculate Word Timestamps---
    audio_duration = audio.duration
    timestamps = calculate_word_timestamps(text, audio_duration)

    # ---3. Create Text Clips---
    text_clips = []
    for item in timestamps:
        word = item["word"]
        start_time = item["start"]
        end_time = item["end"]

        try:
            # For short text, use method="label"
            txt_clip = TextClip(
                txt=word,
                fontsize=50,
                color="white",
                font="Winter_Minie.ttf",      # or any installed system font
                method="label"
            ).set_start(start_time).set_end(end_time).set_position("center")
            
            text_clips.append(txt_clip)
        except Exception as e:
            print(f"Error creating TextClip for word '{word}': {e}")

    # ---4. Combine Video + Text---
    final_video = CompositeVideoClip([video_with_audio, *text_clips])

    # ---5. Export Final Video---
    print("Rendering the final video. Please wait...")
    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac"
    )
    print(f"Video saved to '{output_path}'")


def main():
    """
    Main function: prompts user for video path, audio path, and text,
    then generates the final video with synced text.
    """
    video_path = input("Enter the path to your video file: ")
    audio_path = input("Enter the path to your audio file: ")
    text = input("Enter the text that was used to generate the audio: ")

    create_video_with_synced_text(video_path, audio_path, text)


if __name__ == "__main__":
    main()
