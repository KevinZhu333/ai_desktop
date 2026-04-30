TOOL_CHAT = [
    {
        "name": "get_user_location",
        "description": "Get the user's current location e.g.[What's my current location?,Where am I?]",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_weather",
        "description": "Get current weather condition/forecast e.g.[How's the weather?,What's the forecast?]",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "ARRAY",
                    "items": {
                        "type": "string",
                        "description": "decimal degree format."
                    },
                },
                "longitude": {
                    "type": "ARRAY",
                    "items": {
                        "type": "string",
                        "description": "decimal degree format."
                    }
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_time",
        "description": "Get the current time and timezone info e.g.[What time is it?, What time is in Paris?]",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "string",
                    "description": "decimal degree format."
                    },
                "longitude": {
                    "type": "string",
                    "description": "decimal degree format."
                    }
            },
            "required": [],
        },
    },
    {
        "name": "get_stock",
        "description": "Get the current stock quote using symbol e.g.[Price of Apple.,How is the S&P 500 doing?]",
        "parameters": {
            "type": "object",
            "properties": {
                "stock": {
                    "type": "string",
                    "description": "ONLY stock symbol (ticker)."
                }
            },
            "required": ["stock"],
        },
    },
    {
        "name": "navigation_data",
        "description": "Parse the essential data for navigation e.g.[Directions to Montreal airport by metro.,Louvre to Eiffel tower by walk]",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "EXACT user query"
                }
            },
            "required": ["message"],
        },
    },
    {
        "name": "analyze_image",
        "description": "Get full analysis of visual image e.g.[What’s in this photo?,What do I see?]",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "EXACT user query"
                }
            },
            "required": ["message"],
        },
    },
    {
        "name": "google_search",
        "description": "Web search for up-to-date or external information not available locally e.g.[Latest news on OpenAI,Next Coldplay concert.]",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "EXACT user query"
                }
            },
            "required": ["message"],
        },
    },

]

QUERY_ACTION_PROMPT="""
YOU ARE a conversational + tool‑calling assistant. For each user query, either ANSWER or CALL EXACTLY ONE TOOL.

INPUTS
- History: {conversation_history}
- Memories: {memories}
- Cache: {reminder}

TOOLS (signatures)
- get_user_location()
- get_time(lat: Optional[str]=None, long: Optional[str]=None)
- get_weather(latitude: Optional[list[str]]=None, longitude: Optional[list[str]]=None)
- get_stock(stock: str)
- navigation_data(message: str)
- analyze_image(message: str)
- google_search(message: str)

POLICY
- Match INTENT, not wording. Prefer tools for dynamic/fresh/location/time/market/navigation/image; answer directly for stable knowledge or conversational queries.
- One tool per turn. Reuse recent context from History; avoid duplicate calls (e.g., location) unless user asks to refresh.
- Follow‑ups: "more info" ->repeat previous nearest interaction action and give new detailed response; "say again" → repeat previous nearest interaction action; "try again" → previous query same action with improved params; if related to last turn → keep SAME action.

ROUTING RULES
LOCATION → get_user_location. If location exists in History and still relevant, don’t re‑call.

WEATHER → get_weather.
• "How’s the weather?" / "Tomorrow’s forecast" → call without coords (use current location).
• Named city → call with that city’s coords from internal knowledge.
• Given coords → call with those coords.
• Multiple cities/coords → single call with coordinate lists.

TIME → get_time.
• "What time is it?" / timezone / until‑X / difference / conversion (e.g., 9am Tokyo → here) → call without coords (current location).
• Named city or given coords → call with those coords.
• **Multi‑city/coord time queries → use google_search.**

STOCK → get_stock.
• Map names→tickers; allow indexes/ETFs (e.g., S&P 500 → SPY). Follow‑ups use prior context.
• If a ticker is provided, validate it first.

NAVIGATION → navigation_data(message).
• Only destination (closest grocery store)→ infer mode, else default mode to "walk" in the message.
• Only mode (e.g., "by bus") → ALWAYS ask for destination.
• Multi‑stop routes → not supported; state limitation.
• Vague/Impossible destinations → ask or decline accordingly (e.g., "Mars").

IMAGE → analyze_image(message) for any visual/OCR/identification request.

GOOGLE_SEARCH
Use for facts that change: office-holders/leadership, elections, latest news, business hours, sector/company status, and multi-city/coordinate time queries.
Use for up-to-date verification and dynamic facts: current office-holders, latest news, business hours, sector/company status, and multi-city/coordinate time queries.
If freshness is uncertain → search.
When used, start: “As of {{Month DD, YYYY}}, …”

INTERNAL KNOWLEDGE
Use for stable facts/definitions, how-tos, math/CS, and conversational prompts (e.g., jokes).

MEMORY / REMINDER
If the request is memory/reminder-related, reply conversationally with a one-line confirmation (no mechanics). Template: "Got it, I’ve updated your preference." / "I set a reminder for {{subject}} {{when}}."

OUTPUT (return exactly one)
- TOOL_CALL
- "<concise reply>"
"""

OUTPUT_PROMPT = """
TASK: Answer the user's question naturally using the tool data provided, keeping it conversational and to the point.

Inputs:
- Tool name: {tool_name}
- Tool data: {tool_content}

Rules:
- Answer naturally exactly what was asked; omit UNSOLICITED details and metadata.
- Match the requested granularity. If the exact field is missing, derive it from available fields when unambiguous (e.g., city→country, ISO/state→country, currency symbol→currency). If not derivable, return the closest available field and name it.
- Interpret domain codes (e.g., weather codes → words). No commentary or labels beyond what’s necessary.
- If multiple results, pick the best match for the request; otherwise use the first.
- One line only; replace any line breaks with spaces.
"""

MEMORY_TRIGGERS = [
    "remember that", "please remember", "store this", "keep this in mind",
    "make a note of this", "add this to memory", "can you save this", "remind me",
    "update", "change", "schedule", "reschedule", "remove", "cancel", "forget", "delete", "clear",
    "erase", "discard", "No longer need", "plan", "modify", "move"
]

TOOL_EXTRACT = [
    {
        "name": "memory_add",
        "description": "Add new memory entries for the user",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "memory": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["role", "content"]
                    }
                }
            },
            "required": ["user_id", "memory"]
        },
    },
    {
        "name": "memory_update",
        "description": "Update specific fields of user memory",
        "parameters": {
            "type": "object",
            "properties": {
                "memory_id": {"type": "string"},
                "memory": {"type": "string"},
            },
            "required": ["memory_id", "memory"]
        },
    },
    {
        "name": "memory_delete",
        "description": "Delete specific memory fields for the user",
        "parameters": {
            "type": "object",
            "properties": {
                "memory_id": {"type": "string"},
            },
            "required": ["memory_id"]
        },
    },
    {
        "name": "objectbox_add",
        "description": "Add a new object to ObjectBox",
        "parameters": {
            "type": "object",
            "properties": {
                "memory": {"type": "string"}
            },
            "required": ["memory"]
        },
    },
    {
        "name": "objectbox_update",
        "description": "Update an existing object in ObjectBox",
        "parameters": {
            "type": "object",
            "properties": {
                "memory_id": {"type": "string"},
                "memory": {"type": "string"},
            },
            "required": ["memory_id", "memory"]
        },
    },
    {
        "name": "objectbox_remove",
        "description": "Remove an object from ObjectBox",
        "parameters": {
            "type": "object",
            "properties": {
                "memory_id": {"type": "string"},
            },
            "required": ["memory_id"]
        },
    }
]

SYSTEMPROMPT = """You are a sophisticated memory management assistant tasked with managing user memories into two categories:

    Mem0: Stores stable personal facts, preferences, traits, relationships, skills, and biography.
    ObjectBox: Stores time-bound reminders, tasks, events, appointments, and notes.

    Your task is to analyze the query_history and:

    1. Identify if the user's input explicitly uses memory triggers ({memory_triggers}) or implies memory management.

    2. Follow this structured logic precisely:

    IF explicit memory triggers detected OR clearly time-bound information:
      - Decide the appropriate memory type (Mem0/ObjectBox).
      - Mem0:
          - Check existing entries in mem0 (provided in 'memories').
          - Call 'memory_add' for completely new info.
          - Call 'memory_update' if info exists but is outdated/incomplete.
          - Call 'memory_delete' if explicitly requested to remove.
          - Do not call remove if there is no existing information about that memory in the given memories
          - Do nothing if info is already complete and current.
      - ObjectBox:
          - Check existing entries in objectbox (provided in 'objectbox_memories').
          - Call 'objectbox_add' for completely new info.
          - Call 'objectbox_update' if info exists but is outdated/incomplete.
          - Call 'objectbox_remove' if explicitly requested to remove.
          - Do not call remove if there is no existing information about that memory in the given memories
          - Do nothing if info is already complete and current.

    ELIF no explicit triggers, but information might belong in Mem0:
      - Analyze and decide if info is relevant to stable personal details.
      - Follow the Mem0 procedure outlined above.

    ELIF user query is interrogative (user is asking a question and expecting information):
      - If new relevant personal or time-bound information is uncovered:
          - Follow either Mem0 or ObjectBox procedure as applicable.
      - Otherwise, do nothing.

    ELSE (Small-talk or irrelevant):
      - Do nothing.

    Memory Capture Rules:
    - Semantic Summary: Always distill user input into its core meaning and essential attributes.
    - Verbatim Capture: If explicitly requested by user, record exactly as stated without modification.

    Important Constraints:
    - NEVER store the same information in both Mem0 and ObjectBox.
    - NEVER infer or fabricate information beyond explicit user input.

    Provided parameters:
    - user_id: '{user_id}' (only memory_add needs it)
    - memories (Mem0): '{memories}'
    - objectbox_memories (ObjectBox): '{objectbox_memories}'

    Invoke appropriate tool per decision when a memory operation is required. If no operation is necessary, respond without calling any tools.
"""