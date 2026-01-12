# Project Outline & Architecture

**Status**: Initialization Phase
**Tech Stack**: Python 3.11+, discord.py, Poetry

## ⚠️ Development Rules
1.  **Consult this file first**: Before refactoring or deleting code, check the "Active Features" list to ensure the functionality is not critical.
2.  **Update before coding**: If a new feature is agreed upon, add it to the "Planned Features" section below before writing Python code.
3.  **Environment**: Never commit `.env` files.
4.  **Naming Registry**: Check the "Variable & Configuration Registry" section below before adding new environment variables or global constants.

## 1. Architecture Overview
*   **Dependency Management**: Handled strictly via Poetry (`pyproject.toml`).
*   **Configuration**: Environment variables loaded via `python-dotenv`.
*   **Modularity**: The bot uses `discord.ext.commands.Bot`. Features are separated into "Cogs" located in `src/cogs/` to keep `main.py` clean.
*   **Intents**: Requires "Message Content Intent" and "Server Members Intent" enabled in the Discord Developer Portal.

## 2. Feature Registry

### A. System Features (Core)
| Feature | Status | Description | File Location |
| :--- | :--- | :--- | :--- |
| **Bot Startup** |  Implemented | Connects to Discord Gateway and prints login info. | `src/main.py` |
| **Extension Loader** | 🟢 Implemented | Automatically loads files from `src/cogs/` on startup. | `src/main.py` |
| **Logging** | 🟢 Implemented | Basic console logging for errors and status. | `src/main.py` |
| **Sync Tree** | 🟢 Implemented | Syncs slash commands with Discord API. | `src/main.py` |
| **Database Manager** |  Implemented | Async SQLite connection handling. | `src/database.py` |
| **Global Error Handler** | 🟢 Implemented | Catches unhandled errors globally. | `src/main.py` |

### B. User Features (Commands)
| Feature | Status | Description | File Location |
| :--- | :--- | :--- | :--- |
| **General Cog** | 🟢 Implemented | Collection of general utility commands. | `src/cogs/general.py` |
| **Ping Command** | 🟢 Implemented | Hybrid command to check latency (Renamed to avoid conflicts). | `src/cogs/general.py` |
| **Purge Command** | 🟢 Implemented | Hybrid command to clear messages. | `src/cogs/general.py` |
| **Welcome Feature** | 🟢 Implemented | Sends a welcome message when a user joins. | `src/cogs/welcome.py` |
| **Advanced Logger** | 🟢 Implemented | Logs 7+ event types to hardcoded channels. | `src/cogs/logger.py` |
| **Info Cog** | 🟢 Implemented | User, Server, and Avatar info commands. | `src/cogs/info.py` |
| **Moderation Cog** | 🟢 Implemented | Kick, Ban, and Unban commands. | `src/cogs/moderation.py` |
| **Help Cog** | 🟢 Implemented | Custom help command listing cogs and commands. | `src/cogs/help.py` |

### C. Planned Features
| Feature | Priority | Description |
| :--- | :--- | :--- |
| **Warn System** | 🟡 Medium | Database-backed warning system. |

## 3. Variable & Configuration Registry

**Purpose**: Central source of truth for environment variables, global constants, and naming conventions to prevent conflicts.

### A. Environment Variables (`.env`)
| Key | Required | Description | Source File |
| :--- | :--- | :--- | :--- |
| `DISCORD_TOKEN` | **Yes** | Discord Bot Token | `src/main.py` |
| `DB_FILENAME` | No | Filename for SQLite DB (default: `database.db`) | `src/database.py` |

### B. Global Constants
| Constant | Value | Description | Location |
| :--- | :--- | :--- | :--- |
| `WELCOME_CHANNEL_ID` | `1425212093937881148` | Channel ID for welcome messages. | `src/config.py` |
| `LOG_CHANNEL_MESSAGES` | `1450676392118190181` | Logs edits, deletes, and images. | `src/config.py` |
| `LOG_CHANNEL_MEMBERS` | `1450677423988408410` | Logs joins, leaves, and profile updates. | `src/config.py` |
| `LOG_CHANNEL_MODERATION` | `1450676851331567627` | Logs bans, unbans, and kicks. | `src/config.py` |
| `LOG_CHANNEL_SERVER` | `1450752093899067465` | Logs roles, channels, and emojis updates. | `src/config.py` |
| `LOG_CHANNEL_VOICE` | `1450677163815604355` | Logs voice channel activity. | `src/config.py` |

### C. Naming Conventions
| Type | Convention | Example |
| :--- | :--- | :--- |
| **Cogs (Files)** | snake_case | `admin_commands.py` |
| **Cogs (Classes)** | PascalCase | `AdminCommands` |
| **Commands** | snake_case | `!ban_user` |
| **Variables** | snake_case | `user_id` |
| **Constants** | UPPER_CASE | `MAX_RETRIES` |