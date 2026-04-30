"""Control AR Glasses' Basic Functions"""

import os
import sys
from typing import Dict, Any, Optional
from loguru import logger
from dotenv import load_dotenv

from google import genai
from google.genai import types
from pydantic import BaseModel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from constants import (
        DEVICE_COMMANDS_PROMPT,
        DEVICE_COMMANDS_CODE_MAP,
    )
except ImportError:
    from constants import (
        DEVICE_COMMANDS_PROMPT,
        DEVICE_COMMANDS_CODE_MAP,
    )

load_dotenv()


class Command(BaseModel):
    """Command model for intent detection response"""
    command_code: str
    parameter: str


def _format_commands_text() -> str:
    """Format the commands list for inclusion in the prompt"""
    commands_text = ""
    for cmd in DEVICE_COMMANDS_CODE_MAP:
        commands_text += f"Code: {cmd['code']} - {cmd['description']}"
        if cmd["args"]:
            args_desc = ", ".join(
                [
                    f"{arg['name']} ({arg['type']}): {arg['description']}"
                    for arg in cmd["args"]
                ]
            )
            commands_text += f" - Arguments: {args_desc}"
        commands_text += f" - Example: \"{cmd['command_demo']}\"\n"
    return commands_text


class ARGlassesIntentDetector:
    """
    MCP Server component for detecting user intentions to control AR glasses
    using Google's Gemini model.
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 gemini_client: Optional[genai.Client] = None,
                 vertexai: bool = False):
        if gemini_client is not None:
            self.client = gemini_client
        else:
            if not api_key:
                api_key = os.getenv("GEMINI_API_KEY")
            self.client = genai.Client(api_key=api_key, vertexai=vertexai)
        self.aclient = self.client.aio

    def detect_intent(self, user_instruction: str) -> Dict[str, Any]:
        """
        Detect the user's intent from a natural language instruction
        using Google's Gemini model.
        """
        # Format prompt with user instruction
        formatted_prompt = DEVICE_COMMANDS_PROMPT.format(
            commands_text=_format_commands_text()
        )

        # Call Gemini API
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[types.Content(parts=[types.Part(text=user_instruction)])],
            config=types.GenerateContentConfig(
                system_instruction=formatted_prompt,
                response_mime_type="application/json",
                response_schema=list[Command],
            ),
        )

        try:
            commands_list = response.parsed
            logger.info(f"Commands list: \n{commands_list}")

            results = []
            for command in commands_list:
                try:
                    results.append(command.model_dump())
                except Exception as e:
                    logger.error(f"Failed to parse command: {command}\n{str(e)}")
                    command_dict = command.model_dump()
                    command_dict["message"] = str(e)
                    results.append(command_dict)
            return {"status": "success", "content": results}
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to parse intent detection response: {str(e)}",
                "raw_response": getattr(response, "text", str(response))
            }

    async def a_detect_intent(self, user_instruction: str) -> Dict[str, Any]:
        """Async version using the Gemini aio client."""
        formatted_prompt = DEVICE_COMMANDS_PROMPT.format(
            commands_text=_format_commands_text()
        )

        response = None
        try:
            response = await self.aclient.models.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Content(parts=[types.Part(text=user_instruction)])],
                config=types.GenerateContentConfig(
                    system_instruction=formatted_prompt,
                    response_mime_type="application/json",
                    response_schema=list[Command],
                ),
            )
            commands_list = response.parsed
            logger.info(f"Commands list: \n{commands_list}")

            results = []
            for command in commands_list:
                try:
                    results.append(command.model_dump())
                except Exception as e:
                    command_dict = command.model_dump()
                    command_dict["message"] = str(e)
                    results.append(command_dict)
            return {"status": "success", "content": results}
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to parse intent detection response: {str(e)}",
                "raw_response": getattr(response, "text", str(response)) if "response" in locals() else str(e),
            }


if __name__ == "__main__":
    import asyncio
    import time

    start_time = time.time()

    async def main():
        """test main function"""
        detector = ARGlassesIntentDetector()
        result = await detector.a_detect_intent("i wanna to check the direction")
        print(result)

    asyncio.run(main())

    end_time = time.time()

    print(f"Execution time: {end_time - start_time} seconds")
