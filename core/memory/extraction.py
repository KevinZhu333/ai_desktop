import os
from typing import Optional
from google import genai

from core.constants import SYSTEMPROMPT, MEMORY_TRIGGERS
from core.llm_runtime import Config
from services.dispatcher import Dispatcher


def _fmt_extract_prompt(user_id, memory_triggers, memories, objectbox_memories) -> str:
    formatted_prompt = SYSTEMPROMPT.format(
        user_id=user_id,
        memory_triggers=memory_triggers,
        memories=memories,
        objectbox_memories=objectbox_memories,
    )
    return formatted_prompt

class Extraction:

    def __init__(
            self,
            dispatcher: Dispatcher,
            gemini_api_key: Optional[str] = None,
            gemini_client: Optional[genai.Client] = None,
            vertexai: bool = False,
    ):
        if gemini_client is not None:
            self.gemini_client = gemini_client
        else:
            if not gemini_api_key:
                gemini_api_key = os.getenv("GEMINI_API_KEY")
            self.gemini_client = genai.Client(api_key=gemini_api_key, vertexai=vertexai)

        self.dispatch = dispatcher
        self.config = Config(temperature=0.1)

    def extracting(self, query_history, memories, user_id) -> None:
        objectbox_memories = [
            {"id": doc.id, "memory": doc.content}
            for doc in self.dispatch.function_call("objectbox_get_all", None)
        ]

        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents = f"{query_history}",
            config=self.config.extract_config(_fmt_extract_prompt(user_id, MEMORY_TRIGGERS, memories, objectbox_memories))
        )

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if not part.function_call:
                    continue

                name = part.function_call.name
                args = part.function_call.args

                self.dispatch.function_call(name, args)

        return