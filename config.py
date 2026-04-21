import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    domain: str
    webhook_token: str
    chat_id: int


def load_config(
    domain: str | None = None,
    webhook_token: str | None = None,
    chat_id: int | None = None,
    require_chat_id: bool = True,
) -> Config:
    resolved_domain = domain or os.getenv("BITRIX_DOMAIN", "")
    resolved_token = webhook_token or os.getenv("BITRIX_WEBHOOK_TOKEN", "")
    env_chat_id = os.getenv("BITRIX_CHAT_ID", "")
    resolved_chat_id = chat_id or (int(env_chat_id) if env_chat_id else None)

    errors = []
    if not resolved_domain:
        errors.append("BITRIX_DOMAIN не задан (env или --domain)")
    if not resolved_token:
        errors.append("BITRIX_WEBHOOK_TOKEN не задан (env или --webhook)")
    if require_chat_id and not resolved_chat_id:
        errors.append("BITRIX_CHAT_ID не задан (env или --chat-id)")

    if errors:
        raise ValueError("\n".join(errors))

    return Config(
        domain=resolved_domain,
        webhook_token=resolved_token,
        chat_id=resolved_chat_id or 0,
    )
