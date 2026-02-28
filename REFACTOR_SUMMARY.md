# Refactor Implementation Summary

## Changes Completed

### A) Removed --debug flag
- ✅ Deleted from `cleaner/main.py` argparse
- ✅ Removed from function signatures in `cleaner/cleaner.py` (run_retention, run_pressure)
- ✅ Removed from `framework/catcord_bots/state.py` should_send()
- ✅ Updated README.md to remove debug flag documentation

### B) Renamed --force-notify → --print-effective-config
- ✅ Renamed argparse flag in `cleaner/main.py`
- ✅ Updated function parameters throughout codebase
- ✅ Updated should_send() signature in `framework/catcord_bots/state.py`
- ✅ Updated README.md with new flag name and semantics

### C) New semantics for --print-effective-config
- ✅ Forces should_send() to return True (bypasses dedupe)
- ✅ Forces notification even on no-action runs (overrides send_zero)
- ✅ Implemented in both run_retention() and run_pressure()
- ✅ Logic: `should_notify = (deleted > 0) or send_zero or dry_run or print_effective_config`

### D) Nightly scheduling at 01:00:00
- ✅ Created SYSTEMD.md with service/timer templates
- ✅ Nightly service runs BOTH retention and pressure sequentially with --print-effective-config
- ✅ Separate 2-minute pressure timer without the flag (existing behavior)
- ✅ Updated README.md with scheduling section

### E) Enhanced retention diagnostics
- ✅ Added candidates_count (records matching retention criteria)
- ✅ Added disk usage percent, thresholds, mount path
- ✅ Added total_files_count (count_media_files helper)
- ✅ Existing metrics preserved: deleted_count, freed_gb, deleted_by_type, timing

### F) Retention message output format
- ✅ Created `framework/catcord_bots/formatting.py` with format_retention_stats()
- ✅ Two-part format: AI prefix + deterministic stats
- ✅ Stats include: Disk %, Storage status, Candidates, Deleted, Freed, Files, Duration, Result
- ✅ Storage status mapping: healthy/OK/tight/pressure/critical

### G) AI prompting improvements
- ✅ Updated PersonalityRenderer to generate ONLY prefix (no metrics)
- ✅ Mode-aware context with storage category (healthy/ok/tight/pressure/critical)
- ✅ Prompts distinguish between no-action and action runs
- ✅ All numeric details excluded from AI output
- ✅ Prefix validation ensures no digits, timestamps, or deletion claims

### H) Pressure message format
- ✅ Created format_pressure_stats() in formatting.py
- ✅ Same two-part format: AI prefix + stats
- ✅ Stats include: Disk before→after, Storage status, Deleted, Freed, Duration, Result
- ✅ Applied to both action and no-action runs

### I) Deduplication behavior
- ✅ Fingerprint-based dedupe preserved
- ✅ print_effective_config bypasses dedupe (should_send returns True)
- ✅ print_effective_config bypasses send_zero gating
- ✅ Clear logging: "Deduped: fingerprint unchanged" and "Not sending: send_zero disabled"

## New Files Created

1. `framework/catcord_bots/formatting.py` - Formatting utilities
   - storage_status_label()
   - format_retention_stats()
   - format_pressure_stats()

2. `SYSTEMD.md` - Systemd service/timer documentation
   - catcord-cleaner-nightly.service (01:00 with flag)
   - catcord-cleaner-nightly.timer
   - catcord-cleaner-pressure.service (2-min without flag)
   - catcord-cleaner-pressure.timer

## Modified Files

1. `framework/catcord_bots/state.py`
   - Removed debug parameter
   - Renamed force_notify → print_effective_config

2. `framework/catcord_bots/personality.py`
   - Returns only prefix (no metrics)
   - Uses storage_status_label for context
   - Updated prompts for mode-aware generation

3. `framework/catcord_bots/__init__.py`
   - Exports formatting utilities

4. `cleaner/main.py`
   - Removed --debug flag
   - Renamed --force-notify → --print-effective-config
   - Updated function calls

5. `cleaner/cleaner.py`
   - Added count_media_files() helper
   - Enhanced retention payload with diagnostics
   - Updated run_retention() signature and logic
   - Updated run_pressure() signature and logic
   - Implemented new notification gating logic
   - Uses formatting utilities for message construction

6. `README.md`
   - Removed debug flag documentation
   - Updated CLI flags section
   - Added nightly summary examples
   - Added scheduling section linking to SYSTEMD.md

## Testing Recommendations

```bash
# Test retention with new flag
docker-compose run --rm cleaner --config /config/config.yaml --mode retention --print-effective-config --dry-run

# Test pressure with new flag
docker-compose run --rm cleaner --config /config/config.yaml --mode pressure --print-effective-config --dry-run

# Test normal runs (should respect send_zero)
docker-compose run --rm cleaner --config /config/config.yaml --mode retention --dry-run
docker-compose run --rm cleaner --config /config/config.yaml --mode pressure --dry-run

# Verify message format includes AI prefix + stats
# Verify deduplication works (run twice, second should dedupe unless flag used)
```

## Deployment Steps

1. Deploy code changes
2. Install systemd services on server (see SYSTEMD.md)
3. Enable and start timers
4. Monitor logs for first nightly run at 01:00
5. Verify 2-minute pressure checks continue working

## Message Format Examples

### Retention (with AI)
```
Master, I reviewed the logs and found no issues requiring action.
Disk: 5.1% (threshold 85.0%)
Storage: healthy
Retention candidates: 123
Deleted: 0 (images=0, non-images=0)
Freed: 0.00 GB
Files on disk: 45678
Duration: 3s
Result: no action
```

### Pressure (with AI, no action)
```
Logs reviewed; storage levels remain stable.
Disk: 45.2% → 45.2% (threshold 85.0%)
Storage: healthy
Deleted: 0 (images=0, non-images=0)
Freed: 0.00 GB
Duration: 1s
Result: no action
```

### Pressure (with AI, action taken)
```
Master, I reviewed the logs and cleanup was performed.
Disk: 87.3% → 82.1% (threshold 85.0%)
Storage: pressure
Deleted: 45 (images=12, non-images=33)
Freed: 2.34 GB
Duration: 12s
Result: cleanup performed
```
