from pydantic import BaseModel
from google.genai import types
from core.constants import TOOL_CHAT, TOOL_EXTRACT

class Output(BaseModel):
    tool_name: str
    widget: str
    lang: str
    response: str

FUNCTION_DECLARATION_CHAT = [types.FunctionDeclaration(**d) for d in TOOL_CHAT]
TOOLBOX_CHAT = [types.Tool(function_declarations=FUNCTION_DECLARATION_CHAT)]

FUNCTION_DECLARATION_EXTRACT = [types.FunctionDeclaration(**d) for d in TOOL_EXTRACT]
TOOLBOX_EXTRACT = [types.Tool(function_declarations=FUNCTION_DECLARATION_EXTRACT)]

FAST_THINK = types.ThinkingConfig(thinking_budget=0, include_thoughts=False)
SLOW_THINK = types.ThinkingConfig(thinking_budget=-1, include_thoughts=False)
AUTOMATIC = types.AutomaticFunctionCallingConfig(disable=True)


class Config:
    def __init__(self, temperature: float = 0.1):
        self.temperature = temperature

    def base_config(self, system_text: str) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            tools=TOOLBOX_CHAT,
            system_instruction=system_text,
            thinking_config=FAST_THINK,
            temperature=self.temperature,
            automatic_function_calling=AUTOMATIC
        )

    def output_config(self, system_text: str = "") -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=system_text,
            thinking_config=FAST_THINK,
            temperature=self.temperature,
            response_mime_type="application/json",
            response_schema=Output
        )

    def extract_config(self, system_text: str) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            tools=TOOLBOX_EXTRACT,
            system_instruction=system_text,
            thinking_config=SLOW_THINK,
            temperature=self.temperature,
            automatic_function_calling=AUTOMATIC
        )