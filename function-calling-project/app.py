import os
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
@tool
def calculator(expression: str) -> float:
    """
    Evaluate a mathematical expression and return the result.

    Parameters:
    expression (str): A string containing the mathematical expression to evaluate.

    Returns:
    float: The result of the evaluated expression.

    Examples:
    >>> evaluate_expression("2 + 3 * 4")
    14.0
    >>> evaluate_expression("(10 / 2) + 8")
    13.0

    Note:
    - This function uses Python's eval() to calculate the result.
    - Ensure the input is sanitized to avoid malicious code execution.
    """
    try:
        # Evaluate the expression safely
        result = eval(expression, {"_builtins_": {}})
        return float(result)
    except Exception as e:
        print(f"Error evaluating expression: {e}")
        return None


@tool
def get_weather(city: str) -> str:
    """
    Fetches the current weather for a given city using the OpenWeatherMap API.

    Args:
        city (str): Name of the city to get weather for.

    Returns:
        str: Weather information or error message.
    """
    api_key = "049048adef5f0ac4aa3012b93db79b78"
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"  # Use "imperial" for Fahrenheit
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Extract weather details
        city_name = data["name"]
        temp = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        # Format the result
        return (
            f"Weather in {city_name}:\n"
            f"Temperature: {temp}°C\n"
            f"Condition: {weather_description.capitalize()}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} m/s"
        )

    except requests.exceptions.HTTPError:
        return "City not found. Please check the city name."
    except Exception as e:
        return f"An error occurred: {e}"


@tool(parse_docstring=True)
def get_latest_news(topic: str) -> str:
    """
    Fetches the latest news for a given topic.

    Args:
        topic (str): The topic to search for news articles.

    Returns:
        str: A formatted string containing the tool name, the latest news titles, and their respective links.
    Example:
        get_latest_news("Technology")
    """
    api_key = "e9c6d47717ab4738b733f4a8e15f9375"  # Replace with your actual API key
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={api_key}"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and data.get('articles'):
            articles = data['articles']
            result = f"Tool used: get_latest_news\n get_latest_news tool is used \nHere are the latest news articles related to {topic}:\n"

            for article in articles[:10]:  # Limiting to 5 articles
                title = article['title']
                url = article['url']
                result += f"- {title}: {url}\n"

            return result
        else:
            return f"Error: Could not fetch news for {topic}. Reason: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return f"Error: Unable to fetch news. Details: {str(e)}"


@tool(parse_docstring=True)
def get_movie_details(movie_name: str) -> str:
    """
    Fetches detailed information about a movie using its name.

    Args:
        movie_name (str): The name of the movie.

    Returns:
        str: A detailed summary of the movie, including title, year, genre, director, plot, and rating.
    Raises:
        Exception: If the movie is not found or the API request fails.
    """
    import requests

    api_key = "31f29fd0"  # Replace with your OMDB API key
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "True":
            title = data.get("Title", "N/A")
            year = data.get("Year", "N/A")
            genre = data.get("Genre", "N/A")
            director = data.get("Director", "N/A")
            plot = data.get("Plot", "N/A")
            imdb_rating = data.get("imdbRating", "N/A")

            return (
                f"Tool used: get_movie_details\n"
                f"Movie Details:\n"
                f"- Title: {title}\n"
                f"- Year: {year}\n"
                f"- Genre: {genre}\n"
                f"- Director: {director}\n"
                f"- Plot: {plot}\n"
                f"- IMDb Rating: {imdb_rating}/10"
            )
        else:
            return f"Tool used: get_movie_details\nMovie not found: {movie_name}"
    except Exception as e:
        return f"Tool used: get_movie_details\nError fetching movie details: {str(e)}"


@tool(parse_docstring=True)
def get_recipe(dish_name: str) -> str:
    """Fetches a recipe for a given dish name using the Spoonacular API.

    Args:
        dish_name (str): The name of the dish for which the recipe is to be fetched.

    Returns:
        str: The recipe with ingredients and instructions.
    """
    try:
        api_key = '716e3a77f3e841669be0a6974ff05b9b'  # Replace with your Spoonacular API key
        url = f"https://api.spoonacular.com/recipes/complexSearch?query={dish_name}&apiKey={api_key}&number=1"
        response = requests.get(url)
        data = response.json()

        if data.get('results'):
            recipe_id = data['results'][0]['id']
            recipe_title = data['results'][0]['title']

            # Fetch detailed recipe information
            details_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}"
            details_response = requests.get(details_url)
            details_data = details_response.json()

            ingredients = details_data.get('extendedIngredients', [])
            instructions = details_data.get('instructions', 'No instructions available.')

            # Create the recipe text
            recipe_text = f"Recipe for {recipe_title}:\n\nIngredients:\n"
            for ingredient in ingredients:
                recipe_text += f"- {ingredient['original']}\n"

            recipe_text += f"\nInstructions:\n{instructions}"

            return f"Tool used: get_recipe\n{recipe_text}"
        else:
            return f"Error: Could not find a recipe for {dish_name}. Try another dish name."
    except Exception as e:
        return f"Error: Unable to fetch recipe. Details: {str(e)}"


@tool
def get_distance(location1: str, location2: str) -> str:
    """
    Calculates the distance between two locations using the OpenCage Geocoder API.

    This function uses the OpenCage Geocoder API to get the geographic coordinates (latitude and longitude)
    of the provided locations, then computes the distance between the two points using the Haversine formula.

    Args:
        location1 (str): The first location (e.g., "New York").
        location2 (str): The second location (e.g., "Los Angeles").

    Returns:
        str: A message containing the calculated distance in kilometers between the two locations.

    Raises:
        Exception: If either location is invalid or the API requests fail.
    """

    api_key = "52420d959f5749cfbd67a5258d590195"  # Replace with your OpenCage API key

    # Geocode the origin location
    url1 = f"https://api.opencagedata.com/geocode/v1/json?q={location1}&key={api_key}"
    response1 = requests.get(url1)

    # Geocode the destination location
    url2 = f"https://api.opencagedata.com/geocode/v1/json?q={location2}&key={api_key}"
    response2 = requests.get(url2)

    # Check if both responses are successful
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()
        data2 = response2.json()

        # Extract latitude and longitude for both locations
        lat1, lon1 = data1['results'][0]['geometry']['lat'], data1['results'][0]['geometry']['lng']
        lat2, lon2 = data2['results'][0]['geometry']['lat'], data2['results'][0]['geometry']['lng']

        # Calculate the distance using the Haversine formula
        from math import radians, sin, cos, sqrt, atan2

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # Radius of the Earth in kilometers
        radius = 6371.0

        # Calculate the distance
        distance = radius * c

        return f"Tool used: get_distance\n get_distance tool is used to find The distance between {location1} and {location2} is {distance:.2f} km."

    else:
        return f"Error: Could not calculate the distance. Check if both locations are valid.\nTool used: get_distance"




tools = [calculator, get_weather, get_latest_news, get_movie_details, get_recipe, get_distance]

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=GOOGLE_API_KEY)

agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION)

# Streamlit app
st.sidebar.title("Function Calling Tools")
st.sidebar.write("Choose the tool to interact with:")
tools_list = [
    "Calculator", "Weather", "News", "Movie Details", "Recipe", "Distance"
]
selected_tool = st.sidebar.radio("Select a tool", tools_list)

# Update input field and button based on selected tool
if selected_tool == "Recipe":
    input_placeholder = "Please enter the recipe name"
    button_label = "Get Recipe Details"
elif selected_tool == "Weather":
    input_placeholder = "Enter the city or location"
    button_label = "Get Weather"
elif selected_tool == "News":
    input_placeholder = "Enter a topic for news"
    button_label = "Get News"
elif selected_tool == "Movie Details":
    input_placeholder = "Enter the movie name"
    button_label = "Get Movie Details"
elif selected_tool == "Distance":
    input_placeholder = "Enter locations to calculate distance"
    button_label = "Calculate Distance"
else:
    input_placeholder = "Enter your calculation"
    button_label = "Calculate"

st.title("Function Calling Tools")
st.write("Welcome to my App")

# Dynamic input field based on selected tool
user_input = st.text_input("Enter your prompt", placeholder=input_placeholder)

# Dynamic button text based on selected tool
if st.button(button_label):
    if selected_tool == "Calculator":
        response = agent.invoke(user_input)
    elif selected_tool == "Weather":
        response = agent.invoke(user_input)
    elif selected_tool == "News":
        response = agent.invoke(user_input)
    elif selected_tool == "Movie Details":
        response = agent.invoke(user_input)
    elif selected_tool == "Recipe":
        response = agent.invoke(user_input)
    elif selected_tool == "Distance":
        response = agent.invoke(user_input)

    st.write(response["output"])