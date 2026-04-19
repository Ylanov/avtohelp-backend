# RoadHelp API Contract (frozen for Android `bug_fix`)

> Инвентарь всех HTTP и WebSocket эндпоинтов, которые дёргает Android-клиент (ветка `bug_fix`, versionCode 68, 1.2.2).
> **Этот документ — источник правды при модернизации бэкенда. Ничего из перечисленного нельзя ломать без синхронного обновления фронта.**

Дата фиксации: 2026-04-19
Источник: `C:\Users\yrosh\PycharmProjects\roadhelpandroid` (branch `bug_fix`), анализ Retrofit интерфейса [app/src/main/java/ru/autohelp/server/Api.kt](../../../../../../roadhelpandroid/app/src/main/java/ru/autohelp/server/Api.kt).

## 0. Глобальные инварианты

| Свойство | Значение |
|---|---|
| Base URL (hardcoded в Android) | `http://153.80.245.74:8000/api/v1.0.0/` |
| WebSocket URL (dev) | `ws://153.80.245.74:8000/chat/stream` |
| WebSocket URL (prod) | `wss://153.80.245.74:8000/chat/stream` |
| Auth header | `Authorization: Token <token>` (НЕ `Bearer`) |
| JSON field naming | `lower_case_with_underscores` (GSON policy) |
| DateTime format | ISO 8601, **без миллисекунд**, UTC (`Z` suffix), Joda DateTime |
| Content-Type для upload | `multipart/form-data` |
| Timeout клиента | connect 5s, read 5s |
| Координаты в query | одна строка `"lat,lng"` (напр. `coordinates=55.7558,37.6173`) |
| Координаты в body | отдельные поля `geo_lat`, `geo_lon` (double) |
| Формат ошибки | `{ "errors": ["строка1", "строка2"] }` |

## 1. Аутентификация (не требует токена)

### POST `/authorization/verify`
Request: `{ "phone": "+79...", "mode": 0 }`
Response: `{ "errors": [...]? }`

### POST `/authorization/auth`
Request: `{ "phone": "+79...", "code": "12345" }`
Response: `{ "token": "...", "profile": User, "errors": [...]? }`

## 2. Профиль

| Метод | Путь | Описание |
|---|---|---|
| GET | `/userprofile/profile/detail` | Мой профиль |
| PATCH | `/userprofile/profile/detail` | Обновить мой профиль `{first_name?, last_name?, city?}` |
| PATCH | `/userprofile/profile/change_avatar` | multipart `avatar` |
| PATCH | `/userprofile/profile/update-location` | body `{geo_lat, geo_lon}` |
| GET | `/userprofile/profiles/{profileId}` | Чужой профиль |
| GET | `/userprofile/profiles?search=&cursor=` | Поиск (cursor-based) |

## 3. Друзья / Блеклист

| Метод | Путь | Описание |
|---|---|---|
| POST | `/userprofile/profile/friends/add` | `{profile: userId}` |
| GET | `/userprofile/profile/friends?limit=&offset=` | Список друзей |
| DELETE | `/userprofile/profile/friends/{friendId}/delete` | Удалить друга |
| GET | `/userprofile/profile/friends/requests/incoming?limit=&offset=` | Входящие |
| GET | `/userprofile/profile/friends/requests/outgoing?limit=&offset=&person_id=` | Исходящие |
| PATCH | `/userprofile/profile/friends/requests/incoming/{id}/approve` | Принять |
| DELETE | `/userprofile/profile/friends/requests/incoming/{id}/delete` | Отклонить |
| DELETE | `/userprofile/profile/friends/requests/outgoing/{id}/delete` | Отозвать |
| POST | `/userprofile/profile/blacklist/add` | `{profile: userId}` |
| DELETE | `/userprofile/profile/blacklist/{profileId}/delete` | Удалить из ЧС |
| GET | `/userprofile/profile/blacklist?limit=&offset=` | Список ЧС |

## 4. Машины / Справочники

| Метод | Путь | Описание |
|---|---|---|
| GET | `/catalog/cities` | Список городов |
| GET | `/car/marks?mark_name=` | Марки с поиском |
| GET | `/car/colors?color_name=` | Цвета (поле `hex_color`) |
| GET | `/car/cars?mark_name=&model_name=` | Модели |
| GET | `/userprofile/profile/cars` | Мои машины |
| POST | `/userprofile/profile/cars/add` | `{color?, car?, license_plate?}` |
| PATCH | `/userprofile/profile/cars/{carId}` | Обновить машину |
| GET | `/api/general_info` | Сборник: cities + car_colors + car_makes(с car_models) |

## 5. Запросы помощи

| Метод | Путь | Описание |
|---|---|---|
| POST | `/order/requests/create` | multipart: `full_name, phone, what_broken, where_broken, description, lat, lng, radius?, photo?` |
| GET | `/order/requests?coordinates=lat,lng` | Ближайшие запросы |
| GET | `/order/requests/count` | `{count, unread}` |
| GET | `/order/requests/{order_id}` | Детали |
| DELETE | `/order/requests/{order_id}/delete` | Удалить |

**Response Help:**
```
{ id, profile_id, issue, profile?: User, contact_phone, text_address, description,
  image?, geo_lat?, geo_lon?, is_owner?, distance? (в метрах) }
```

## 6. Чат (REST)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/chat/rooms?participant_id=&cursor=` | Список комнат |
| GET | `/chat/rooms/{roomId}` | Комната |
| POST | `/chat/rooms/private/create` | `{participant: userId}` → создаёт/возвращает приватный чат |
| GET | `/chat/messages/room/{roomId}?cursor=` | Сообщения |
| GET | `/chat/messages/room/{roomId}/count` | Всего |
| GET | `/chat/messages/room/{roomId}/unread/count` | Непрочитанные в комнате |
| GET | `/chat/messages/unread/count` | Непрочитанные глобально |

## 7. Чат (WebSocket)

URL: `ws(s)://.../chat/stream` с header `Authorization: Token <...>`.

**Server → Client** события:
- `ChatMessage`: `{ avatar?, datetime, first_name, last_name, message, message_id, msg_type, room, profile_id }`
  - `msg_type`: `"0"` = MESSAGE, `"4"` = ENTER, `"5"` = LEAVE
- `RoomCommand`, `StateTransition`, `WebSocketEvent`, сырой текст

**Client → Server** команды:
- `RoomCommand`: `{ command: "join"|"leave"|"read_message", room, messages?: [id] }`
- `ChatMessageCommand`: `{ command: "send", room, message }`

## 8. Новости

| Метод | Путь | Описание |
|---|---|---|
| GET | `/base/news?cursor=` | Лента |
| POST | `/base/news/{id}/comments` | `{text}` → Comment |
| PUT | `/base/news/{id}/toggle-like` | Toggle like |
| POST | `/base/recommendation` | multipart: `title, text, photo?` |
| GET | `/base/recommendations?cursor=` | Мои предложенные |

## 9. Push

| Метод | Путь | Описание |
|---|---|---|
| POST | `/userprofile/device` | `{registration_id, type: "android"}` |

## 10. Пагинация — два формата

**Cursor-based** (`?cursor=...`): `/userprofile/profiles`, `/chat/rooms`, `/chat/messages/...`, `/base/news`, `/base/recommendations`
**Offset-based** (`?limit=&offset=`): `/userprofile/profile/friends*`, `/userprofile/profile/blacklist`

Оба формата возвращают:
```
{ results: [...], count, next, previous, errors? }
```

## 11. Non-negotiable при миграции

1. **snake_case** всех полей (менять field naming = сломать фронт).
2. **`Token <val>`**, не `Bearer`, не `Authorization-JWT`.
3. **ISO 8601 без ms в UTC** для всех datetime.
4. **`errors: [string]`** — фронт парсит именно такую форму ошибки.
5. **Координаты:** `lat,lng` в query, `geo_lat/geo_lon` в body.
6. **`msg_type` в чат-сообщениях — строка ("0", "4", "5")**, не число.
7. **v1.0.0 в базовом URL** — пока фронт не пересобран.

## 12. Deploy plan (resolved)

Облачный сервер — IP `153.80.245.74`: **тот же, что захардкожен в Android `bug_fix`**. Двухфазный подход:

**Фаза 1 — HTTP на `:8000` (без пересборки Android).** Android уже указан на `http://153.80.245.74:8000/api/v1.0.0/` и `ws://153.80.245.74:8000/chat/stream`. Docker compose публикует api на `:8000`, ws на `:8001`; для chat на этой фазе Android продолжает ходить на тот же `:8000` (Django URL conf не экспонирует WS под HTTP — см. ограничение ниже). Runbook — [deploy/DEMO_QUICK_START.md](../deploy/DEMO_QUICK_START.md).

**Фаза 2 — HTTPS через `avtohelp24.ru` (для инвестора).** DNS → IP, `nginx + certbot` поднимается из `docker-compose.prod.yml`. Android пересобирается с `https://avtohelp24.ru/api/v1.0.0/` + `wss://avtohelp24.ru/chat/stream`.

### Известное ограничение Фазы 1

В Phase 1 WebSocket из Android пойдёт на `ws://153.80.245.74:8000/chat/stream`, но daphne слушает `:8001`, а gunicorn на `:8000` не умеет WebSocket. Для чата в Phase 1 либо:
- (a) временно перепривязать daphne на `:8000` (отключить api-контейнер — REST не работает),
- (b) либо уже на Phase 1 поднять nginx с proxy_pass `/chat/stream` → `ws:8001`, всё остальное → `api:8000`, и пересобрать Android убрав порт из `chat/stream` URL.

Для первого демо достаточно REST (аутентификация, профиль, запросы помощи). Чат подключим на Phase 2.

## 13. Gap analysis: контракт vs текущий бэкенд (на 2026-04-19)

Сверено с реальными URL-ами в `src/*/urls.py` и `src/*/urls/current.py`.

### 13.1. MISSING — нет на бэке, фронт зовёт → нужно реализовать

| Путь | Метод | Что нужно |
|---|---|---|
| `/api/general_info` | GET | Собрать в одном response: `{cities: [...], car_colors: [...], car_makes: [{id, name, car_models: [...]}]}`. Простой view поверх существующих моделей City/CarColor/CarMark/Car. |
| `/chat/messages/room/{roomId}/count` | GET | Вернуть `{count}` — всего сообщений в комнате. |
| `/chat/messages/room/{roomId}/unread/count` | GET | Вернуть `{count}` — непрочитанных в комнате для текущего юзера. |

### 13.2. EXISTS — полное совпадение, не трогать

Всё остальное из разделов 1–9 контракта имеет живой URL-паттерн и view. Файлы:
- `src/authorization/urls/current.py`
- `src/userprofile/urls.py`
- `src/order/urls/current.py`
- `src/chat/urls.py`
- `src/catalog/urls/current.py`
- `src/car/urls/current.py`
- `src/base/urls/current.py`

### 13.3. Ложные тревоги (не требуют действий)

- Имена Django-kwarg `<int:pk>` vs `{profileId}`/`{roomId}`/`{order_id}` в контракте — это **не поломка**. HTTP-клиент шлёт число в URL-позиции, Django матчит позиционно.
- Дополнительный `DELETE /userprofile/profile/cars/delete/<int:pk>` — фронт им не пользуется (фронт делает PATCH). Оставить как есть до уборки техдолга.

### 13.4. WebSocket `/chat/stream`

Реализован в `src/chat/consumers.py` (ChatConsumer), роутинг — `src/roadhelpbackend/routing.py:12`, auth — `src/chat/token_auth.py`. Поддерживает все команды (`join`/`leave`/`send`/`read_message`) и события (`msg_type: "0"/"4"/"5"`). Ничего менять не нужно.
