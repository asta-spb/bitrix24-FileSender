# Bitrix24 File Sender

CLI-утилита для отправки файлов в чат Bitrix24 через webhook.

## Возможности

- Отправка одного или нескольких файлов в чат
- Отправка всех файлов из директории с фильтрацией по маске и рекурсивным обходом
- Сопроводительное сообщение — строкой или из файла
- Просмотр списка доступных чатов
- Переопределение параметров подключения прямо из командной строки
- Предупреждение при превышении лимита 100 МБ

## Требования

- Python 3.9+
- [b24pysdk](https://github.com/Isys1n/b24pysdk) (локальная зависимость)
- `python-dotenv`

## Установка

```bash
git clone <repo-url>
cd bitrix-bot

pip install python-dotenv
# b24pysdk устанавливается из локального пути, указанного в requirements.txt
pip install -r requirements.txt
```

## Настройка

Скопируйте `.env.example` в `.env` и заполните переменные:

```bash
cp .env.example .env
```

```env
BITRIX_DOMAIN=example.bitrix24.com
BITRIX_WEBHOOK_TOKEN=1/your_webhook_token_here
BITRIX_CHAT_ID=2941
```

| Переменная              | Описание                                      |
|-------------------------|-----------------------------------------------|
| `BITRIX_DOMAIN`         | Домен портала Bitrix24                        |
| `BITRIX_WEBHOOK_TOKEN`  | Webhook-токен в формате `user_id/token`       |
| `BITRIX_CHAT_ID`        | ID чата назначения                            |

> Webhook создаётся в Bitrix24: **Профиль → Разработчикам → Входящий webhook**.

## Использование

### Отправка файлов

```bash
# Один файл
python main.py report.pdf

# Несколько файлов с сопроводительным сообщением
python main.py file1.pdf file2.xlsx file3.png -m "Документы за апрель"

# Сообщение из файла
python main.py report.pdf --message-file cover.txt
```

### Отправка из директории

```bash
# Все файлы из папки
python main.py --dir ./reports

# Только PDF-файлы
python main.py --dir ./reports --pattern "*.pdf"

# Рекурсивно, все xlsx
python main.py --dir ./reports --pattern "*.xlsx" --recursive
```

### Управление подключением

```bash
# Переопределить параметры из .env
python main.py report.pdf --domain portal.bitrix24.com --chat-id 1234 --webhook "1/abc123"

# Показать список доступных чатов
python main.py --list-chats
```

### Прочее

```bash
# Подробный вывод (DEBUG-уровень)
python main.py report.pdf -v
```

### Справка

```bash
python main.py --help
```

## Параметры командной строки

| Параметр           | Описание                                                         |
|--------------------|------------------------------------------------------------------|
| `FILE [FILE ...]`  | Один или несколько файлов для отправки                           |
| `--dir DIR`        | Директория с файлами                                             |
| `--pattern GLOB`   | Маска файлов в директории (по умолчанию `*`)                     |
| `--recursive`      | Рекурсивный обход поддиректорий                                  |
| `-m, --message`    | Сопроводительное сообщение (строка)                              |
| `--message-file`   | Путь к файлу с сопроводительным сообщением                       |
| `--domain`         | Домен портала (переопределяет `BITRIX_DOMAIN`)                   |
| `--chat-id`        | ID чата (переопределяет `BITRIX_CHAT_ID`)                        |
| `--webhook`        | Webhook-токен (переопределяет `BITRIX_WEBHOOK_TOKEN`)            |
| `--list-chats`     | Показать список чатов и выйти                                    |
| `-v, --verbose`    | Подробный вывод                                                  |

## Структура проекта

```
bitrix-bot/
├── .env                  # секреты (не коммитится)
├── .env.example          # шаблон переменных окружения
├── requirements.txt
├── main.py               # точка входа, CLI
├── config.py             # загрузка конфигурации
├── sender.py             # загрузка и отправка файлов
└── logger.py             # настройка логирования
```

## Логирование

Логи пишутся одновременно в консоль и в файл `bitrix_sender.log`:

- Консоль: уровень INFO (DEBUG при `-v`)
- Файл: всегда DEBUG

## Ограничения

- Максимальный размер файла: **100 МБ** (лимит Bitrix24)
- Сопроводительное сообщение прикрепляется только к первому файлу в пакете

## Лицензия

MIT
