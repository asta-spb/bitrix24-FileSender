# Bitrix24 Bot — Project Instructions

## Project Overview

Python application for a Bitrix24 bot using the b24pysdk library.

## Libraries & Documentation

- **SDK:** `D:\SoftProjects\bitrix-bot\libs\b24pysdk` — Python SDK for Bitrix24 REST API
- **API Docs:** `D:\SoftProjects\bitrix-bot\libs\b24-rest-docs` — Full REST API reference

## SDK Usage

### Installation
```python
# Add to Python path or install via pip from local directory
import sys
sys.path.insert(0, r"D:\SoftProjects\bitrix-bot\libs\b24pysdk")
from b24pysdk import BitrixWebhook, Client
```

### Authentication
```python
from b24pysdk import BitrixWebhook, Client

webhook = BitrixWebhook(
    domain="example.bitrix24.com",
    webhook_token="USER_ID/WEBHOOK_TOKEN"
)
client = Client(webhook)
```

### API Call Patterns
```python
# Single call — deferred, executes on .result access
result = client.crm.deal.get(bitrix_id=2).result

# List all (auto-pagination)
deals = client.crm.deal.list().as_list().result

# List large datasets (generator, memory efficient)
for deal in client.crm.deal.list().as_list_fast().result:
    print(deal["TITLE"])

# Batch (up to 50 calls in one HTTP request)
batch = client.call_batch({
    "deal1": client.crm.deal.get(bitrix_id=1),
    "deal2": client.crm.deal.get(bitrix_id=2),
})
results = batch.result.result
```

### Error Handling
```python
from b24pysdk.errors import BitrixAPIError, BitrixAPIExpiredToken, BitrixRequestTimeout

try:
    result = client.crm.deal.get(bitrix_id=2).result
except BitrixAPIExpiredToken:
    pass  # token auto-refreshes for BitrixToken
except BitrixAPIError as e:
    print(f"{e.error}: {e.error_description}")
except BitrixRequestTimeout:
    pass
```

## Bot API (imbot.v2)

Key methods for chatbot functionality:
- `imbot.v2.Bot.register` — Register bot with webhook token
- `imbot.v2.Event.get` — Poll for events (fetch mode)
- `imbot.v2.Chat.Message.send` — Send message to chat
- `imbot.v2.Command.register` — Register bot commands
- `imbot.v2.File.upload` / `imbot.v2.File.download` — File operations

Bot types: `bot` (standard), `supervisor` (sees all), `personal`, `openline`.

## Project Conventions

- Python 3.9+
- Use `b24pysdk` for all Bitrix24 API calls — never raw `requests`
- Config via `.env` file, loaded with `python-dotenv`
- Credentials in env vars: `BITRIX_DOMAIN`, `BITRIX_WEBHOOK_TOKEN`
- No comments unless the WHY is non-obvious
- Prefer `as_list_fast()` for large datasets
- Use batch calls when making multiple related API requests

## Project Structure
```
bitrix-bot/
├── CLAUDE.md
├── .env                  # secrets (not committed)
├── .env.example          # template
├── requirements.txt
├── main.py               # CLI entry point
├── config.py             # config from env + CLI overrides
├── sender.py             # file upload and send logic
└── logger.py             # logging setup (console + file)
```

## Logging

- Log file: `bitrix_sender.log` (always DEBUG level)
- Console: INFO by default, DEBUG with `-v / --verbose`
- Use `logger.get()` to get the logger anywhere in the code
- Always call `logger.setup()` once in `main()` before other imports use it

## CLI Usage

```bash
# One file
python main.py report.pdf -m "Отчёт за апрель"

# Multiple files
python main.py file1.pdf file2.xlsx file3.png -m "Документы"

# Message from file
python main.py report.pdf --message-file cover.txt

# Override domain, chat and webhook from CLI
python main.py report.pdf -m "Срочно" --domain portal.bitrix24.com --chat-id 1234 --webhook "1/abc123"

# Verbose/debug output
python main.py report.pdf -v
```

## File Size Limit

Bitrix24 hard limit: 100 MB per file.
Files exceeding this produce a WARNING in log before attempting upload.
