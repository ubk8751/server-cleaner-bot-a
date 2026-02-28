# Catcord Bots

Matrix bot framework with automated media cleanup service.

## Architecture

```
bots/
├── framework/          # Shared Python package
│   └── catcord_bots/  # Matrix client, config, personality, state
├── cleaner/           # Media cleanup bot
│   ├── main.py        # Entry point
│   ├── cleaner.py     # Cleanup logic
│   └── config.yaml    # Configuration
└── tests/             # Test suite
```

## Features

- **Matrix Integration**: Async Matrix client with auto-join and messaging
- **Media Cleanup**: Retention and pressure-based cleanup modes
- **AI Personality**: Optional AI-generated status prefixes via prompt-composer
- **Deduplication**: Prevents duplicate notifications using payload fingerprints
- **State Management**: Tracks last notification to avoid spam

## Setup

### Docker (Production)

```bash
./setup.sh  # Choose option 1
docker build -t catcord-bots-framework:latest -f framework/Dockerfile framework
docker-compose build cleaner
```

### Local (Development)

```bash
./setup.sh  # Choose option 2
source venv/bin/activate
```

## Configuration

Copy `config.yaml.template` to `config.yaml` and configure:

```yaml
matrix:
  homeserver_url: "https://matrix.example.com"
  user_id: "@bot:example.com"
  access_token: "your_token"
  notifications_room: "!room:example.com"

cleaner:
  media_root: "/path/to/media"
  db_path: "/path/to/uploads.db"
  policy:
    image_days: 90
    non_image_days: 30
    pressure: 0.85
    emergency: 0.92

add_personality:
  enabled: true
  prompt_composer_url: "http://localhost:8110"
  character_id: "irina"
  cathy_api_url: "http://localhost:8100"
  cathy_api_mode: "ollama"
  cathy_api_model: "gemma2:2b"
```

## Usage

### Cleaner Bot

**Retention Mode**: Delete media older than configured days

```bash
docker-compose run --rm cleaner --config /config/config.yaml --mode retention --dry-run
docker-compose run --rm cleaner --config /config/config.yaml --mode retention
```

**Pressure Mode**: Delete media when disk usage exceeds threshold

```bash
docker-compose run --rm cleaner --config /config/config.yaml --mode pressure --dry-run
docker-compose run --rm cleaner --config /config/config.yaml --mode pressure
```

**Flags**:
- `--mode {retention,pressure}`: Cleanup mode (required)
- `--dry-run`: Simulate without deleting
- `--print-effective-config`: Force send notification (for scheduled runs)

### Scheduling

Use systemd timers or cron:

```bash
# Nightly full check at 01:00
0 1 * * * docker-compose run --rm cleaner --config /config/config.yaml --mode retention --print-effective-config
0 1 * * * docker-compose run --rm cleaner --config /config/config.yaml --mode pressure --print-effective-config

# Frequent pressure monitoring every 2 minutes
*/2 * * * * docker-compose run --rm cleaner --config /config/config.yaml --mode pressure
```

## AI Personality

The bot can generate contextual status prefixes using:
1. **prompt-composer**: Builds character-specific prompts
2. **LLM API**: Generates natural language prefixes (Ollama or OpenAI-compatible)

### Validation Rules

AI prefixes are validated to ensure:
- 3-140 characters, single sentence
- No digits, quotes, newlines
- No meta-descriptions (bot, Matrix, room, etc.)
- No temporal references (today, yesterday, uptime)
- No deletion claims (deleted, removed, purged)

### Fallback Prefixes

If AI fails or is disabled, deterministic fallbacks are used:
- No deletions + healthy storage: "Logs clear, Master."
- No deletions + tight storage: "Storage getting tight, Master."
- Deletions occurred: "Cleanup executed, Master."

## Deduplication

Notifications are deduplicated using payload fingerprints stored in `/state/{mode}_last.fp`. Messages are only sent when:
- Payload changes (different deletions, disk usage, etc.)
- `--print-effective-config` flag is used (always send)

This prevents spam from frequent checks while ensuring important changes are reported.

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Code Standards

- PEP 8 compliance (88 char line length)
- reST docstrings with type annotations
- Type hints for all function signatures

### Commit Format

```
[type]: Title

Description:
  - Change 1
  - Change 2

Additional info:
  - Info 1
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Framework Modules

### catcord_bots.matrix
Matrix client wrapper with async operations, auto-join, and messaging.

### catcord_bots.config
YAML configuration parsing and validation.

### catcord_bots.personality
AI prefix generation with prompt-composer integration, validation, and fallbacks.

### catcord_bots.state
Payload fingerprinting and deduplication logic.

### catcord_bots.formatting
Message formatting for retention and pressure reports.

## License

See repository license file.
