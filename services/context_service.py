import os
from typing import Optional, Literal, Any, Dict
import requests
from google.genai import types
from google import genai
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

class ContextService:
    """
    Class wrapper for the helper functions that interact with Gemini, IP Geolocation,
    Open-Meteo, and Alpha Vantage. Method names/behavior mirror the originals.
    """

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        gemini_client: Optional[genai.Client] = None,
        ipgeo_api_key: Optional[str] = None,
        stock_api_key: Optional[str] = None,
        vertexai: bool = False,
        *,
        session: Optional[requests.Session] = None,
        default_timeout: float | tuple[float, float] = (3.0, 5.0),
        user_agent: str = "ai-agent/0.1",
    ):
        if not ipgeo_api_key:
            ipgeo_api_key = os.getenv("IPGEO_API_KEY")
        if not stock_api_key:
            stock_api_key = os.getenv("STOCK_API_KEY")
        if gemini_client is not None:
            self.gemini_client = gemini_client
        else:
            if not gemini_api_key:
                gemini_api_key = os.getenv("GEMINI_API_KEY")
            self.gemini_client = genai.Client(api_key=gemini_api_key, vertexai=vertexai)

        self.ipgeo_api_key = ipgeo_api_key
        self.stock_api_key = stock_api_key

        self.default_timeout = default_timeout
        self._session = session or requests.Session()
        self._session.headers.update({"User-Agent": user_agent})

    def _get(self, url: str, **kw) -> requests.Response:
        kw.setdefault("timeout", self.default_timeout)
        return self._session.get(url, **kw)

    def analyze_image(self, message: str) -> str:
        """
        Analyze a local image file and generate a textual description using the Gemini API.

        NOTE: Uses the same hardcoded path as the original function. Adjust as needed.
        """
        class ImageContent(BaseModel):
            image_title: str
            description: str

        my_file = self.gemini_client.files.upload(
            file="/home/zhujianwen/images/mandelaquote.jpg"
        )

        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[my_file, f"{message}"],
            config={
                "response_mime_type": "application/json",
                "response_schema": ImageContent
            }
        ).text

        return response

    def get_user_location(self) -> Dict[str, Any]:
        """
        Retrieve the current geographical location of the user based on their IP address.

        Uses the IP Geolocation API to fetch the user's latitude, longitude, and city.

        Returns:
            dict: A dictionary containing the user's location data, including latitude,
                  longitude, and city name.
        """
        url = "https://api.ipgeolocation.io/v2/ipgeo"
        params = {
            "apiKey": self.ipgeo_api_key,
            "fields": "location.latitude,location.longitude,location.city,location.country_name,time_zone.name",
        }
        response = self._get(url, params=params)
        location = response.json()["location"]
        return location

    def navigation_data(self, message: str) -> str:
        """
        Parse a user's navigation query into structured navigation data.

        The function sends the user's query to the Gemini API, requesting a JSON response
        containing the destination and mode of transportation.

        Args:
            message (str): The user's navigation-related query.

        Returns:
            str: A JSON-formatted string containing the destination and mode of transport.
        """
        class NavData(BaseModel):
            destination: str
            mode_transport: Literal["drive", "walk", "bike", "transit", "UNKNOWN"]

        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{message}",
            config={
                "response_mime_type": "application/json",
                "response_schema": NavData,
            },
        ).text

        return response

    def get_stock(self, stock: str) -> Dict[str, Any]:
        """
        Retrieve the latest stock market data for a given stock symbol.

        Uses the Alpha Vantage API to fetch real-time quote data for the specified stock.

        Args:
            stock (str): The stock ticker symbol (e.g., 'AAPL', 'GOOGL').

        Returns:
            dict: A dictionary containing real-time market data for the stock.
        """
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": stock,
            "apikey": self.stock_api_key,
        }
        response = self._get(url, params=params)
        return response.json()

    def get_time(
            self,
            latitude: Optional[str] = None,
            longitude: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve the current time and timezone information for the user's location.

        Uses the IP Geolocation API to determine the user's timezone and current local time.

        Returns:
            dict: A dictionary containing the timezone name and current date-time string.
        """
        url = "https://api.ipgeolocation.io/v2/timezone"
        params = {"apiKey": self.ipgeo_api_key}

        if latitude is not None and longitude is not None:
            params.update({"lat": latitude, "long": longitude})

        response = self._get(url, params=params)
        return response.json()

    def get_weather(
        self,
        latitude: Optional[list[str]] = None,
        longitude: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve current and daily weather data for the user's location.

        Uses the Open-Meteo API to fetch weather data (including current temperature,
        precipitation, and forecasts) based on the user's latitude and longitude.

        Returns:
            dict: A dictionary containing current and forecast weather information.
        """
        url = "https://api.open-meteo.com/v1/forecast"

        if latitude is None and longitude is None:
            coord = self.get_user_location()
            latitude = float(coord["latitude"])
            longitude = float(coord["longitude"])

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "weather_code",
                "precipitation_probability_max",
                "precipitation_sum",
                "temperature_2m_max",
                "temperature_2m_min",
            ],
            "current": ["temperature_2m",
                        "apparent_temperature",
                        "weather_code",
                        "precipitation"],
            "timezone": "auto",
        }

        response = self._get(url, params=params)
        return response.json()

    def google_search(self, message: str) -> str:
        """
        Perform a Google search using the Gemini API's Google Search tool.

        Configures the Gemini API with the Google Search tool, executes the search query,
        and returns the results as a text string.

        Args:
            message (str): The user's search query.

        Returns:
            str: The search results returned by the Gemini API.
        """
        grounding_tool = types.Tool(google_search=types.GoogleSearch())

        generate_content_config = types.GenerateContentConfig(
            tools=[grounding_tool],
            thinking_config=types.ThinkingConfig(thinking_budget=0, include_thoughts=False),
            temperature=0.1,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
        )

        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message,
            config=generate_content_config
        ).text

        return response
