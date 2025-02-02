"""
###############################################################################
#                           Recipe Generator API                              #
#-----------------------------------------------------------------------------#
# Author  : S.Akshith Raj                                                     #
# Email   : sakrj17@gmail.com                                                 #
# Degree  : M.Tech in Computer Science & Engineering (2023)                   #
#-----------------------------------------------------------------------------#
# Description:                                                                #
# This Flask-based API generates personalized recipes based on user input.    #
# It takes ingredients, meal type, cuisine preference, cooking time, and      #
# complexity level, then streams an AI-generated recipe in real time.         #
###############################################################################
"""

from flask import Flask, render_template, request, Response
from flask_cors import CORS
from openai import OpenAI  # OpenAI API integration
import time  # Used for debugging/delays if needed

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) for frontend requests

# OpenAI API Key (Replace with your actual key or store securely)
OPENAI_API_KEY = "your-api-key-here"
openai = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def home():
    """Renders the home page."""
    return render_template('index.html')

@app.route("/recipeStream", methods=["GET"])
def recipe_stream():
    """
    Handles real-time streaming of AI-generated recipes.
    
    - Extracts user input from the request (ingredients, meal type, cuisine, etc.).
    - Constructs a structured prompt for OpenAI.
    - Streams response back to the front end in chunks.
    """
    
    # Extract user inputs from query parameters
    ingredients = request.args.get("ingredients", "")
    meal_type = request.args.get("mealType", "")
    cuisine = request.args.get("cuisine", "")
    cooking_time = request.args.get("cookingTime", "")
    complexity = request.args.get("complexity", "")

    print(request.args)  # Debugging: Print request parameters to console

    # Construct the AI prompt based on user inputs
    prompt = [
        "Generate a recipe with the following details:",
        f"[Ingredients: {ingredients}]",
        f"[Meal Type: {meal_type}]",
        f"[Cuisine Preference: {cuisine}]",
        f"[Cooking Time: {cooking_time}]",
        f"[Complexity: {complexity}]",
        "Provide a detailed recipe including preparation steps.",
        "Ensure the recipe highlights fresh and vibrant flavors.",
        "Give the recipe a suitable name in the local language (based on cuisine preference).",
    ]
    
    # Format the prompt as a system message for OpenAI
    messages = [{"role": "system", "content": " ".join(prompt)}]

    def event_stream():
        """
        Streams OpenAI's response in real-time to the front end.
        
        - Uses SSE (Server-Sent Events) for live updates.
        - Sends chunks of data as they are received.
        """
        try:
            # Call OpenAI API with streaming enabled
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=messages,
                temperature=1,
                stream=True  # Enable streaming for real-time response
            )

            # Loop through streamed response chunks
            for chunk in response:
                # Check if OpenAI has finished generating the response
                if chunk.choices[0].finish_reason == "stop":
                    yield f"data: {str({'action': 'close'})}\n\n"

                else:
                    # First chunk: Start the recipe generation process
                    if chunk.choices[0].delta.get("role") == "assistant":
                        yield f"data: {str({'action': 'start'})}\n\n"

                    else:
                        # **Chunk Handling Explanation**
                        # OpenAI sends the response in small "chunks" of text.
                        # Instead of waiting for the full response, we send each part as soon as it's available.
                        # This makes the user experience feel more dynamic and interactive.
                        
                        yield f"data: {str({'action': 'chunk', 'chunk': chunk.choices[0].delta.get('content', '')})}\n\n"

        except Exception as e:
            # Handle API errors
            if 'insufficient_quota' in str(e):
                yield f"data: {str({'action': 'error', 'message': 'API Quota exceeded. Please try again later.'})}\n\n"
            else:
                print("Error fetching data from OpenAI API:", e)
                yield f"data: {str({'action': 'error', 'message': 'An unexpected error occurred.'})}\n\n"

    # Return the streaming response as SSE (Server-Sent Events)
    return Response(event_stream(), content_type="text/event-stream")

if __name__ == "__main__":
    # Start the Flask server on port 3001 with debugging enabled
    app.run(port=3001, debug=True)
