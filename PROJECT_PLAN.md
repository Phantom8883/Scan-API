# PENTEST-PLATFORM

## Полная архитектура проекта

> Версия: архитектурный план 1.0
> Назначение: автоматизированная security-assessment платформа для малого и среднего бизнеса и их разработчиков.

---

# 1. Главная идея системы

Проект — не «API над Nmap».

Nmap, HTTP scanner, DNS scanner, TLS scanner и другие инструменты являются отдельными исполнителями внутри большой системы.

Главная задача платформы:

```text
Компания
    │
    ▼
Активы / инфраструктура
    │
    ▼
Разведка
    │
    ▼
Построение attack surface
    │
    ▼
Формирование security hypotheses
    │
    ▼
Контролируемая проверка
    │
    ▼
Evidence
    │
    ▼
Findings
    │
    ▼
Risk / Prioritization
    │
    ▼
Developer-friendly remediation
    │
    ▼
Повторная проверка
```

То есть конечная ценность находится не в конкретном сканере.

Сканеры являются заменяемыми компонентами.

---

# 2. Архитектурный принцип

Система делится на два больших уровня.

```text
┌──────────────────────────────────────────────────────────────┐
│                     CONTROL / BUSINESS PLANE                 │
│                                                              │
│                         DJANGO                               │
│                                                              │
│ users / organizations / projects / billing / permissions     │
│ targets / scope / verification / configuration / admin       │
│ findings / reports / audit / business workflows              │
└──────────────────────────────┬───────────────────────────────┘
                               │
                         API / Events
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                     EXECUTION PLANE                          │
│                                                              │
│                        FASTAPI                               │
│                                                              │
│ orchestration / scanning / jobs / workers / execution        │
│ recon / HTTP / Nmap / DNS / TLS / analysis / validation      │
└──────────────────────────────────────────────────────────────┘
```

Django отвечает на вопрос:

> **Кто, что, зачем и имеет ли право это делать?**

FastAPI отвечает на вопрос:

> **Как именно выполнить техническую работу?**

---

# 3. Почему Django и FastAPI не должны смешиваться

Django не должен запускать Nmap.

FastAPI не должен заниматься:

* регистрацией пользователя;
* billing;
* подписками;
* административной панелью;
* организационной моделью;
* бизнесовыми разрешениями;
* управлением тарифами.

Получаем чёткую границу:

```text
Django
    │
    │ "Создай security assessment для Target X"
    ▼
FastAPI
    │
    │ "Принято. Создаю execution jobs."
    ▼
Workers
    │
    ▼
Scanners
```

Django владеет **бизнесовым состоянием**.

FastAPI владеет **техническим выполнением**.

---

# 4. Общая архитектура

```text
                                      ┌───────────────────┐
                                      │     FRONTEND      │
                                      │                   │
                                      │ React / Vue       │
                                      └─────────┬─────────┘
                                                │
                                      HTTPS / WebSocket
                                                │
                         ┌──────────────────────┴──────────────────────┐
                         │                                             │
                         ▼                                             ▼
              ┌─────────────────────┐                       ┌─────────────────────┐
              │       DJANGO        │                       │      FASTAPI        │
              │                     │                       │                     │
              │ Business API        │                       │ Execution API       │
              │ Admin               │                       │ Scanner Core        │
              │ Auth                │                       │ Job orchestration   │
              │ Organizations       │                       │ WebSocket events    │
              │ Projects            │                       │ Internal APIs       │
              │ Billing             │                       │                     │
              │ Targets             │                       │                     │
              │ Findings            │                       │                     │
              │ Reports             │                       │                     │
              └──────────┬──────────┘                       └──────────┬──────────┘
                         │                                             │
                         │                                             │
                         └──────────────────┬──────────────────────────┘
                                            │
                                            ▼
                              ┌────────────────────────┐
                              │      MESSAGE BUS       │
                              │                        │
                              │ Redis / RabbitMQ       │
                              │ Celery                 │
                              │ Events                 │
                              └────────────┬───────────┘
                                           │
             ┌─────────────────────────────┼─────────────────────────────┐
             │                             │                             │
             ▼                             ▼                             ▼
   ┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
   │  RECON WORKERS   │          │ SECURITY WORKERS │          │ ANALYSIS WORKERS │
   │                  │          │                  │          │                  │
   │ Nmap             │          │ HTTP checks      │          │ Correlation      │
   │ DNS              │          │ validation       │          │ Risk             │
   │ TLS              │          │ security tests   │          │ Fingerprinting   │
   │ Asset discovery  │          │ evidence         │          │ Deduplication    │
   └────────┬─────────┘          └────────┬─────────┘          └────────┬─────────┘
            │                             │                             │
            └─────────────────────────────┼─────────────────────────────┘
                                          │
                                          ▼
                               ┌──────────────────────┐
                               │     DATA LAYER       │
                               │                      │
                               │ PostgreSQL           │
                               │ Redis                │
                               │ MinIO / S3           │
                               └──────────────────────┘
```

---

# 5. Django — Business Plane

Django является главным источником истины для бизнесового состояния платформы.

## Django отвечает за:

```text
Authentication
Authorization
Users
Organizations
Memberships
Projects
Targets
Target ownership
Target verification
Scopes
Subscriptions
Billing
Plans
Usage limits
Reports
Findings
Notifications
Audit logs
Administrative operations
```

---

# 6. Django applications

Предлагаемая структура:

```text
django_backend/
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── testing.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   │
│   ├── accounts/
│   ├── organizations/
│   ├── projects/
│   ├── targets/
│   ├── assessments/
│   ├── findings/
│   ├── reports/
│   ├── billing/
│   ├── usage/
│   ├── notifications/
│   ├── audit/
│   └── integrations/
│
├── common/
│   ├── permissions/
│   ├── exceptions/
│   ├── middleware/
│   ├── validators/
│   └── utils/
│
└── manage.py
```

---

# 7. Accounts

```text
accounts
├── User
├── Authentication
├── Sessions
├── API credentials
├── Password reset
└── MFA
```

Пользователь не должен напрямую владеть всей системой.

Основная модель владения:

```text
User
  │
  ▼
Organization
  │
  ├── Member
  ├── Project
  ├── Subscription
  └── Usage
```

---

# 8. Organizations

Основная multi-tenant граница.

```text
Organization
│
├── members
├── projects
├── targets
├── assessments
├── findings
├── reports
├── subscription
└── usage
```

Каждый запрос должен быть разрешён относительно organization context.

Это предотвращает ситуацию:

```text
User A
   ↓
угадывает UUID
   ↓
получает данные Organization B
```

UUID сам по себе не является authorization.

---

# 9. Projects

```text
Organization
    │
    ├── Project A
    │     ├── Target
    │     ├── Assessment
    │     ├── Findings
    │     └── Reports
    │
    └── Project B
          ├── Target
          ├── Assessment
          └── ...
```

Project является логической границей assessment.

---

# 10. Targets

Target — один из важнейших объектов системы.

```text
Target
├── id
├── project
├── hostname / domain
├── verification_status
├── ownership
├── scope
├── created_at
└── metadata
```

Состояния:

```text
PENDING_VERIFICATION
        │
        ▼
VERIFIED
        │
        ▼
ACTIVE
        │
        ▼
DISABLED
```

Система **не должна позволять выполнять активные проверки произвольного target**, пришедшего из HTTP-запроса.

Target должен существовать в системе и принадлежать соответствующей организации.

---

# 11. Target Verification

```text
User
 │
 ▼
Add target
 │
 ▼
VerificationToken
 │
 ▼
Ownership verification
 │
 ▼
Target VERIFIED
 │
 ▼
Allowed for assessment
```

Это фундаментальная security boundary.

---

# 12. Scope

Для каждого assessment существует scope.

```text
Assessment
│
├── included targets
├── excluded targets
├── allowed modules
├── execution limits
└── schedule
```

Scope должен проверяться **до постановки задачи worker'у**.

---

# 13. Assessments

Assessment — бизнесовая сущность, представляющая security assessment.

```text
Assessment
├── project
├── created_by
├── status
├── scope
├── configuration
├── started_at
├── completed_at
└── execution_id
```

Состояния:

```text
DRAFT
  ↓
QUEUED
  ↓
RUNNING
  ↓
ANALYZING
  ↓
COMPLETED
```

В случае ошибок:

```text
RUNNING
   │
   ▼
FAILED
```

---

# 14. Findings

Finding — уже не raw scanner output.

Это нормализованная проблема безопасности.

```text
Finding
├── asset
├── category
├── severity
├── confidence
├── title
├── description
├── evidence
├── remediation
├── first_seen
├── last_seen
└── status
```

Статусы:

```text
OPEN
ACKNOWLEDGED
IN_PROGRESS
RESOLVED
REOPENED
FALSE_POSITIVE
```

---

# 15. Reports

Reports собираются из нормализованных данных.

```text
Assessment
    │
    ▼
Findings
    │
    ▼
Risk aggregation
    │
    ▼
Report generation
    │
    ├── HTML
    ├── PDF
    └── JSON
```

Генерация отчёта не должна блокировать HTTP-запрос.

Это worker job.

---

# 16. Billing

Billing полностью находится в Django.

```text
Organization
    │
    ▼
Plan
    │
    ├── max targets
    ├── max assessments
    ├── concurrent jobs
    ├── retention
    └── available modules
```

FastAPI не должен решать:

```text
"Может ли пользователь купить этот тариф?"
```

Он получает уже разрешённую execution policy.

---

# 17. Usage

Отдельный модуль:

```text
usage
├── scan count
├── worker minutes
├── assets
├── storage
└── API usage
```

Это понадобится и для billing, и для rate limiting.

---

# 18. Django Admin

Django Admin — административная плоскость оператора.

Через неё управляются:

```text
Users
Organizations
Projects
Targets
Assessments
Findings
Plans
Subscriptions
Usage
Workers
Audit logs
Feature flags
System configuration
```

Но Admin **не должен напрямую запускать произвольные системные команды**.

Даже администратор должен инициировать нормальный application workflow.

---

# 19. FastAPI — Execution Plane

FastAPI отвечает за техническую сторону системы.

```text
fastapi/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── health.py
│   │   ├── jobs.py
│   │   ├── scans.py
│   │   └── websocket.py
│   │
│   ├── application/
│   │   ├── orchestration/
│   │   ├── jobs/
│   │   └── workflows/
│   │
│   ├── domain/
│   │   ├── jobs/
│   │   ├── assets/
│   │   ├── findings/
│   │   └── policies/
│   │
│   ├── infrastructure/
│   │   ├── celery/
│   │   ├── redis/
│   │   ├── postgres/
│   │   └── object_storage/
│   │
│   └── workers/
│       ├── recon/
│       ├── discovery/
│       ├── web/
│       ├── analysis/
│       ├── validation/
│       └── reports/
```

---

# 20. FastAPI services

Я бы разделил execution layer на следующие логические сервисы.

```text
1. Execution API
2. Orchestrator
3. Recon Service
4. Asset Discovery Service
5. Attack Surface Analysis Service
6. Security Validation Service
7. Findings/Correlation Service
8. Report Service
9. Notification/Event Service
```

При этом **не обязательно сразу делать каждый из них отдельным Docker/microservice**.

На первом этапе некоторые можно держать в одном FastAPI deployment с отдельными Celery queues.

---

# 21. Execution API

Получает команду:

```text
"Запустить assessment X"
```

Проверяет:

```text
execution token
assessment
scope
allowed modules
limits
idempotency
```

После этого создаёт execution graph.

---

# 22. Orchestrator

Это центральный координатор.

```text
Assessment
     │
     ▼
Orchestrator
     │
     ├── Recon
     │
     ├── Discovery
     │
     ├── Analysis
     │
     ├── Validation
     │
     └── Reporting
```

Он **не должен сам выполнять тяжёлую работу**.

Он только управляет workflow.

---

# 23. Worker Architecture

Здесь начинается множество workers.

```text
Celery
│
├── recon queue
│   ├── nmap worker
│   ├── dns worker
│   ├── tls worker
│   └── asset discovery worker
│
├── web queue
│   ├── http worker
│   ├── crawler worker
│   └── technology detection worker
│
├── analysis queue
│   ├── fingerprint worker
│   ├── correlation worker
│   └── risk worker
│
├── validation queue
│   └── controlled security validation workers
│
└── reports queue
    ├── html worker
    ├── pdf worker
    └── export worker
```

---

# 24. Recon Service

Задача:

> построить техническое представление поверхности.

```text
Target
  │
  ├── DNS
  ├── Network
  ├── Ports
  ├── Services
  ├── TLS
  └── HTTP metadata
```

Nmap является только одним worker'ом:

```text
Recon Service
    │
    ├── Nmap
    ├── DNS
    ├── TLS
    └── HTTP metadata
```

---

# 25. Nmap Worker

Nmap worker:

```text
input:
    verified target
    approved scope
    approved profile

output:
    normalized network observations
```

Не:

```text
raw arbitrary shell command
```

Worker получает **структурированный job**.

```text
ScanProfile
Target
Timeout
Scope
ResourcePolicy
```

и сам строит допустимую команду.

---

# 26. Asset Discovery

Recon может обнаружить дополнительные assets.

Например:

```text
example.com
    │
    ├── api.example.com
    ├── admin.example.com
    └── static.example.com
```

Но обнаруженный asset **не становится автоматически разрешённым для активного тестирования**.

Это критически важно.

```text
DISCOVERED
    │
    ▼
PENDING_SCOPE_REVIEW
    │
    ▼
APPROVED
    │
    ▼
VALIDATION_ALLOWED
```

Для полностью автоматического режима это может быть выражено policy, заранее согласованной владельцем проекта.

---

# 27. Attack Surface Service

Получает результаты Recon:

```text
ports
services
hosts
technologies
DNS
HTTP
TLS
```

и создаёт:

```text
AttackSurface
```

Пример:

```text
Asset
│
├── nginx
├── HTTPS
├── API
├── authentication endpoint
└── exposed service
```

Этот сервис **не обязан выполнять проверки**.

Его задача — определить:

> какие security hypotheses существуют.

---

# 28. Hypothesis Model

```text
SecurityHypothesis
├── asset_id
├── category
├── confidence
├── reason
├── required_validation
└── policy
```

Например:

```text
"Potentially exposed service"

"Potential outdated component"

"Potentially insecure TLS configuration"

"Potentially exposed administrative interface"
```

Это промежуточный слой между discovery и validation.

---

# 29. Security Validation Service

Это отдельный execution layer.

```text
Hypothesis
     │
     ▼
Validation Policy
     │
     ▼
Security Test
     │
     ▼
Evidence
```

Основной принцип:

> Система должна подтверждать конкретную гипотезу, а не предоставлять произвольный механизм атаки.

Каждый validation worker:

```text
получает:
    hypothesis
    target
    scope
    policy
    timeout

возвращает:
    status
    evidence
    confidence
    metadata
```

---

# 30. Почему validation нужно отделить

Потому что Recon и Validation имеют разные свойства.

Recon:

```text
широкий
относительно безопасный
много targets
много параллельных jobs
```

Validation:

```text
более чувствительный
строго ограниченный
требует audit
требует scope
требует resource limits
```

Поэтому:

```text
recon workers ≠ validation workers
```

И на инфраструктурном уровне они могут иметь разные:

```text
containers
permissions
network policies
queues
timeouts
resource limits
```

---

# 31. Findings / Correlation Service

Raw results разных workers нельзя просто складывать в одну таблицу.

Нужна нормализация:

```text
Nmap result
      │
HTTP result
      │
TLS result
      │
DNS result
      │
      ▼
Normalized Observation
      │
      ▼
Correlation
      │
      ▼
Finding
```

Например несколько наблюдений могут относиться к одной проблеме.

---

# 32. Finding lifecycle

```text
Observation
    │
    ▼
Candidate Finding
    │
    ▼
Validation
    │
    ▼
Confirmed Finding
    │
    ▼
Risk Calculation
    │
    ▼
Developer Finding
```

---

# 33. Risk Engine

Risk не должен быть просто:

```text
severity = "high"
```

Можно учитывать:

```text
severity
confidence
asset criticality
exposure
exploitability
business context
```

Получаем:

```text
Risk Score
```

Но бизнес-контекст должен приходить из Django.

Например:

```text
Asset:
production API

criticality:
CRITICAL
```

FastAPI может технически обнаружить проблему, но Django знает бизнесовый контекст проекта.

---

# 34. Developer-facing output

Именно здесь должна находиться значительная часть коммерческой ценности.

Не:

```text
TCP 5432 OPEN
```

а:

```text
HIGH

Publicly reachable database service

Asset:
api.example.com

Evidence:
PostgreSQL service detected on public interface.

Why it matters:
A database service is exposed outside the expected
application network boundary.

Recommended action:
Restrict inbound access through firewall/security groups.

Status:
Needs review
```

---

# 35. Event-driven architecture

Основной pipeline:

```text
AssessmentCreated
        │
        ▼
ExecutionStarted
        │
        ▼
ReconRequested
        │
        ▼
ReconCompleted
        │
        ▼
AssetsDiscovered
        │
        ▼
AttackSurfaceUpdated
        │
        ▼
HypothesesCreated
        │
        ▼
ValidationRequested
        │
        ▼
ValidationCompleted
        │
        ▼
FindingsCreated
        │
        ▼
RiskCalculated
        │
        ▼
AssessmentCompleted
        │
        ▼
ReportRequested
        │
        ▼
ReportReady
```

---

# 36. Redis

Redis используется для:

```text
Celery broker
distributed locks
rate limits
short-lived state
progress
pub/sub
caching
```

Но Redis не должен становиться основной persistent database.

---

# 37. PostgreSQL

PostgreSQL — persistent source of truth.

Django:

```text
users
organizations
projects
targets
billing
findings
reports
audit
```

FastAPI:

```text
execution
jobs
observations
scan results
worker state
```

При этом границы владения таблицами должны быть определены заранее.

Не должно быть:

```text
Django ORM
       ↓
произвольно изменяет execution tables FastAPI
```

и наоборот.

---

# 38. Object Storage

MinIO / S3:

```text
raw scan XML
raw JSON
screenshots
large evidence
reports
exports
artifacts
```

PostgreSQL хранит metadata:

```text
artifact_id
scan_id
type
size
hash
storage_key
created_at
```

а не гигабайты raw output.

---

# 39. WebSocket

FastAPI предоставляет realtime execution events.

```text
Worker
  │
  ▼
Event
  │
  ▼
Redis Pub/Sub
  │
  ▼
FastAPI WebSocket
  │
  ▼
Frontend
```

Например:

```text
assessment.started
recon.started
asset.discovered
recon.completed
validation.started
finding.created
assessment.completed
```

---

# 40. Audit Log

Для security-продукта audit является обязательным.

Записывать:

```text
who
what
when
organization
project
target
assessment
action
result
```

Особенно:

```text
target added
target verified
scope changed
assessment started
module enabled
validation executed
finding changed
report downloaded
```

---

# 41. Security boundaries

Система должна иметь несколько независимых уровней защиты.

```text
Internet
   │
   ▼
API Gateway
   │
   ▼
Authentication
   │
   ▼
Organization authorization
   │
   ▼
Project authorization
   │
   ▼
Target ownership
   │
   ▼
Target verification
   │
   ▼
Assessment scope
   │
   ▼
Execution policy
   │
   ▼
Worker isolation
   │
   ▼
Resource limits
```

Даже если один слой ошибся, следующий должен ограничить ущерб.

---

# 42. Worker isolation

Workers, выполняющие внешние security checks, не должны иметь доступ ко всей инфраструктуре.

Отдельно:

```text
API network
Database network
Worker network
Scanner network
Storage network
```

Например:

```text
Internet
   │
   ▼
Scanner Worker
   │
   ├── allowed target network
   │
   └── no direct access to
       PostgreSQL / Redis administration
```

---

# 43. Worker resource policy

Для каждого типа worker:

```text
CPU
Memory
Timeout
Concurrency
Network access
Filesystem
Process limit
```

Например концептуально:

```text
Nmap worker:
    CPU: limited
    memory: limited
    timeout: bounded
    concurrency: bounded

Report worker:
    no external network
    CPU bounded
    memory bounded
```

---

# 44. Idempotency

Любая команда типа:

```text
start assessment
```

должна иметь idempotency semantics.

Иначе:

```text
POST
POST
POST
POST
```

может создать четыре одинаковых assessment.

Нужен:

```text
Idempotency-Key
```

и server-side state.

---

# 45. Retry policy

Не все задачи можно retry одинаково.

```text
Database timeout
    → retry

Redis temporary failure
    → retry

Nmap target timeout
    → возможно retry

Invalid target
    → NO retry

Authorization failure
    → NO retry

Policy violation
    → NO retry
```

Retry является частью domain policy, а не просто настройкой Celery.

---

# 46. Dead Letter Queue

Для неуспешных jobs:

```text
Celery
  │
  ▼
retry
  │
  ▼
retry
  │
  ▼
failed
  │
  ▼
dead-letter / failed-jobs
```

После этого оператор может расследовать проблему.

---

# 47. Observability

В проекте должны быть:

```text
Prometheus
Grafana
structured logging
distributed tracing
health checks
metrics
```

Метрики:

```text
scan_duration
worker_duration
queue_latency
queue_depth
scan_success_total
scan_failure_total
finding_total
validation_total
```

---

# 48. Correlation IDs

Каждая операция получает:

```text
request_id
organization_id
project_id
assessment_id
job_id
```

Например:

```text
request_id = ...
assessment_id = ...
job_id = ...
```

И эти значения проходят через:

```text
Django
 ↓
FastAPI
 ↓
Celery
 ↓
Worker
 ↓
Database
 ↓
logs
```

Тогда можно восстановить путь конкретного assessment.

---

# 49. Docker infrastructure

Концептуально:

```text
docker-compose
│
├── django
├── fastapi
│
├── celery-recon
├── celery-web
├── celery-analysis
├── celery-validation
├── celery-reports
│
├── postgres
├── redis
├── minio
│
├── prometheus
└── grafana
```

Позже это может переехать в Kubernetes.

Но **не нужно начинать с Kubernetes**.

Сначала Docker Compose.

---

# 50. Репозитории

Я бы разделил код примерно так:

```text
pentest-platform/
│
├── backend-django/
│
├── scanner-fastapi/
│
├── workers/
│
├── frontend/
│
├── infrastructure/
│   ├── docker/
│   ├── prometheus/
│   └── grafana/
│
├── docs/
│
└── .github/
    └── workflows/
```

На раннем этапе workers могут физически находиться внутри FastAPI repository, но логически оставаться отдельными bounded contexts.

---

# 51. Django → FastAPI contract

Django не должен передавать FastAPI произвольные команды.

Контракт:

```json
{
    "assessment_id": "...",
    "organization_id": "...",
    "project_id": "...",
    "scope": {
        "targets": ["..."]
    },
    "modules": [
        "recon",
        "web"
    ],
    "execution_policy": {
        "max_duration": 300,
        "max_concurrency": 5
    }
}
```

FastAPI принимает именно этот **domain command**.

---

# 52. FastAPI → Django

FastAPI возвращает:

```text
execution_id
status
progress
findings
completion
```

Но не должен самовольно менять бизнесовую модель.

Лучше:

```text
FastAPI
   │
   ▼
Domain Events
   │
   ▼
Django consumer
   │
   ▼
Business state
```

---

# 53. Главный data flow

Полностью:

```text
USER
 │
 ▼
DJANGO
 │
 ├── authentication
 ├── authorization
 ├── organization
 ├── project
 ├── target
 ├── verification
 ├── scope
 └── assessment
 │
 ▼
FASTAPI
 │
 ▼
ORCHESTRATOR
 │
 ▼
CELERY
 │
 ├───────────────────────┐
 ▼                       ▼
RECON                   WEB
 │                       │
 ├─ Nmap                 ├─ HTTP
 ├─ DNS                  ├─ crawler
 ├─ TLS                  └─ tech detection
 └─ discovery
 │                       │
 └───────────┬───────────┘
             ▼
      NORMALIZATION
             │
             ▼
      ATTACK SURFACE
             │
             ▼
       HYPOTHESES
             │
             ▼
        VALIDATION
             │
             ▼
          EVIDENCE
             │
             ▼
       CORRELATION
             │
             ▼
        FINDINGS
             │
             ▼
        RISK ENGINE
             │
             ▼
        DJANGO STATE
             │
             ▼
          REPORT
             │
             ▼
          USER
```

---

# 54. Главная сущность — Assessment

Вместо того чтобы проектировать всё вокруг Nmap, центральной сущностью execution architecture должен стать:

```text
Assessment
```

Он связывает:

```text
Organization
     │
Project
     │
Scope
     │
Targets
     │
Modules
     │
Execution
     │
Observations
     │
Findings
     │
Report
```

Это значительно лучше масштабируется.

---

# 55. Module system

В дальнейшем каждый scanner реализует общий контракт.

Концептуально:

```text
ScannerModule
├── metadata
├── capabilities
├── input schema
├── execution policy
├── output schema
└── worker
```

Например:

```text
NmapModule
DNSModule
TLSModule
HTTPModule
TechnologyModule
```

Позже:

```text
ContainerModule
DependencyModule
API security module
Cloud configuration module
```

---

# 56. Module lifecycle

```text
registered
    │
    ▼
enabled
    │
    ▼
selected for assessment
    │
    ▼
queued
    │
    ▼
running
    │
    ▼
completed
```

Модуль не должен иметь права самостоятельно выбирать следующий модуль.

Orchestrator решает workflow.

---

# 57. Два вида результатов

Это особенно важно.

## Observation

Факт:

```text
Port 443 is open.
nginx detected.
TLS certificate expires in X days.
```

## Finding

Интерпретация:

```text
Potentially insecure configuration.
```

Нельзя смешивать эти понятия.

```text
Scanner
   ↓
Observation
   ↓
Analysis
   ↓
Finding
```

---

# 58. Почему эта архитектура коммерчески интереснее

Продукт продаёт не:

```text
Nmap
```

и не:

```text
FastAPI
```

Он продаёт:

```text
Discovery
+
Continuous assessment
+
Correlation
+
Validation
+
Prioritization
+
Developer remediation
```

То есть разработчик получает ответ:

> **«Что у меня небезопасно, насколько это важно, почему система так решила и что мне исправить?»**

А не просто список портов.

---

# 59. Roadmap

## Phase 0 — Foundation

```text
Django
FastAPI
PostgreSQL
Redis
Docker
authentication
organizations
projects
targets
verification
```

---

## Phase 1 — Assessment Core

```text
Assessment model
Scope
Execution
Celery
job state
idempotency
audit
```

---

## Phase 2 — Recon

```text
Nmap worker
DNS worker
HTTP metadata worker
TLS worker
normalization
asset inventory
```

---

## Phase 3 — Attack Surface

```text
asset graph
service fingerprinting
hypotheses
correlation
```

---

## Phase 4 — Controlled Validation

```text
validation framework
policy engine
evidence
isolated workers
resource limits
audit
```

Конкретные активные security checks проектируются **после** того, как scope/policy/isolation готовы.

---

## Phase 5 — Findings

```text
finding lifecycle
deduplication
risk
confidence
severity
business criticality
remediation
```

---

## Phase 6 — Developer Experience

```text
dashboard
finding details
remediation
history
diffs
notifications
API
Webhooks
CI integration
```

---

## Phase 7 — Reports

```text
HTML
PDF
JSON
executive report
technical report
developer report
```

---

## Phase 8 — Continuous Security

```text
scheduled assessments
asset changes
new exposure
regression detection
finding reopening
baseline comparison
```

---

# 60. Самая важная архитектурная картина

В конечном итоге я вижу проект так:

```text
                         ┌────────────────────┐
                         │      USER / SMB     │
                         └──────────┬─────────┘
                                    │
                                    ▼
                         ┌────────────────────┐
                         │       DJANGO       │
                         │                    │
                         │ Business Platform  │
                         │                    │
                         │ Users              │
                         │ Organizations      │
                         │ Projects           │
                         │ Targets            │
                         │ Scope              │
                         │ Billing            │
                         │ Findings           │
                         │ Reports            │
                         │ Admin              │
                         └──────────┬─────────┘
                                    │
                             Assessment
                                    │
                                    ▼
                         ┌────────────────────┐
                         │      FASTAPI       │
                         │                    │
                         │ Execution Platform │
                         │                    │
                         │ Orchestrator       │
                         │ Job API             │
                         │ Events              │
                         └──────────┬─────────┘
                                    │
                                  Celery
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
 ┌────────────────┐       ┌────────────────┐       ┌────────────────┐
 │ RECON WORKERS  │       │ ANALYSIS       │       │ VALIDATION     │
 │                │       │ WORKERS        │       │ WORKERS        │
 │ Nmap           │       │                │       │                │
 │ DNS            │       │ fingerprinting │       │ controlled     │
 │ TLS            │       │ correlation    │       │ checks         │
 │ HTTP           │       │ hypotheses     │       │ evidence       │
 └───────┬────────┘       └───────┬────────┘       └───────┬────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                                  ▼
                         ┌────────────────────┐
                         │    OBSERVATIONS    │
                         └──────────┬─────────┘
                                    │
                                    ▼
                         ┌────────────────────┐
                         │      FINDINGS      │
                         │                    │
                         │ Risk               │
                         │ Confidence         │
                         │ Evidence           │
                         │ Remediation        │
                         └──────────┬─────────┘
                                    │
                                    ▼
                         ┌────────────────────┐
                         │     DEVELOPER      │
                         │                    │
                         │ What happened?     │
                         │ Why?               │
                         │ How serious?       │
                         │ How fix?           │
                         └────────────────────┘


              ┌───────────────────────────────────┐
              │            DATA LAYER              │
              │                                   │
              │ PostgreSQL  │ Redis │ MinIO/S3    │
              └───────────────────────────────────┘
```

---

# 61. Главная граница проекта

Вся система должна держаться на следующей цепочке:

```text
BUSINESS
   ↓
AUTHORIZATION
   ↓
SCOPE
   ↓
ORCHESTRATION
   ↓
OBSERVATION
   ↓
ANALYSIS
   ↓
VALIDATION
   ↓
EVIDENCE
   ↓
FINDING
   ↓
REMEDIATION
```

А не на:

```text
API
 ↓
Nmap
 ↓
JSON
```

Это принципиальная разница.

---

# 62. Что мы НЕ делаем сейчас

На этом этапе намеренно не проектируем глубоко:

* конкретные Nmap arguments;
* конкретные offensive techniques;
* конкретные exploit chains;
* payloads;
* обход защит;
* brute-force механизмы;
* конкретные vulnerability exploitation workflows.

Сначала проектируем **контракт между сервисами, security boundaries, scope, worker isolation, data model и execution lifecycle**.

После этого каждый scanner/validator становится подключаемым модулем.

---

# 63. Следующий порядок разработки

После утверждения этой картины проект нужно разбивать не по принципу:

```text
"Сегодня пишем Nmap"
```

а так:

```text
1. Identity / Organization
        ↓
2. Project / Target / Verification
        ↓
3. Assessment / Scope
        ↓
4. Django ↔ FastAPI contract
        ↓
5. Execution / Celery
        ↓
6. Worker framework
        ↓
7. Observation model
        ↓
8. Recon framework
        ↓
9. Nmap module
        ↓
10. Attack Surface analysis
        ↓
11. Validation framework
        ↓
12. Findings / Risk
        ↓
13. Reports
        ↓
14. WebSocket / realtime
        ↓
15. Scheduling / continuous assessment
        ↓
16. CI/CD integration
```

**Только после этой карты имеет смысл садиться за конкретные модули.**

Именно так мы избежим ситуации, когда через несколько недель обнаружится, что Nmap worker, FastAPI, Django и база данных имеют разные представления о том, что такое `Target`, `Scan`, `Finding` и `Assessment`.
