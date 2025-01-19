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
                {"role": "system", "content": "You are a motivational, insperational person that will make the watcher of you'r tiktok video inspired to make money and persue greatness and their dream car."},
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
