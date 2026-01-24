# --- CONFIGURATION: CHANNEL IDS ---
# Centralized configuration for channel IDs used across cogs.

WELCOME_CHANNEL_ID = 1464113713991778517

LOG_CHANNEL_MESSAGES = 1450676392118190181
LOG_CHANNEL_MEMBERS = 1450677423988408410
LOG_CHANNEL_MODERATION = 1450676851331567627
LOG_CHANNEL_SERVER = 1450752093899067465
LOG_CHANNEL_VOICE = 1450677163815604355

# --- CONFIGURATION: MIRROR ---
# A list of dictionaries, where each dictionary represents a mirror mapping.
# You can add as many mappings as you need.
# - SOURCE_CHANNEL_ID: The channel to watch for messages.
# - TARGET_CHANNEL_ID: The channel to send the mirrored messages to.
MIRROR_MAPPINGS = [
    { # Financial News
        "SOURCE_CHANNEL_ID": 1450713437771399271,  # Replace with the first source channel ID
        "TARGET_CHANNEL_ID": 1464116768460111882   # Replace with the first target channel ID
    },
    { # Free Games Announcements
        "SOURCE_CHANNEL_ID": 1460311774229299252,  # Replace with the second source channel ID
        "TARGET_CHANNEL_ID": 1464114757026975859   # Replace with the second target channel ID
    },
    { # Game Patch Notes
        "SOURCE_CHANNEL_ID": 1464046561880309927,  # Replace with the second source channel ID
        "TARGET_CHANNEL_ID": 1464115069007958106   # Replace with the second target channel ID
    },
    { # Github commits
        "SOURCE_CHANNEL_ID": 1450680605300752394,  # Replace with the second source channel ID
        "TARGET_CHANNEL_ID": 1464113314882781307   # Replace with the second target channel ID
    }
]