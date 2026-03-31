# Техническая документация — КартриджУчёт

Документ для разработчиков: архитектура, база данных, API, логика работы.

---

## Стек технологий

| Компонент   | Технология                          |
|-------------|-------------------------------------|
| Backend     | Python 3.9+, Flask 3.x              |
| БД          | SQLite (файл `data.db`)             |
| Шаблоны     | Jinja2 (встроен в Flask)            |
| Frontend    | Vanilla JS, CSS (без фреймворков)   |
| WSGI-сервер | `waitress` (Windows) / `gunicorn` (Linux) |
| Разработка  | Flask dev-сервер (`app.run`)        |

---

## Архитектура

Приложение — монолит на Flask. Весь backend в одном файле `app.py` (~1300 строк).

```
Браузер
  │  GET/POST HTML-страниц
  ▼
Flask (app.py)
  ├── Маршруты страниц  → рендерит templates/*.html
  └── API-маршруты (/api/...)  → возвращает JSON
        │
        ▼
      SQLite (data.db)
```

Фронтенд работает через AJAX: страницы загружаются один раз, данные подгружаются через `/api/...` и рендерятся JavaScript'ом на клиенте.

---

## Структура `app.py`

| Строки      | Содержимое                                      |
|-------------|--------------------------------------------------|
| 1–15        | Импорты, инициализация Flask, константы          |
| 17–103      | `check_win11_compat()` — анализ совместимости с Win11 |
| 106–110     | `get_db()` — подключение к SQLite                |
| 111–289     | `init_db()`, `seed_printers()`, `seed_toners()` |
| 292–311     | `hash_pw()`, декораторы `login_required`, `admin_required` |
| 313–386     | Маршруты страниц (`/`, `/login`, `/dashboard`, ...) |
| 388–498     | `/api/stats` — главная статистика дэшборда       |
| 499–594     | API принтеров и записей расхода                  |
| 595–683     | API тонеров и записей тонеров                    |
| 684–757     | API пользователей и бэкапов                      |
| 759–851     | API склада (`/api/stock/...`)                    |
| 853–1022    | API оборудования (`/api/equipment/...`)          |
| 1023–1312   | Экспорт (`/export/excel/...`, `/export/print/...`) |
| 1308–1314   | Запуск сервера (`init_db()`, `app.run`)          |

---

## База данных

SQLite, файл `data.db` в корне проекта. Создаётся автоматически при первом запуске.

### Таблица `users`
```sql
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL,        -- SHA-256 хэш
    role        TEXT NOT NULL DEFAULT 'viewer',  -- admin | operator | viewer
    created_at  TEXT DEFAULT (datetime('now'))
);
```

### Таблица `printers`
```sql
CREATE TABLE printers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    floor        TEXT NOT NULL,       -- "1 этаж", "2 этаж" и т.д.
    dept         TEXT NOT NULL,       -- подразделение
    model        TEXT NOT NULL,
    cartridge    TEXT NOT NULL,       -- тип картриджа
    monthly_rate REAL DEFAULT 0.5,   -- норма расхода в месяц (штук)
    price        INTEGER DEFAULT 600, -- цена картриджа (руб.)
    active       INTEGER DEFAULT 1,  -- 0 = деактивирован
    note         TEXT DEFAULT ''
);
```

### Таблица `records`
```sql
CREATE TABLE records (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    printer_id INTEGER NOT NULL,
    year       INTEGER NOT NULL,
    month      INTEGER NOT NULL,      -- 1–12
    qty        INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_by TEXT DEFAULT '',
    UNIQUE(printer_id, year, month)   -- один факт на принтер/месяц
);
```

### Таблица `toners`
```sql
CREATE TABLE toners (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    monthly_rate REAL DEFAULT 0.3,
    price        INTEGER DEFAULT 1300,
    active       INTEGER DEFAULT 1
);
```

### Таблица `toner_records`
```sql
CREATE TABLE toner_records (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    toner_id INTEGER NOT NULL,
    year     INTEGER NOT NULL,
    month    INTEGER NOT NULL,
    qty      INTEGER DEFAULT 0,
    updated_by TEXT DEFAULT '',
    UNIQUE(toner_id, year, month)
);
```

### Таблица `stock`
```sql
CREATE TABLE stock (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    cartridge  TEXT NOT NULL UNIQUE,  -- название картриджа
    qty        INTEGER DEFAULT 0,
    min_qty    INTEGER DEFAULT 2,     -- порог оповещения
    price      INTEGER DEFAULT 0,
    note       TEXT DEFAULT '',
    updated_at TEXT,
    updated_by TEXT DEFAULT ''
);
```

### Таблица `stock_log`
```sql
CREATE TABLE stock_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    cartridge  TEXT NOT NULL,
    change_qty INTEGER NOT NULL,      -- положительный = приход, отрицательный = расход
    reason     TEXT DEFAULT '',
    created_at TEXT,
    created_by TEXT DEFAULT ''
);
```

### Таблица `equipment`
```sql
CREATE TABLE equipment (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    floor            TEXT NOT NULL,
    dept             TEXT NOT NULL,
    responsible      TEXT DEFAULT '',  -- ответственный
    pc_name          TEXT DEFAULT '',
    pc_inv           TEXT DEFAULT '',  -- инвентарный номер ПК
    pc_brand         TEXT DEFAULT '',
    pc_model         TEXT DEFAULT '',
    pc_serial        TEXT DEFAULT '',
    pc_os            TEXT DEFAULT '',
    pc_cpu           TEXT DEFAULT '',
    pc_ram           TEXT DEFAULT '',
    pc_hdd           TEXT DEFAULT '',
    pc_ip            TEXT DEFAULT '',
    pc_mac           TEXT DEFAULT '',
    monitor          TEXT DEFAULT '',
    monitor_inv      TEXT DEFAULT '',
    monitor_serial   TEXT DEFAULT '',
    keyboard         TEXT DEFAULT '',
    mouse            TEXT DEFAULT '',
    ups              TEXT DEFAULT '',
    phone            TEXT DEFAULT '',
    other_devices    TEXT DEFAULT '',
    purchase_date    TEXT DEFAULT '',
    warranty_until   TEXT DEFAULT '',
    status           TEXT DEFAULT 'active',
    note             TEXT DEFAULT '',
    created_at       TEXT,
    updated_at       TEXT,
    updated_by       TEXT DEFAULT ''
);
```

### Таблица `equipment_history`
```sql
CREATE TABLE equipment_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    field_name   TEXT NOT NULL,    -- имя поля, которое изменилось
    old_value    TEXT DEFAULT '',
    new_value    TEXT DEFAULT '',
    changed_at   TEXT,
    changed_by   TEXT DEFAULT ''
);
```

---

## API-эндпоинты

Все `/api/...` возвращают JSON. Требуют авторизации (cookie-сессия).

### Статистика и аналитика

| Метод | URL                    | Описание                                      |
|-------|------------------------|-----------------------------------------------|
| GET   | `/api/stats`           | Сводная статистика для дэшборда               |
| GET   | `/api/analytics`       | Данные для раздела аналитики (план/факт, топ) |
| GET   | `/api/floors`          | Список этажей из таблицы printers             |

**`/api/stats` возвращает:**
- `year_spent` — фактические затраты за год (руб.)
- `year_plan` — плановые затраты (норма × цена × 12)
- `prev_year_spent` — затраты за прошлый год
- `avg_month` — средний расход за месяц (текущий год)
- `forecast` — прогноз до конца года
- `by_dept` — расход по подразделениям
- `top_printers` — ТОП-7 принтеров по сумме
- `months` — помесячный расход (факт vs план)
- `cartridge_counts` — расход по типам картриджей

### Принтеры

| Метод  | URL                      | Права    | Описание                    |
|--------|--------------------------|----------|-----------------------------|
| GET    | `/api/printers`          | viewer+  | Список всех принтеров       |
| POST   | `/api/printers`          | admin    | Добавить принтер            |
| PUT    | `/api/printers/<id>`     | admin    | Изменить принтер            |
| DELETE | `/api/printers/<id>`     | admin    | Удалить принтер             |
| GET    | `/api/cartridge-names`   | viewer+  | Уникальные типы картриджей  |

### Записи расхода картриджей

| Метод  | URL              | Права      | Описание                          |
|--------|------------------|------------|-----------------------------------|
| GET    | `/api/records`   | viewer+    | Расход за год (параметр `?year=`) |
| POST   | `/api/records`   | operator+  | Сохранить/обновить запись         |

POST-тело: `{ printer_id, year, month, qty }`
При `qty=0` запись удаляется.

### Тонеры

| Метод  | URL                         | Права     | Описание                  |
|--------|-----------------------------| ----------|---------------------------|
| GET    | `/api/toners`               | viewer+   | Список тонеров            |
| POST   | `/api/toners`               | admin     | Добавить тонер            |
| PUT    | `/api/toners/<id>`          | admin     | Изменить тонер            |
| DELETE | `/api/toners/<id>`          | admin     | Удалить тонер             |
| POST   | `/api/toner_records`        | operator+ | Записать расход тонера    |

### Склад

| Метод  | URL                    | Права     | Описание                           |
|--------|------------------------|-----------|------------------------------------|
| GET    | `/api/stock`           | viewer+   | Остатки по всем картриджам         |
| POST   | `/api/stock`           | operator+ | Обновить остаток (приход/коррекция)|
| POST   | `/api/stock/move`      | operator+ | Списание со склада                 |
| GET    | `/api/stock/log`       | viewer+   | Журнал движения склада             |
| GET    | `/api/stock/alerts`    | viewer+   | Картриджи ниже минимального запаса |

POST `/api/stock` тело: `{ cartridge, qty, min_qty, price, note, change_qty, reason }`
POST `/api/stock/move` тело: `{ cartridge, qty, reason }`

### Оборудование

| Метод  | URL                            | Права     | Описание                        |
|--------|--------------------------------|-----------|---------------------------------|
| GET    | `/api/equipment`               | viewer+   | Список всей техники             |
| POST   | `/api/equipment`               | operator+ | Добавить запись                 |
| PUT    | `/api/equipment/<id>`          | operator+ | Обновить запись (с историей)    |
| DELETE | `/api/equipment/<id>`          | admin     | Удалить запись                  |
| GET    | `/api/equipment/<id>/history`  | viewer+   | История изменений записи        |
| GET    | `/api/equipment/stats`         | viewer+   | Сводная статистика по технике   |
| GET    | `/api/equipment/depts`         | viewer+   | Список подразделений            |
| GET    | `/api/equipment/win11`         | viewer+   | Анализ совместимости с Win11    |

PUT `/api/equipment/<id>` автоматически записывает в `equipment_history` все изменившиеся поля.

### Пользователи и бэкапы _(только admin)_

| Метод  | URL                        | Описание                         |
|--------|----------------------------|----------------------------------|
| GET    | `/api/users`               | Список пользователей             |
| POST   | `/api/users`               | Добавить пользователя            |
| PUT    | `/api/users/<id>`          | Изменить роль/пароль             |
| DELETE | `/api/users/<id>`          | Удалить пользователя             |
| POST   | `/api/backup`              | Создать резервную копию          |
| GET    | `/api/backups`             | Список резервных копий           |
| GET    | `/api/backup/download/<f>` | Скачать резервную копию          |

### Экспорт

| Метод | URL                          | Описание                              |
|-------|------------------------------|---------------------------------------|
| GET   | `/export/excel/<report>`     | Скачать Excel-файл (openpyxl)         |
| GET   | `/export/print/<report>`     | HTML-страница для печати              |

Доступные `<report>`: `cartridges`, `toners`, `analytics`, `stock`, `equipment`

> **Примечание:** Для Excel-экспорта требуется `openpyxl`. Установить: `pip install openpyxl`
> Если не установлен — вернётся ошибка 400 с подсказкой.

---

## Авторизация

Сессия на основе cookie (Flask `session`). Пароли хранятся как SHA-256 хэш.

```python
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
```

Два декоратора:
- `@login_required` — проверяет наличие `user_id` в сессии
- `@admin_required` — проверяет `role == "admin"`

Оператор (`operator`) не имеет своего декоратора — проверяется внутри функций где нужно.

---

## Анализ совместимости с Windows 11

Функция `check_win11_compat(cpu, ram_str)` в начале `app.py`.

Анализирует строки CPU и RAM из таблицы `equipment` и возвращает один из четырёх статусов:

| Статус        | Значение                                    |
|---------------|---------------------------------------------|
| `compatible`  | CPU совместим, RAM ≥ 4 ГБ                   |
| `needs_upgrade`| CPU совместим, но RAM < 4 ГБ               |
| `incompatible`| CPU не поддерживается Windows 11            |
| `unknown`     | Нет данных или не удалось определить        |

Логика по CPU:
- **Intel Core 2 / старые Celeron / старые Pentium** → несовместим
- **Intel Core i3/i5/i7/i9, 8+ поколение** → совместим (по номеру модели)
- **Intel 11th/12th/13th Gen** → совместим
- **Celeron G5900+** → совместим
- **Pentium Gold G7000+** → совместим (12-е поколение)
- **AMD Ryzen** → совместим (серия 3000 и выше)
- **AMD Athlon / старые AMD** → несовместим

> TPM 2.0 программно не проверяется — только CPU + RAM.

Эндпоинт `/api/equipment/win11` возвращает:
```json
{
  "compatible": 21,
  "needs_upgrade": 0,
  "incompatible": 24,
  "unknown": 2,
  "total": 47,
  "details": [ { "id", "dept", "floor", "pc_cpu", "pc_ram", "status", "reason" } ]
}
```

---

## Резервные копии

- Хранятся в папке `backups/` (создаётся автоматически)
- Имя файла: `data_YYYYMMDD_HHMMSS.db`
- Реализация: `shutil.copy2(DB_PATH, backup_path)` — простое копирование файла БД
- Автоматическая очистка: хранится не более 30 файлов (удаляются самые старые)
- Скачивание через `/api/backup/download/<filename>`

---

## Инициализация базы данных

При каждом запуске `app.py` вызывается `init_db()`:
1. Создаёт таблицы (`CREATE TABLE IF NOT EXISTS`)
2. Добавляет пользователя `admin` с паролем `admin123` (если не существует)
3. Если таблица `printers` пустая — вызывает `seed_printers(db)`
4. Если таблица `toners` пустая — вызывает `seed_toners(db)`

Чтобы добавить свои начальные данные — отредактируйте `seed_printers()` и `seed_toners()` в `app.py`.

---

## Как добавить новый раздел

1. Создать HTML-шаблон в `templates/`
2. Добавить маршрут страницы (`@app.route(...)`) рядом с остальными страничными маршрутами
3. Добавить API-эндпоинты (`/api/...`)
4. Добавить ссылку в навигацию в `templates/base.html`
5. При необходимости — добавить таблицу в `init_db()` и создать её `CREATE TABLE IF NOT EXISTS`

---

## Зависимости

| Пакет      | Зачем                                   | Обязательный |
|------------|-----------------------------------------|:------------:|
| flask      | Веб-фреймворк                           | Да           |
| waitress   | WSGI-сервер для Windows                 | Нет          |
| gunicorn   | WSGI-сервер для Linux                   | Нет          |
| openpyxl   | Экспорт в Excel                         | Нет          |

Стандартные библиотеки Python (не нужно устанавливать): `sqlite3`, `hashlib`, `os`, `shutil`, `json`, `io`, `datetime`, `re`
