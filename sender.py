import base64
from pathlib import Path

from b24pysdk import BitrixWebhook, Client
from b24pysdk.api.callers import call_method

import logger
from config import Config

MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def _build_client(cfg: Config) -> Client:
    webhook = BitrixWebhook(
        domain=cfg.domain,
        webhook_token=cfg.webhook_token,
    )
    return Client(webhook)


def _encode_file(path: Path) -> tuple[str, str]:
    content = base64.b64encode(path.read_bytes()).decode()
    return path.name, content


def _check_file_size(path: Path) -> None:
    size = path.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        mb = size / 1024 / 1024
        logger.get().warning(
            "Файл %s имеет размер %.1f МБ, что превышает лимит Bitrix24 (%d МБ). "
            "Отправка может завершиться ошибкой.",
            path.name, mb, MAX_FILE_SIZE_MB,
        )


def list_chats(cfg: Config) -> list[dict]:
    """Return all group chats the current user is a member of."""
    client = _build_client(cfg)
    result = client.im.recent.list(skip_dialog=True).result
    chats = []
    for item in result.get("items", []):
        chat_id_raw = item.get("id", "")
        chat_id = str(chat_id_raw).removeprefix("chat")
        chats.append({
            "id": chat_id,
            "title": item.get("title", ""),
            "type": item.get("type", ""),
        })
    return chats


UPLOAD_TIMEOUT = 120


def _get_chat_folder(cfg: Config) -> int:
    response = call_method(
        domain=cfg.domain,
        auth_token=cfg.webhook_token,
        is_webhook=True,
        api_method="im.disk.folder.get",
        params={"DIALOG_ID": f"chat{cfg.chat_id}"},
        timeout=UPLOAD_TIMEOUT,
    )
    return response["result"]["ID"]


def send_files(cfg: Config, file_paths: list[Path], message: str) -> list[int]:
    """Send multiple files. Message is attached to the first file only."""
    log = logger.get()

    folder_id = _get_chat_folder(cfg)
    log.debug("Папка чата на диске: ID=%s", folder_id)

    message_ids = []
    for i, file_path in enumerate(file_paths):
        log.info("Отправка файла %d/%d: %s", i + 1, len(file_paths), file_path.name)

        size_mb = file_path.stat().st_size / 1024 / 1024
        log.info("  Загружаем файл (%.1f МБ)...", size_mb)

        filename, content_b64 = _encode_file(file_path)

        upload_response = call_method(
            domain=cfg.domain,
            auth_token=cfg.webhook_token,
            is_webhook=True,
            api_method="disk.folder.uploadfile",
            params={
                "id": folder_id,
                "data": {"NAME": filename},
                "fileContent": [filename, content_b64],
                "generateUniqueName": True,
            },
            timeout=UPLOAD_TIMEOUT,
        )
        file_id = upload_response["result"]["ID"]
        log.debug("Файл загружен на диск: ID=%s", file_id)

        commit_params: dict = {"CHAT_ID": cfg.chat_id, "UPLOAD_ID": [file_id]}
        if i == 0 and message:
            commit_params["MESSAGE"] = message

        commit_response = call_method(
            domain=cfg.domain,
            auth_token=cfg.webhook_token,
            is_webhook=True,
            api_method="im.disk.file.commit",
            params=commit_params,
            timeout=UPLOAD_TIMEOUT,
        )
        message_id = commit_response["result"]["MESSAGE_ID"]
        log.debug("Сообщение создано: ID=%s", message_id)
        message_ids.append(message_id)

    return message_ids
