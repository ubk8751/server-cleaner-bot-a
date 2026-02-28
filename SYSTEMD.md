# Systemd Service Files for Catcord Cleaner

## Nightly Summary Service

Create `/etc/systemd/system/catcord-cleaner-nightly.service`:

```ini
[Unit]
Description=Catcord Cleaner Nightly Summary
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/cathyAI-bots
ExecStart=/bin/bash -c '\
  /usr/bin/docker-compose run --rm cleaner --config /config/config.yaml --mode retention --print-effective-config && \
  sleep 2 && \
  /usr/bin/docker-compose run --rm cleaner --config /config/config.yaml --mode pressure --print-effective-config'
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## Nightly Summary Timer

Create `/etc/systemd/system/catcord-cleaner-nightly.timer`:

```ini
[Unit]
Description=Run Catcord Cleaner Nightly Summary at 01:00
Requires=catcord-cleaner-nightly.service

[Timer]
OnCalendar=*-*-* 01:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

## Pressure Check Service (2-minute interval)

Create `/etc/systemd/system/catcord-cleaner-pressure.service`:

```ini
[Unit]
Description=Catcord Cleaner Pressure Check
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/cathyAI-bots
ExecStart=/usr/bin/docker-compose run --rm cleaner --config /config/config.yaml --mode pressure
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## Pressure Check Timer (2-minute interval)

Create `/etc/systemd/system/catcord-cleaner-pressure.timer`:

```ini
[Unit]
Description=Run Catcord Cleaner Pressure Check every 2 minutes
Requires=catcord-cleaner-pressure.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=2min
Persistent=true

[Install]
WantedBy=timers.target
```

## Installation

```bash
# Copy service files to systemd directory
sudo cp catcord-cleaner-*.service /etc/systemd/system/
sudo cp catcord-cleaner-*.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timers
sudo systemctl enable catcord-cleaner-nightly.timer
sudo systemctl start catcord-cleaner-nightly.timer

sudo systemctl enable catcord-cleaner-pressure.timer
sudo systemctl start catcord-cleaner-pressure.timer

# Check timer status
sudo systemctl list-timers catcord-cleaner-*
```

## Notes

- The nightly service runs BOTH retention and pressure modes at 01:00 with `--print-effective-config` flag
- This forces notifications even on no-action runs (overrides send_zero setting)
- The 2-minute pressure timer does NOT use `--print-effective-config`, so it respects send_zero setting
- Adjust WorkingDirectory path to match your installation location
