import openai
import os

# Load the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_story(prompt_text):
    """
    Generates a story using OpenAI's ChatGPT API.
    Args:
        prompt_text (str): The user's input prompt for the story.
    Returns:
        str: The generated story.
    """
    try:
        # Use the new ChatCompletion.create interface
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "you are a tiktok video creator. Your videos have content playing behind you and you job is simply creating the story in a redy to voice over state. none off this voiceover, background set detail describing. Just pure script off what the voice over is going to say. The video behind you is not going to chnage under no surcumstance so you are just going to output the script. The theme is probmt based and it can be whatever. Countinues story, no numbers throughout the script which clariyfies parts."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7,  # Adjust creativity level
            max_tokens=200   # Limit the length of the story
        )

        # Extract the content of the response
        story = response["choices"][0]["message"]["content"]
        return story
    except Exception as e:
        # Return a meaningful error message for debugging
        return f"Error generating story: {str(e)}"
