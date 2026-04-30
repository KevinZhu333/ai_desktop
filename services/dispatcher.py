import requests
from typing import Optional

from google import genai

from dotenv import load_dotenv
load_dotenv()

from services.context_service import ContextService
from services.memory_service import MemoryService

class Dispatcher:
    def __init__(
        self,
        *,
        mem0_api_key: Optional[str] = None,
        objectbox_path: Optional[str] = None,

        gemini_api_key: Optional[str] = None,
        gemini_client: Optional[genai.Client] = None,
        ipgeo_api_key: Optional[str] = None,
        stock_api_key: Optional[str] = None,
        vertexai: bool = False,

        memory_service: Optional[MemoryService] = None,

        session: Optional[requests.Session] = None,
        default_timeout: float | tuple[float, float] = (3.0, 5.0),
        user_agent: str = "ai-agent/0.1",
    ) -> None:
        self.memory_service = memory_service or MemoryService(mem0_api_key=mem0_api_key, path=objectbox_path)
        self.context_service = ContextService(
            gemini_api_key=gemini_api_key,
            gemini_client=gemini_client,
            ipgeo_api_key=ipgeo_api_key,
            stock_api_key=stock_api_key,
            vertexai=vertexai,
            session=session,
            default_timeout=default_timeout,
            user_agent=user_agent,
        )

        self.DISPATCH = {
            # --- Mem0 ---
            "memory_add":         lambda args=None: self.memory_service.memory_add(**(args or {})),
            "memory_update":      lambda args=None: self.memory_service.memory_update(**(args or {})),
            "memory_delete":      lambda args=None: self.memory_service.memory_delete(**(args or {})),
            "memory_retrieve":    lambda args=None: self.memory_service.memory_retrieve(**(args or {})),
            # --- ObjectBox ---
            "objectbox_add":      lambda args=None: self.memory_service.objectbox_add(**(args or {})),
            "objectbox_update":   lambda args=None: self.memory_service.objectbox_update(**(args or {})),
            "objectbox_remove":   lambda args=None: self.memory_service.objectbox_remove(**(args or {})),
            "objectbox_retrieve": lambda args=None: self.memory_service.objectbox_retrieve(**(args or {})),
            "objectbox_get_all": lambda args=None: self.memory_service.objectbox_get_all(),
            # --- External / Gemini / APIs ---
            "get_user_location":  lambda args=None: self.context_service.get_user_location(),
            "get_weather":        lambda args=None: self.context_service.get_weather(**(args or {})),
            "get_time":           lambda args=None: self.context_service.get_time(**(args or {})),
            "get_stock":          lambda args=None: self.context_service.get_stock(**(args or {})),
            "navigation_data":    lambda args=None: self.context_service.navigation_data(**(args or {})),
            "analyze_image":      lambda args=None: self.context_service.analyze_image(**(args or {})),
            "google_search":      lambda args=None: self.context_service.google_search(**(args or {}))
        }

    def function_call(self, name: str, args = None):
        fn = self.DISPATCH.get(name)
        if not fn:
            return {"error": f"Unknown function '{name}'"}
        return fn(args)

    def close(self) -> None:
        self.memory_service.objectbox_close()

if __name__ == "__main__":
    # ------------ TESTING CONNECTION ----------------
    dispatch = Dispatcher()
    answer1 = dispatch.function_call("memory_add", {"memory": "memory", "user_id": "user_id"})
    answer2 = dispatch.function_call("memory_update", {"memory": "memory", "memory_id": "memory_id"})
    answer3 = dispatch.function_call("memory_delete", {"memory_id": "memory_id"})
    answer4 = dispatch.function_call("memory_retrieve", {"user_id": "user_id"})

    answer5 = dispatch.function_call("objectbox_add", {"memory": "memory"})
    answer6 = dispatch.function_call("objectbox_update", {"memory": "memory", "memory_id": "memory_id"})
    answer7 = dispatch.function_call("objectbox_remove", {"memory_id": "memory_id"})
    answer8 = dispatch.function_call("objectbox_retrieve", {"query": "query"})
    answerX = dispatch.function_call("objectbox_get_all", None)

    answer9 = dispatch.function_call("analyze_image", {"message": "What am I seeing?"})
    answer10 = dispatch.function_call("get_user_location", None)
    answer11 = dispatch.function_call("navigation_data", {"message": "Direction to Eiffel Tower by bike"})
    answer12 = dispatch.function_call("get_stock", {"stock": "AAPL"})
    answer13 = dispatch.function_call("get_time", None)
    answer14 = dispatch.function_call("get_time", {"latitude": "1", "longitude": "1"})
    answer15 = dispatch.function_call("get_weather", None)
    answer16 = dispatch.function_call("get_weather", {"latitude": "1", "longitude": "1"})
    answer17 = dispatch.function_call("google_search", {"message": "latest news on AIR CANADA strikes"})

    print(answer1)
    print(answer2)
    print(answer3)
    print(answer4)
    print(answer5)
    print(answer6)
    print(answer7)
    print(answer8)
    print(answer9)
    print(answer10)
    print(answer11)
    print(answer12)
    print(answer13)
    print(answer14)
    print(answer15)
    print(answer16)
    print(answer17)
    print(answerX)