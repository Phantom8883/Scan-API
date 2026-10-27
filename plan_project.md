# PENTEST-PLATFORM — Project Plan v2

## 0. Что изменилось относительно первой версии плана

Исходный план строился на разделении Django (Business Plane) + FastAPI (Execution Plane) — два отдельных сервиса, HTTP-контракт между ними. По ходу разработки архитектура менялась дважды:

1. Django+FastAPI → два FastAPI-сервиса (`platform-api` + `execution-api`)
2. Два FastAPI-сервиса → один `platform-api`

Причина объединения — это соло-проект, а не команда. Два сервиса означают два деплоя, межсервисную аутентификацию, два набора миграций, дублирование моделей — операционную сложность, которая оправдана для команды из нескольких человек, но не для одного разработчика на этапе MVP. Разделение можно будет вернуть позже, когда реальная нагрузка это потребует — это решение по масштабированию, не архитектурная догма, которую нужно соблюдать с первого дня.

Что **осталось неизменным** из исходной идеи, и это важно: Celery-воркеры — **по-прежнему отдельный уровень изоляции**, не слитый в один процесс с `platform-api`. Это не операционная сложность ради сложности — это требование безопасности: воркеры, которые реально атакуют цели (Validation), должны жить в отдельном контейнере с урезанными правами, отдельно от воркеров, которые просто собирают информацию (Recon). Это разделение сохраняется и в новой архитектуре.

---

## 1. Главная идея системы

Платформа автоматизирует процесс пентеста по контролируемому пайплайну: от сбора информации о цели до подтверждённых находок (findings) с оценкой риска — без произвольного "запусти что угодно против чего угодно". Каждый шаг — отдельный, узкоспециализированный модуль с чёткой границей ответственности.

---

## 2. Высокоуровневая архитектура

```
                    ┌──────────────────────────┐
                    │       platform-api         │   FastAPI, один сервис
                    │                             │
                    │  api/        — роутеры      │
                    │  services/   — бизнес-логика │
                    │  repositories/ — доступ к БД  │
                    │  core/       — auth, security │
                    │  dependencies.py — DI-сборка  │
                    └─────────────┬──────────────┘
                                  │
                ┌─────────────────┼──────────────────┐
                │                                     │
          ┌─────▼──────┐                      ┌───────▼────────┐
          │   Redis     │                      │   PostgreSQL    │
          │             │                      │                 │
          │ Celery broker│                     │ source of truth │
          │ distributed  │                     │  все сущности    │
          │   locks      │                     └─────────────────┘
          │ rate limits  │
          │ progress/    │
          │  pub-sub     │
          │ короткий кэш │
          └─────┬────────┘
                │
   ┌────────────┼─────────────┬────────────────┐
   │            │              │                 │
┌──▼───┐   ┌────▼────┐   ┌─────▼─────┐   ┌───────▼───────┐
│ recon │   │   web    │   │ analysis  │   │   validation    │   Celery queues —
│ queue │   │  queue   │   │  queue    │   │     queue       │   разный уровень
└───────┘   └──────────┘   └───────────┘   └─────────────────┘   доверия/изоляции
   │                                              │
   │ широкий, безопасный                          │ узкий, чувствительный,
   │ много параллельных job'ов                     │ строгий scope, audit,
   │                                               │ отдельный контейнер
   ▼                                               ▼
```

**Object Storage (MinIO/S3)** и **Vulnerability Feed (CVE/NVD)** — внешние по отношению к этой схеме источники/приёмники данных, подробности в разделах 11 и 14.

---

## 3. Users / Organizations / Auth — уже реализовано

```
User
  │
  └── OrganizationMembership (role: owner / admin / member)
            │
            └── Organization
                    │
                    └── Project → Target → Assessment → Execution → Job
```

Реализовано и работает:

- Регистрация (`/auth/register`) — Argon2-хэширование паролей через отдельный `ThreadPoolExecutor`, защита от timing attack (хэш считается всегда, независимо от того, занят email или нет; плюс `DUMMY_PASSWORD_HASH` — заранее посчитанный настоящий хэш, чтобы не было разницы во времени парсинга фейковой строки vs настоящей).
- Логин (`/auth/login`) — JWT access (короткий, 30 мин) + refresh (длинный, 7 дней), поле `"type"` внутри payload разделяет их, чтобы refresh нельзя было использовать как access.
- `/auth/refresh` — ротация токенов: каждый рефреш выдаёт новую пару, а не возвращает старый refresh обратно.
- `get_current_user` dependency — аутентификация (401, "кто ты").
- `require_org_role(*roles)` — авторизация (403, "что тебе разрешено"), через таблицу `OrganizationMembership`.

---

## 4. Архитектурный паттерн внутри platform-api

```
api/ (роутер)
   │   "тупой" слой — только HTTP, никакой логики
   ▼
services/ (BaseService)
   │   бизнес-правила, зависит от AbstractRepository (интерфейс), не от конкретной БД
   ▼
repositories/ (SqlAlchemyRepository, MembershipRepository)
   │   единственное место, которое знает про SQL
   ▼
PostgreSQL
```

Repository — generic (`SqlAlchemyRepository[ModelType]`) для моделей с единым `id` (через `Protocol`-ограниченный `TypeVar`), и отдельные специализированные репозитории (`MembershipRepository`) для моделей с нестандартным ключом (составной PK). `dependencies.py` — только сборка объектов через `Depends`, ни одной строчки SQL.

---

## 5. Concurrency-модель — что где используется и почему

Три разных инструмента, каждый под свою задачу, выбор не "по вкусу", а по типу нагрузки:

| Инструмент | Когда | Пример в проекте |
|---|---|---|
| `asyncio` (нативный) | I/O-bound: сеть, БД | SQLAlchemy async, TCP connect scan, HTTP-запросы в Recon |
| `ThreadPoolExecutor` | CPU-bound, но C-расширение отпускает GIL | Argon2-хэширование паролей |
| `ProcessPoolExecutor` | CPU-bound, чистый Python, GIL не отпускается | Будущий Risk Engine / корреляция findings (если окажется тяжёлой чистым Python) |
| Celery (отдельные процессы) | Изоляция + масштабирование + очереди с разным уровнем доверия | Recon/Validation воркеры |

---

## 6. Orchestrator

Координатор event-driven пайплайна (раздел 9). **Не выполняет тяжёлую работу сам** — только управляет порядком вызова остальных сервисов и состоянием Assessment.

---

## 7. Recon Service

```
Target → [Nmap worker, DNS worker, TLS worker, HTTP worker] → Observation (нормализованные)
```

- **Nmap worker** — сейчас: TCP connect scan (`asyncio.open_connection`). Следующий шаг: banner grabbing + сигнатурный fingerprinting сервисов (pattern matching по известным баннерам).
- **DNS/subdomain discovery** — brute-force по словарю (конкурентно, как в async-url-collector) + passive-метод через Certificate Transparency logs.
- **TLS/HTTP worker** — метаданные: версии протокола, заголовки, cipher suites.

Recon — широкий, относительно безопасный, много параллельных job'ов → своя Celery-очередь с мягкими лимитами.

---

## 8. Scope & Policy Engine — НОВЫЙ явный модуль

Раньше это было полем состояния у asset'а. Теперь — отдельный модуль с явной state machine, через который обязан пройти **любой** asset, прежде чем попасть в Validation:

```
DISCOVERED → PENDING_SCOPE_REVIEW → APPROVED → VALIDATION_ALLOWED
```

Почему отдельный модуль, а не поле: если проверка scope размазана по коду каждого воркера отдельно — легко один раз забыть её в новом воркере и случайно атаковать то, что не было согласовано владельцем. Централизованный модуль означает: **любой** validation-воркер обязан спросить у этого сервиса "можно ли?", прежде чем действовать — проверка в одном месте, не в N местах.

---

## 9. Attack Surface + Hypothesis Model

```
Observations → AttackSurface → SecurityHypothesis { category, confidence, reason, required_validation }
```

Rule-based слой (не ML на старте) — таблица "паттерн наблюдения → гипотеза". Confidence на первом этапе — простое взвешенное правило (чем больше независимых признаков подтверждают гипотезу, тем выше число), без статистики. ML имеет смысл добавлять только когда накопится датасет подтверждённых/опровергнутых гипотез — не раньше.

---

## 10. Security Validation Service

```
Hypothesis → Validation Policy → Security Test → Evidence
```

Принцип (без изменений из исходного плана, он верный): система подтверждает **конкретную** гипотезу, не предоставляет произвольный механизм атаки.

Примеры проверок:
- "Устаревший компонент" — сверка версии (из banner grabbing) с CVE-базой (раздел 11).
- "Небезопасная TLS-конфигурация" — проверка cipher suites и версий протокола.
- "Открытый административный интерфейс" — проверка конечного списка известных путей/дефолтных учёток.

Отдельная Celery-очередь, отдельный Docker-контейнер с урезанными правами — обязано работать только внутри `VALIDATION_ALLOWED` scope (раздел 8), с обязательным audit log (раздел 17) на каждое действие.

---

## 11. Vulnerability Intelligence Service — НОВЫЙ модуль

Без него Validation Service нечем проверять гипотезу "устаревший компонент" — реальный пробел исходного плана.

```
NVD/CVE feed (публичный, бесплатный)
        │
        ▼
Периодическая синхронизация (раз в сутки, НЕ на каждый scan)
        │
        ▼
Локальный кэш CVE-записей в PostgreSQL (версия продукта → известные уязвимости)
```

Реализуется как отдельный периодический Celery-таск (`celery beat`), не как часть scan-пайплайна — синхронизация с NVD не должна блокировать или замедлять пользовательские сканы.

---

## 12. Findings / Correlation Service

Дедупликация и объединение нескольких Observation/Evidence, относящихся к одной и той же проблеме (например, один и тот же устаревший компонент, обнаруженный и через banner grabbing, и через отдельный HTTP-заголовок) — иначе пользователь увидит 3 находки вместо одной.

---

## 13. Risk Engine

Взвешенная оценка: severity × confidence × exposure (насколько asset публично доступен). На старте — формула, не модель. CVSS-подобный скоринг, если нужна стандартизация под индустрию.

---

## 14. Object Storage (MinIO/S3) — явно вынесенный модуль

Сырой вывод воркеров — не реляционные данные, не должны лежать в Postgres:
- Сырой вывод nmap/сканеров
- Полные HTTP-тела ответов
- Скриншоты (если будут)

Postgres хранит только **ссылку** на объект в storage, не сам объект.

---

## 15. Redis — роли (никогда не persistent-хранилище результатов)

- Celery broker
- Distributed locks (не дать двум job'ам сканировать один target параллельно)
- Rate limits (ограничение запросов/сек к одной цели — техническая и этическая необходимость)
- Progress/pub-sub (прогресс job'а → WebSocket-сервис → браузер пользователя в реальном времени)
- Короткоживущий кэш

---

## 16. PostgreSQL — source of truth

Один сервис — одна схема владения таблицами, никаких межсервисных границ данных (в отличие от исходного плана с Django/FastAPI split).

---

## 17. WebSocket, Audit Log, Idempotency, Retry policy, Dead Letter Queue

Без изменений по сути из исходного плана:
- WebSocket — живой прогресс через Redis pub/sub.
- Audit Log — обязателен для всего, что проходит через Validation Service.
- Idempotency — повторный вызов одного job'а не должен создавать дубликат работы (уже частично заложено в модели `Job` — `celery_task_id`, `attempts`).
- Retry policy + Dead Letter Queue — что происходит, если job падает (сколько раз повторить, куда складывать окончательно неудавшиеся).

---

## 18. Observability, Docker infrastructure

Без изменений по сути — correlation ID на весь путь запроса через пайплайн, структурированные логи, отдельные Docker-образы под recon/validation воркеры с разными resource/network policy.

---

## 19. Главный data flow (event-driven pipeline)

```
AssessmentCreated → ExecutionStarted → ReconRequested → ReconCompleted
  → AssetsDiscovered → ScopeReview → AttackSurfaceUpdated → HypothesesCreated
  → ValidationRequested → ValidationCompleted → FindingsCreated
  → RiskCalculated → AssessmentCompleted → ReportRequested → ReportReady
```

(Добавлен `ScopeReview` между `AssetsDiscovered` и `AttackSurfaceUpdated` — отражает новый явный модуль из раздела 8, в исходном плане этот шаг подразумевался, но не был явным событием в пайплайне.)

---

## 20. Два вида результатов — Observation vs Finding

- **Observation** — сырой факт ("порт 443 открыт, сервис nginx 1.18") — результат Recon, не содержит оценки риска.
- **Finding** — подтверждённая проблема с severity/confidence — результат Validation + Correlation, то, что реально показывается пользователю как итог.

---

## 21. Текущий статус реализации (честный срез, не план — факт)

**Готово и работает:**
- Модели данных (Job, Execution, Observation, Target, Assessment, Organization, User, OrganizationMembership и т.д.)
- Repository-слой (AbstractRepository + SqlAlchemyRepository + MembershipRepository)
- Service-слой (BaseService)
- Auth целиком: регистрация, логин, refresh, get_current_user, require_org_role
- `db/session.py` с commit/rollback на уровне запроса
- TCP connect scan (базовый, на asyncio.open_connection)

**Не начато:**
- Ни один реальный защищённый бизнес-роут (targets/assessments/jobs CRUD) — `get_current_user`/`require_org_role` написаны, но ещё не применены ни на одном роуте
- Celery-воркеры — вообще не подключены, Job создаётся в БД, но ничего реально не исполняет
- Banner grabbing, DNS/TLS/HTTP recon-воркеры
- Scope/Policy Engine
- Attack Surface / Hypothesis / Validation / Vulnerability Feed / Findings / Risk Engine — весь слой целиком
- Object Storage
- WebSocket, Audit Log

---

## 22. Следующий порядок разработки (ближайшие шаги, не весь roadmap)

1. Первый реальный защищённый роут (например, `GET /organizations/{organization_id}/targets`) — чтобы увидеть auth-цепочку в деле.
2. Подключить Celery реально — простейший воркер, который берёт Job из очереди и меняет его статус в БД.
3. Banner grabbing поверх текущего TCP-сканера.
4. Scope/Policy Engine — до того, как появится хоть один validation-воркер, не после.
