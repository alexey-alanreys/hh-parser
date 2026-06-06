# HireScope

Анализатор вакансий с hh.ru. Парсит страницы поиска, извлекает навыки и ключевые слова, показывает что чаще всего встречается в описаниях вакансий.

---

## Установка

### Шаг 1 — Установить Python

1. Открыть https://www.python.org/downloads/
2. Нажать **"Download Python 3.x.x"** (последняя версия)
3. Запустить установщик
4. ⚠️ На первом экране обязательно поставить галочку **"Add python.exe to PATH"**
5. Нажать **"Install Now"**

Проверить установку — открыть терминал (`Win+R` → ввести `cmd` → Enter):
```cmd
python --version
```
Должно вывести что-то вроде `Python 3.12.3`.

---

### Шаг 2 — Скачать HireScope

Положить все файлы проекта в одну папку, сохранив структуру:
```
HireScope\
├── main.py
├── config.py
├── models.py
├── requirements.txt
├── core\
│   ├── __init__.py
│   ├── fetcher.py
│   ├── parser.py
│   ├── analyzer.py
│   └── reporter.py
├── data\
│   ├── stopwords.txt
│   └── skill_aliases.json
└── tests\
    ├── test_parser.py
    ├── test_analyzer.py
    └── test_reporter.py
```

---

### Шаг 3 — Открыть терминал в папке проекта

Открыть папку `HireScope` в Проводнике, кликнуть правой кнопкой по пустому месту → **"Открыть в терминале"**.

Или вручную: `Win+R` → `cmd` → Enter, затем:
```cmd
cd C:\HireScope
```

---

### Шаг 4 — Создать виртуальное окружение

```cmd
python -m venv venv
```

---

### Шаг 5 — Активировать окружение

```cmd
venv\Scripts\activate
```

В начале строки появится `(venv)` — окружение активно.

---

### Шаг 6 — Установить зависимости

```cmd
pip install -r requirements.txt
```

---

## Запуск

> ⚠️ Перед каждым запуском убедитесь что виртуальное окружение активировано — в начале строки есть `(venv)`. Если нет — выполните `venv\Scripts\activate`.

### Минимальный запуск

```cmd
python main.py --query "Frontend React"
```

### Полный пример

```cmd
python main.py ^
  --query "Frontend React" ^
  --max-vacancies 100 ^
  --skill-threshold 5 ^
  --keyword-threshold 8 ^
  --top-n 25 ^
  --cache-dir .cache ^
  --output-format both ^
  --output-file results.json
```

---

## Параметры

### Поиск

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--query` | — | Поисковый запрос, например `"Frontend React"` |
| `--area` | `0` | Регион: `0` = вся Россия, `1` = Москва, `2` = Санкт-Петербург |
| `--max-vacancies` | `100` | Сколько вакансий обработать |
| `--experience` | — | Опыт: `noExperience`, `between1And3`, `between3And6`, `moreThan6` |

### Анализ

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--skill-threshold` | `5` | Мин. повторений навыка чтобы считаться горячим |
| `--keyword-threshold` | `5` | Мин. повторений слова чтобы считаться горячим |
| `--top-n` | `30` | Сколько результатов показать в выводе |
| `--min-word-length` | `3` | Мин. длина слова для анализа ключевых слов |
| `--stopwords-file` | — | Дополнительный файл стоп-слов (по одному слову на строку) |
| `--bigrams` | выкл. | Включить поиск словосочетаний из двух слов (биграммы) |

### Вывод

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--output-format` | `console` | Формат: `console`, `json`, `csv`, `both` |
| `--output-file` | `hirescope_results.json` | Имя файла для сохранения |

### Технические

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--delay` | `1.0` | Пауза между запросами в секундах |
| `--cache-dir` | — | Папка для кеширования HTML на диск |
| `--verbose` | выкл. | Подробный лог |

---

## Примеры запросов

**Быстрая проверка** (2-3 мин):
```cmd
python main.py --query "Frontend React" --max-vacancies 20 --skill-threshold 2 --keyword-threshold 3 --cache-dir .cache
```

**Полноценный анализ** (10-15 мин):
```cmd
python main.py --query "Frontend React" --max-vacancies 100 --skill-threshold 5 --keyword-threshold 8 --cache-dir .cache --output-format both --output-file results.json
```

**С биграммами — ловим словосочетания** (`state management`, `code review` и т.д.):
```cmd
python main.py --query "Frontend React" --max-vacancies 100 --bigrams --keyword-threshold 5 --cache-dir .cache
```

**Только Москва, опыт 1-3 года**:
```cmd
python main.py --query "Frontend React" --area 1 --experience between1And3 --max-vacancies 100 --cache-dir .cache
```

**Другая специальность**:
```cmd
python main.py --query "Python разработчик" --max-vacancies 100 --skill-threshold 5 --keyword-threshold 8 --cache-dir .cache
```

---

## Кеширование

Флаг `--cache-dir .cache` сохраняет HTML страниц на диск. При повторном запуске данные берутся из кеша — запросов к hh.ru не делается.

Удобно когда нужно пересчитать с другими порогами без повторного скачивания:

```cmd
rem Первый запуск — скачивает и кеширует
python main.py --query "Frontend React" --max-vacancies 100 --cache-dir .cache --skill-threshold 5

rem Второй запуск — из кеша, меняем только порог
python main.py --query "Frontend React" --max-vacancies 100 --cache-dir .cache --skill-threshold 3
```

---

## Настройка стоп-слов и навыков

**`data/stopwords.txt`** — слова которые игнорируются при анализе ключевых слов. Строки начинающиеся с `#` — комментарии. Можно добавлять свои слова.

**`data/skill_aliases.json`** — нормализация навыков. Примеры:
- `"react.js"` → `"React"` — объединяет варианты написания
- `"frontend"` → `"_ignore"` — полностью исключает из навыков

Оба файла редактируются в любом текстовом редакторе без изменения кода.

---

## Запуск тестов

```cmd
python -m pytest tests\ -v
```

---

## Завершение работы

```cmd
deactivate
```