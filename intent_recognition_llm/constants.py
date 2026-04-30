"""Device control constants for AR glasses."""

DEVICE_COMMANDS_CODE_MAP = [
    # Contact functions
    {
        "code": "openContacts",
        "description": "Open contacts application",
        "command_demo": "Open contacts",
        "args": None,
    },
    {
        "code": "makePhoneCall",
        "description": "Make a phone call to specified contact",
        "command_demo": "Call John",
        "args": [
            {
                "name": "contact",
                "type": "str",
                "description": "Contact name or phone number",
            }
        ],
    },
    # Teleprompter functions
    {
        "code": "openTeleprompter",
        "description": "Open teleprompter",
        "command_demo": "Open teleprompter",
        "args": None,
    },
    # Message notification functions
    {
        "code": "openNotifications",
        "description": "Open message notifications",
        "command_demo": "Open notifications",
        "args": None,
    },
    # Translation functions
    {
        "code": "openTranslation",
        "description": "Open translation",
        "command_demo": "Open translation",
        "args": None,
    },
    # Compass functions
    {
        "code": "openCompass",
        "description": "Open compass",
        "command_demo": "Open compass",
        "args": None,
    },
    # Calendar functions
    {
        "code": "openCalendar",
        "description": "Open calendar",
        "command_demo": "Open calendar",
        "args": None,
    },
    # Real-time conversation functions
    {
        "code": "openRealTimeChat",
        "description": "Open real-time conversation",
        "command_demo": "Open real-time chat",
        "args": None,
    },
    # Settings functions
    {
        "code": "openSettings",
        "description": "Open settings",
        "command_demo": "Open settings",
        "args": None,
    },
    {
        "code": "setLanguage",
        "description": "Language settings",
        "command_demo": "Set language to English",
        "args": [
            {
                "name": "language",
                "type": "str",
                "description": "Language to set",
            }
        ],
    },
    # Music functions
    {
        "code": "openMusic",
        "description": "Open music application",
        "command_demo": "Open music",
        "args": None,
    },
    {
        "code": "playMusic",
        "description": "Play music",
        "command_demo": "Play music",
        "args": None,
    },
    {
        "code": "pauseMusic",
        "description": "Pause music",
        "command_demo": "Pause music",
        "args": None,
    },
    {
        "code": "previousTrack",
        "description": "Previous track",
        "command_demo": "Previous track",
        "args": None,
    },
    {
        "code": "nextTrack",
        "description": "Next track",
        "command_demo": "Next track",
        "args": None,
    },
    # Camera functions
    {
        "code": "openCamera",
        "description": "Open camera",
        "command_demo": "Open camera",
        "args": None,
    },
    {
        "code": "openVideoRecording",
        "description": "Open video recording",
        "command_demo": "Open video recording",
        "args": None,
    },
    {
        "code": "takePhoto",
        "description": "Take photo",
        "command_demo": "Take photo",
        "args": None,
    },
    {
        "code": "startVideoRecording",
        "description": "Start video recording",
        "command_demo": "Start recording",
        "args": None,
    },
    # Volume control functions
    {
        "code": "volumeUp",
        "description": "Increase volume",
        "command_demo": "Volume up",
        "args": None,
    },
    {
        "code": "volumeDown",
        "description": "Decrease volume",
        "command_demo": "Volume down",
        "args": None,
    },
    {
        "code": "muteVolume",
        "description": "Mute volume",
        "command_demo": "Mute",
        "args": None,
    },
    {
        "code": "unmuteVolume",
        "description": "Unmute volume",
        "command_demo": "Unmute",
        "args": None,
    },
    {
        "code": "setVolumeLevel",
        "description": "Set volume to specific level",
        "command_demo": "Set volume to 80",
        "args": [
            {
                "name": "level",
                "type": "int",
                "description": "Volume level 0-100",
            }
        ],
    },
    # Brightness control functions
    {
        "code": "brightnessUp",
        "description": "Increase brightness",
        "command_demo": "Brightness up",
        "args": None,
    },
    {
        "code": "brightnessDown",
        "description": "Decrease brightness",
        "command_demo": "Brightness down",
        "args": None,
    },

    {
        "code": "setBrightnessLevel",
        "description": "Set brightness to specific level",
        "command_demo": "Set brightness to 80",
        "args": [
            {
                "name": "level",
                "type": "int",
                "description": "Brightness level 0-100",
            }
        ],
    },
    {
        "code": "toggleAutoBrightness",
        "description": "Toggle automatic brightness",
        "command_demo": "Auto brightness",
        "args": None,
    },
    # Power functions
    {
        "code": "shutdown",
        "description": "Shutdown device",
        "command_demo": "Shutdown",
        "args": None,
    },
    # Screen functions
    {
        "code": "screenOff",
        "description": "Turn off screen",
        "command_demo": "Screen off",
        "args": None,
    },
]

DEVICE_COMMANDS_PROMPT = """You are a device control assistant.
Please analyze the user's instruction and return the corresponding command code and parameters (if needed).

Available device commands:
{commands_text}

Please note:
1. If the instruction requires controlling the volume level, please extract a 
   number between 0-100 from the instruction.
2. If the instruction requires controlling the brightness level, please extract a 
   number between 0-100 from the instruction.
3. Other commands do not require parameters.
4. The specific application name used by the user may not be exactly the same as 
   the application name in the device command list. Please determine the specific 
   application name based on the instruction.
5. If the instruction is to open an application not in the device command list 
   (such as Douyin, WeChat, etc.), please use command code `notSupported`.
6. All parameters should be returned as strings. For commands without parameters, 
   the parameter should be an empty string.
"""
