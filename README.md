# server-cleaner-bot-a

Matrix bot for automated media cleanup with SQLite tracking and filesystem deletion.

## Features

- SQLite database tracking of media uploads (event_id, room_id, sender, mxc_uri, mimetype, size, timestamp)
- Retention-based cleanup: Delete media older than configured days
- Pressure-based cleanup: Delete media when disk usage exceeds threshold
- Prioritizes non-images (videos, files) before images
- Dry-run mode for safe testing
- Matrix notifications posted to log room
- Deletes both Matrix events (redaction) and actual files from `/srv/media`

## Usage

```bash
# Dry-run (safe testing)
python main.py --mode retention --config config.yaml --dry-run
python main.py --mode pressure --config config.yaml --dry-run

# Live execution
python main.py --mode retention --config config.yaml
python main.py --mode pressure --config config.yaml
```

## Modes

### Retention Mode
Deletes media older than configured retention periods:
- Images: 90 days (default)
- Non-images: 30 days (default)

Deletion order: non-images first → oldest first → largest first

### Pressure Mode
Activates when disk usage exceeds threshold (85% default):
- Deletes media until usage drops below threshold
- Prioritizes large non-images to maximize space freed

Deletion order: non-images first → largest first

## Configuration

`config.yaml` structure:

```yaml
homeserver_url: "http://conduit:6167"
server_name: "example.org"

bot:
  mxid: "@cleaner:example.org"
  access_token: "<token>"

policy:
  retention_days:
    image: 90
    non_image: 30
  disk_thresholds:
    pressure: 0.85
    emergency: 0.92
  prefer_large_first: true

notifications:
  log_room_id: "!room:example.org"
  send_deletion_summary: true
  send_nightly_status: true
  send_zero_deletion_summaries: false

rooms_allowlist: []  # Empty = all joined rooms
```

## Database

Uploads tracked in `/state/uploads.db`:
- Syncs last 100 messages per room on each run
- Stores event metadata for efficient querying
- Removes entries after successful deletion

## Docker

Requires mounts:
- `/config` - Configuration file
- `/state` - SQLite database persistence
- `/srv/media` - Media files to clean

## Dependencies

- mautrix >= 0.20.0
- aiohttp >= 3.9.0
- aiosqlite >= 0.20.0
- PyYAML >= 6.0.1
- python-dateutil >= 2.9.0
