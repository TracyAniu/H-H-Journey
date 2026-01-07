# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WeChat public account (微信公众号) scheduled message push service. Sends daily templated messages to subscribed users containing weather, anniversary countdowns, birthdays, and daily quotes.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the message push
python main.py
```

The service is also configured to run via GitHub Actions (`.github/workflows/weixin.yml`) daily at 8:00 AM Beijing time (cron: `0 0 * * *` UTC).

## Architecture

Single-file Python application (`main.py`) with the following flow:

1. **Configuration**: Reads `config.txt` (Python dict literal format) containing API credentials, user IDs, birthdays, and regional settings
2. **WeChat API**: Authenticates via `app_id`/`app_secret` to obtain access token, then sends template messages
3. **Weather API**: Uses QWeather (和风天气) API to fetch current weather by location
4. **Daily Quote**: Fetches from iCIBA API (金山词霸), or uses custom quotes from config
5. **Birthday Calculation**: Supports both Gregorian and lunar calendar (农历) birthdays using `zhdate` library - lunar dates prefixed with "r" (e.g., "r2000-01-15")

## Configuration (config.txt)

Key fields:
- `app_id`, `app_secret`: WeChat public account credentials
- `template_id`: WeChat message template ID
- `user`: List of recipient WeChat OpenIDs
- `weather_key`: QWeather API key
- `region`: Location name for weather lookup
- `birthday1`, `birthday2`, etc.: Birthday entries with `name` and `birthday` fields
- `love_date`: Anniversary date for countdown
