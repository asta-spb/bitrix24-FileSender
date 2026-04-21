#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

import logger
from config import load_config
from sender import _check_file_size, list_chats, send_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Отправка файлов в чат Bitrix24",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "files",
        type=Path,
        nargs="*",
        metavar="FILE",
        help="Путь к файлу (или несколько файлов через пробел)",
    )

    parser.add_argument(
        "--dir",
        type=Path,
        metavar="DIR",
        help="Директория с файлами для отправки",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*",
        metavar="GLOB",
        help="Маска файлов в директории (по умолчанию: *)\nПримеры: *.pdf, report_*.xlsx, *.{pdf,docx}",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Обходить поддиректории рекурсивно (работает с --dir)",
    )

    msg_group = parser.add_mutually_exclusive_group()
    msg_group.add_argument(
        "-m", "--message",
        type=str,
        default="",
        help="Сопроводительное сообщение (строка)",
    )
    msg_group.add_argument(
        "--message-file",
        type=Path,
        metavar="PATH",
        help="Путь к текстовому файлу с сопроводительным сообщением",
    )

    parser.add_argument(
        "--domain",
        type=str,
        metavar="DOMAIN",
        help="Домен портала, например example.bitrix24.com\n(переопределяет BITRIX_DOMAIN из .env)",
    )
    parser.add_argument(
        "--chat-id",
        type=int,
        metavar="ID",
        help="ID чата (переопределяет BITRIX_CHAT_ID из .env)",
    )
    parser.add_argument(
        "--webhook",
        type=str,
        metavar="TOKEN",
        help="Webhook-токен формата user_id/key\n(переопределяет BITRIX_WEBHOOK_TOKEN из .env)",
    )
    parser.add_argument(
        "--list-chats",
        action="store_true",
        help="Показать список доступных чатов и выйти",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Подробный вывод (debug-уровень в консоль)",
    )

    return parser.parse_args()


def collect_from_dir(directory: Path, pattern: str, recursive: bool) -> list[Path]:
    log = logger.get()

    if not directory.exists():
        log.error("Директория не найдена: %s", directory)
        sys.exit(1)
    if not directory.is_dir():
        log.error("Путь не является директорией: %s", directory)
        sys.exit(1)

    glob_fn = directory.rglob if recursive else directory.glob
    files = sorted(p for p in glob_fn(pattern) if p.is_file())

    log.debug(
        "Директория %s, маска '%s', рекурсия=%s → найдено %d файлов",
        directory, pattern, recursive, len(files),
    )
    return files


def validate_files(paths: list[Path]) -> list[Path]:
    log = logger.get()
    valid = []
    has_error = False

    for path in paths:
        if not path.exists():
            log.error("Файл не найден: %s", path)
            has_error = True
            continue
        if not path.is_file():
            log.error("Путь не является файлом: %s", path)
            has_error = True
            continue
        _check_file_size(path)
        valid.append(path)

    if has_error:
        sys.exit(1)

    return valid


def main() -> None:
    args = parse_args()

    log = logger.setup(verbose=args.verbose)
    log.debug("Запуск. Аргументы: %s", vars(args))

    if args.list_chats:
        try:
            cfg = load_config(domain=args.domain, webhook_token=args.webhook, require_chat_id=False)
        except ValueError as e:
            log.error("Ошибка конфигурации:\n%s", e)
            sys.exit(1)
        chats = list_chats(cfg)
        if not chats:
            log.info("Чаты не найдены")
        else:
            log.info("Доступные чаты (%d):", len(chats))
            for chat in chats:
                log.info("  ID=%-8s  %s", chat["id"], chat["title"])
        sys.exit(0)

    # Collect files: explicit + from --dir
    all_files: list[Path] = list(args.files or [])

    if args.dir:
        dir_files = collect_from_dir(args.dir, args.pattern, args.recursive)
        all_files.extend(dir_files)

    if not all_files:
        log.error("Не указаны файлы для отправки. Укажите FILE или --dir.")
        sys.exit(1)

    # Deduplicate preserving order
    seen: set[Path] = set()
    unique_files = []
    for f in all_files:
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_files.append(f)

    files = validate_files(unique_files)

    if not files:
        log.error("Нет файлов для отправки после валидации.")
        sys.exit(1)

    log.info("Файлов к отправке: %d", len(files))
    for f in files:
        log.debug("  → %s", f)

    # Resolve message
    if args.message_file:
        if not args.message_file.exists():
            log.error("Файл сообщения не найден: %s", args.message_file)
            sys.exit(1)
        message = args.message_file.read_text(encoding="utf-8").strip()
        log.debug("Сообщение загружено из файла: %s", args.message_file)
    else:
        message = args.message

    # Load config
    try:
        cfg = load_config(
            domain=args.domain,
            webhook_token=args.webhook,
            chat_id=args.chat_id,
        )
    except ValueError as e:
        log.error("Ошибка конфигурации:\n%s", e)
        sys.exit(1)

    log.debug("Конфиг: domain=%s, chat_id=%d", cfg.domain, cfg.chat_id)

    # Send
    try:
        message_ids = send_files(cfg, files, message)
        for file_path, msg_id in zip(files, message_ids):
            log.info("Отправлен: %s → ID сообщения: %d", file_path.name, msg_id)
    except Exception as e:
        log.error("Ошибка при отправке: %s", e)
        log.debug("", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
