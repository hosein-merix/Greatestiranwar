# Political War Bot - Replit.md

## Overview

This is a Telegram bot for a political war game written in Python. Players can join political parties, manage their resources (coins, soldiers), and engage in strategic gameplay across different Iranian regions. The bot uses the python-telegram-bot library for Telegram integration and JSON files for data persistence.

## System Architecture

### Backend Architecture
- **Language**: Python 3.x
- **Framework**: python-telegram-bot library for Telegram API integration
- **Data Storage**: JSON file-based storage system
- **Structure**: Single-file monolithic architecture with modular helper functions

### Data Storage Strategy
- **Type**: File-based JSON storage
- **Location**: `data/` directory
- **Files**: 
  - `parties.json`: Stores political party information
  - `players.json`: Stores player profiles and game state
- **Rationale**: Simple, lightweight solution for small-scale bot without database overhead

### Bot Architecture
- **Commands**: `/start` and `/join` commands for user interaction
- **Callbacks**: Inline keyboard callbacks for party selection
- **Event Handling**: Asynchronous message and callback handlers

## Key Components

### 1. Player Management System
- **Player Creation**: Automatic player registration on first interaction
- **Player Data**: ID, coins (starting: 1000), party affiliation, location, investments, soldiers
- **Default Location**: Tehran (تهران)

### 2. Political Party System
- **Pre-configured Parties**: 11 political parties across different Iranian regions
- **Party Structure**: ID, name, region, members list, soldier count, companies
- **Regional Distribution**: Each party controls a specific region (Tehran, Hamedan, Fars, etc.)

### 3. Game Mechanics
- **Currency System**: Coin-based economy starting with 1000 coins per player
- **Military System**: Soldier recruitment and management
- **Investment System**: Player investment tracking
- **Party Membership**: One-time party joining mechanism

### 4. Telegram Integration
- **Bot Token**: Environment variable with fallback hardcoded token
- **Channel Subscription**: Required subscription to @Nonobodynonono
- **UI Elements**: Inline keyboards for interactive party selection
- **Access Control**: Player authorization system with admin management

## Data Flow

1. **Player Registration**: User sends `/start` → Bot creates player profile → Welcome message
2. **Party Selection**: User sends `/join` → Bot displays party list → User selects party → Membership confirmed
3. **Data Persistence**: All interactions update JSON files immediately
4. **Game State**: Player and party data maintained across bot restarts

## External Dependencies

### Python Libraries
- `python-telegram-bot`: Telegram Bot API wrapper
- `json`: Built-in JSON handling
- `os`: Environment variable and file system operations

### External Services
- **Telegram Bot API**: Core messaging and interaction platform
- **Channel Subscription**: @Nonobodynonono channel for user verification

## Deployment Strategy

### Environment Configuration
- **Bot Token**: Configurable via `BOT_TOKEN` environment variable
- **Data Directory**: Local `data/` folder for JSON storage
- **Error Handling**: Basic file I/O error handling with fallback mechanisms

### File Structure
```
/
├── main.py              # Main bot application
├── data/
│   ├── parties.json     # Political parties data
│   └── players.json     # Player profiles
└── attached_assets/     # Backup/reference files
```

### Deployment Requirements
- Python 3.x runtime
- Write permissions for data directory
- Network access for Telegram API
- Environment variable support for bot token

## Changelog

```
Changelog:
- July 01, 2025. Initial setup and bot deployment
  * Successfully installed python-telegram-bot==21.0
  * Created data folder with parties.json and players.json
  * Configured bot with token: 8109322082:AAFBpC7pIJRiLogy_4pvZ8Gd6zQ4W6O74s4
  * Bot is running and ready to receive Telegram commands
  * Resolved import conflicts with telegram packages

- July 01, 2025. Access control system implementation
  * Added player authorization system - only approved players can access game
  * Unauthorized players see message: "شما دسترسی به بازی ندارید برای خرید اشتراک به آیدی @Nonobodynonono پیام بدید"
  * Created admin commands: /addplayer, /removeplayer, /listplayers for managing authorized users
  * Added authorized_players.json file for storing approved player IDs
  * All game commands now check authorization before allowing access
  * Admin ID must be updated in code (currently set to placeholder 123456789)

- July 01, 2025. Shopping system with glass-style buttons
  * Added interactive /shop command with Persian glass-style buttons
  * Military purchases: Infantry (100), Special (250), Tank (500), Plane (1000 coins)
  * Company investments: Small Factory (500), Large Factory (1500), Oil Company (3000), Bank (5000 coins)
  * Companies generate daily income (50-800 coins per day)
  * Enhanced /profile command with purchase buttons
  * Complete purchase system with coin validation and inventory management
  * Interactive button navigation with Persian labels

- July 01, 2025. Location change system with 11 Iranian provinces
  * Added "📍 تغییر موقعیت" button to main menu and profile
  * Players can change location to any of 11 provinces: Tehran, Hamedan, Fars, Khuzestan, Khorasan, Baluchestan, Mazandaran, Azerbaijan, Kurdistan, Lorestan, Isfahan
  * Each province has unique emoji and Persian name
  * Location changes are saved to player data immediately
  * Enhanced navigation with back buttons and confirmation messages

- July 01, 2025. Party leadership system and party information display
  * Added "🏛️ حزب من" (My Party) button to main menu and profile
  * Dynamic party leadership system: richest player (most coins) becomes party leader
  * Party info shows: party name, region, member count, total soldiers (sum of all members), leader ID and coins
  * Total soldiers calculated from all party members combined
  * Leader information displays name, Telegram ID, and coin amount
  * Added helper functions: get_party_leader() and get_party_total_soldiers()

- July 01, 2025. Leave party functionality
  * Added "❌ ترک حزب" (Leave Party) button in party information screen
  * Players can leave their current party and join a new one
  * Automatic cleanup: removes player from party members list and clears party_id
  * Success confirmation with options to join new party or return to main menu
  * Error handling for players not in any party
  * Added leave_party() helper function for proper data management

- July 14, 2025. Major regional warfare system overhaul
  * Reduced parties from 11 to 6 political parties
  * Each party now controls 6 regions instead of 1 single region
  * Implemented regional asset management system (soldiers and companies per region)
  * Added soldier movement system between regions within same party
  * Created comprehensive combat system with region-based warfare
  * Combat mechanics: when defenders lose all soldiers, all companies are destroyed
  * Victory rewards: company values distributed equally among attacking party members
  * Updated player data structure to include regional_assets instead of global soldiers/investments
  * Added regional management UI with attack, defense, and troop movement capabilities
  * Enhanced purchase system to require region selection for soldiers and companies
  * Implemented multi-step combat interface: select attack region → target party → target region
  * Added real-time regional status display showing soldiers and companies per region
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## Technical Notes

### Current Limitations
- No database integration (relies on JSON files)
- Incomplete main.py file (appears truncated)
- Basic error handling
- Single-threaded operation

### Future Considerations
- Database migration path available (code agent may add Postgres)
- Scalability improvements needed for larger player bases
- Additional game mechanics implementation required
- Enhanced error handling and logging capabilities

### Security Considerations
- Bot token should be properly secured via environment variables
- Input validation needed for user data
- Rate limiting may be required for production use