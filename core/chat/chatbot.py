import os
from typing import Optional
from google import genai
from dotenv import load_dotenv
from core.constants import QUERY_ACTION_PROMPT, OUTPUT_PROMPT
from services.dispatcher import Dispatcher
from core.llm_runtime import Config

load_dotenv()

def _fmt_tool_prompt(conversation_history, memories, reminder) -> str:
    return QUERY_ACTION_PROMPT.format(
        conversation_history=conversation_history,
        memories=memories,
        reminder=reminder
    )

def _fmt_output_prompt(tool_name, tool_content) -> str:
    return OUTPUT_PROMPT.format(
        tool_name=tool_name,
        tool_content=tool_content
    )

class ExchangeMessages:

    def __init__(
            self,
            dispatcher: Optional[Dispatcher] = None,
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

        self.dispatch = dispatcher or Dispatcher()
        self.config = Config(temperature=0.1)

    def exchange_messages(self, query: str, history: list, query_history: list, memories: list, reminder: list):

        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents = query,
            config=self.config.base_config(_fmt_tool_prompt(history, memories, reminder))
        )

        if response.text:
            response = response.text.strip()
        else:
            name=""
            tool_content = {}
            for part in response.candidates[0].content.parts:
                name = part.function_call.name
                args = part.function_call.args

                tool_content = self.dispatch.function_call(name, args)
                if name in ("navigation_data", "analyze_image"):

                    history.append([{"role": "user", "content": query}, {"role": "assistant", "content": tool_content}])

                    return tool_content

            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=query,
                config=self.config.output_config(_fmt_output_prompt(name, tool_content))
            ).text.strip()

        history.append([{"role": "user", "content": query}, {"role": "assistant", "content": response}])
        query_history.append({"role": "user", "content": query})

        return response


if __name__ == "__main__":
    chat = ExchangeMessages()
    his = []
    q_history = []
    mem = []
    rem=[]
    answer = chat.exchange_messages("How's the weather", history=his, query_history=q_history, memories=mem, reminder=rem)
    print(answer)