import asyncio
import os
import time
from typing import Optional
from dotenv import load_dotenv
from google import genai

from core.memory.extraction import Extraction
from intent_recognition_llm.device_controller import ARGlassesIntentDetector
from core.chat.chatbot import ExchangeMessages
from services.dispatcher import Dispatcher
from services.memory_service import MemoryService

load_dotenv()


class Chat:
    def __init__(
            self,
            gemini_api_key: Optional[str] = None,
            vertexai: bool = False
    ):
        if not gemini_api_key:
            gemini_api_key = os.getenv("GEMINI_API_KEY")

        self.gemini_client = genai.Client(api_key=gemini_api_key, vertexai=vertexai)
        # self.aclient = self.gemini_client.aio

        self.detector = ARGlassesIntentDetector()

        self.memory_service = MemoryService()
        self.dispatch = Dispatcher(memory_service=self.memory_service)
        self.extractor = Extraction(dispatcher=self.dispatch, gemini_client=self.gemini_client)
        self.exchanger = ExchangeMessages(dispatcher=self.dispatch, gemini_client=self.gemini_client)

    def chat(self, user_id: str, query: str, history: Optional[list] = None):
            if not user_id: raise ValueError("401 AUTHENTICATION Failed: Need User ID")
            if not query: raise ValueError("400 INPUT ERROR: Please input a query")
            if history is None: history = []
            query_history: list = []

            intention = self.detector.detect_intent(query)

            if isinstance(intention, dict) and intention.get("status") == "success":
                content = intention.get("content", [])
                if content and content[0].get("command_code") != "notSupported":
                    return intention

            memories = self.dispatch.function_call("memory_retrieve", {"user_id": user_id})
            reminder = self.dispatch.function_call("objectbox_retrieve", {"query": query})

            response = self.exchanger.exchange_messages(
                query=query,
                history=history,
                query_history=query_history,
                memories=memories,
                reminder=reminder
            )

            self.extractor.extracting(
                query_history=query_history,
                memories=memories,
                user_id=user_id
            )

            self.dispatch.close()
            return {"response": response, "history": history}


if __name__ == "__main__":
    chat = Chat()

    answer = chat.chat("Test", "I like blue")
    print(answer)