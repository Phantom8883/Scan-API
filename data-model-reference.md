# Справочник моделей данных — Pentest Platform

Полный каталог всех сущностей проекта: что значит название, зачем нужна, с чем связана. Организовано слоями — от бизнес-уровня (кто и что заказывает) до отчёта (что получает в итоге).

Пометка после названия:
- ✅ модель + схема уже написаны в коде
- 🆕 нужно создать с нуля (в этом файле — дизайн + схема)

---

## Слой 1 — Бизнес-сущности (кто, что, для кого)

### `User` ✅ — Пользователь
Человек, который пользуется платформой. Хранит email, хэш пароля, имя.
**Связи:** состоит в организациях через `OrganizationMembership`; создаёт `Assessment`.

### `Organization` ✅ — Организация
Компания/команда-владелец. Всё в системе в итоге принадлежит какой-то организации — это граница изоляции данных между разными клиентами платформы.
**Связи:** имеет участников (`OrganizationMembership`), владеет `Project`.

### `OrganizationMembership` ✅ — Членство в организации
Связующая таблица между `User` и `Organization`, с дополнительным полем `role` (owner/admin/member). Без неё не было бы ответа на вопрос "а имеет ли право этот конкретный юзер делать что-то в этой конкретной организации" — это и есть твой слой авторизации, который мы недавно строили (`require_org_role`).
**Связи:** `user` ↔ `organization`.

### `Project` ✅ — Проект
Контейнер внутри организации — например, "Проверка безопасности интернет-магазина" как отдельный проект, отдельный от "Проверки внутренней CRM" той же компании.
**Связи:** принадлежит `Organization`; содержит `Target`, `Assessment`.

### `Target` ✅ — Цель
Конкретный объект для проверки: домен, IP, URL, подсеть. `value` — как ввёл пользователь ("example.com"), `normalized_value` — приведённое к единому виду.
**Связи:** принадлежит `Project`; проходит `TargetVerification`; участвует в `Assessment` через `AssessmentTarget`.

### `TargetVerification` ✅ — Верификация цели
Подтверждение, что цель реально принадлежит заказчику (например, через DNS TXT-запись) — **критичный для legal/этики компонент**: без этого пентест превращается в атаку на чужую инфраструктуру без разрешения.
**Связи:** принадлежит `Target`.

### `Assessment` ✅ — Оценка (проверка)
Главная бизнес-сущность — "заказ на пентест" целиком: какой проект, кто заказал, какой статус (draft/ready/running/completed/failed), какая конфигурация (выбранные модули проверки).
**Связи:** принадлежит `Project`; создан `User` (`created_by_user`); связан с `Target` через `AssessmentTarget`; порождает `Finding` и `Report`.

### `AssessmentTarget` ✅ — связь Assessment↔Target
Таблица многие-ко-многим: один Assessment может проверять несколько Target, один Target может участвовать в нескольких Assessment со временем.

---

## Слой 2 — Выполнение (что технически происходит)

### `Execution` ✅ — Технический запуск
Один конкретный "прогон" Assessment. Разница с Assessment: Assessment — это бизнес-заказ ("проверь example.com"), Execution — конкретная техническая попытка это выполнить (может быть несколько Execution на один Assessment, если первый упал и перезапустили).

**Важная деталь, которую стоит знать:** поля `assessment_id` и `user_id` в этой модели помечены комментарием *"внешний UUID, не ForeignKey"* — это наследие той эпохи, когда `execution-api` и `platform-api` были разными сервисами с разными базами данных (настоящий `ForeignKey` между базами невозможен). Сейчас, когда всё в одной базе, технически это можно было бы превратить в настоящий `ForeignKey` — не критично, но стоит занести в список технического долга на будущее.

**Связи:** порождает `TargetSnapshot`, `Job`, `FindingCandidate`, `SecurityHypothesis`.

### `TargetSnapshot` ✅ — Снимок цели
Неизменная копия состояния `Target` на момент начала конкретного `Execution`. Зачем нужен отдельно от `Target`: Assessment может идти часами/днями, а `Target` в это время теоретически может измениться (например, пользователь поправил значение) — snapshot фиксирует, с чем реально работал сканер, для воспроизводимости и аудита. Также хранит `resolved_addresses` (резолв DNS на момент снимка) и `scope_metadata` (зачаток Scope Engine, раздел ниже).
**Связи:** принадлежит `Execution`; на него ссылаются `Job`, `Observation`, `SecurityHypothesis`, `FindingCandidate`.

### `Job` ✅ — Задача (единица работы для Celery)
Одна конкретная задача для воркера: какой модуль (`nmap`/`dns`/`tls`/`http`/`analysis`), какая очередь Celery, статус, попытки (`attempts`/`max_attempts`), `celery_task_id` для связи с реальной Celery-задачей.
**Связи:** принадлежит `Execution`; опционально привязана к `TargetSnapshot`; порождает `Observation`.

### `Observation` ✅ — Наблюдение
Сырой факт, который обнаружил `Job`: открытый порт, DNS-запись, HTTP-заголовок, TLS-сертификат. **Это ещё не вывод, не оценка — просто зафиксированный факт.** `type` — что за факт, `data` (JSON) — сами данные, `fingerprint` — для дедупликации одинаковых наблюдений из разных прогонов.
**Связи:** принадлежит `Job` и `TargetSnapshot`; имеет `Evidence`; используется в `SecurityHypothesis` (через `HypothesisObservation`) и в `FindingCandidate` (через `FindingObservation`).

### `Evidence` ✅ — Доказательство
Физический артефакт, подтверждающий `Observation` — файл в Object Storage (скриншот, сырой вывод сканера, HTTP-тело ответа). Хранит не сам файл, а ссылку (`storage_provider`, `storage_key`) + `sha256` для проверки целостности + `size_bytes`/`content_type`.
**Связи:** принадлежит `Observation`.

---

## Слой 3 — Анализ (от факта к гипотезе, от гипотезы к проверке)

### `SecurityHypothesis` ✅ — Гипотеза о проблеме
Предположение анализа: "возможно, здесь проблема", **ещё не подтверждённая уязвимость**. `category` — классификация (например, по OWASP, в коде уже заложен формат `A01:2025`), `confidence` — числовая уверенность (0.0–1.0), `status` (proposed/testing/validated/rejected).
**Связи:** принадлежит `Execution`; опирается на несколько `Observation` (через `HypothesisObservation`); порождает `ValidationPlan`.

### `HypothesisObservation` ✅ — связь Hypothesis↔Observation
Многие-ко-многим: одна гипотеза может опираться на несколько наблюдений, одно наблюдение — подтверждать несколько разных гипотез.

### `ValidationPlan` ✅ — План проверки
Структурированный план того, **как именно** будем проверять гипотезу: `objective` (цель проверки), `expected_secure_behavior`/`expected_insecure_behavior` (как выглядит "безопасно" и "небезопасно" по итогу), `success_criteria` (формальные критерии успеха, JSON), `constraints` (ограничения). Статус: proposed/approved/running/completed/rejected.

Важно по смыслу: это разделение "план" (что и как собираемся проверить) и "запуск" (следующая сущность, `ValidationRun`) — один и тот же план потенциально можно перезапустить, если первая попытка упала технически, не переосмысливая саму стратегию проверки заново.

**Связи:** принадлежит `SecurityHypothesis`; порождает `ValidationRun`.

### `ValidationRun` ✅ — Запуск проверки
Конкретная фактическая попытка выполнить `ValidationPlan`. Привязан к `Job` (та же Celery-механика, что и у Recon) и к `Execution`. Статус: queued/running/completed/failed.
**Связи:** принадлежит `ValidationPlan`; связан с `Execution` и опционально `Job`; порождает ровно один `ValidationResult`.

### `ValidationResult` ✅ — Результат проверки
Не просто "да/нет, подтвердилось", а подробная фиксация того, что произошло: `baseline` (что было до), `observed_state`/`observed_changes` (что получили), `data_exposure` (что потенциально раскрылось), `state_changed` (изменилось ли состояние системы — важно для контроля побочных эффектов), `success` + `confidence`.
**Связи:** принадлежит ровно одному `ValidationRun` (`unique=True` на `run_id`, то есть это связь один-к-одному, не один-ко-многим).

---

## Слой 4 — Находки (от технического кандидата к готовому отчёту для клиента)

### `FindingCandidate` ✅ — Кандидат в находку
Техническая, "сырая" находка, **в рамках одного `Execution`**, ещё не прошедшая финальное решение о включении в отчёт клиенту. `fingerprint` — для дедупликации похожих находок из разных прогонов. Статус: detected/validated/rejected/promoted. Может ссылаться на `SecurityHypothesis` (откуда возникла) и на `ValidationRun` (чем подтверждена) — опционально, потому что не каждый candidate обязательно прошёл полный путь гипотеза→проверка (некоторые находки могут быть обнаружены напрямую, без промежуточной гипотезы).
**Связи:** принадлежит `Execution`; опирается на `Observation` (через `FindingObservation`); опционально связан с `SecurityHypothesis` и `ValidationRun`; при "повышении" (`status = promoted`) превращается в `Finding`.

### `FindingObservation` ✅ — связь FindingCandidate↔Observation
Многие-ко-многим, та же логика, что `HypothesisObservation`.

### `Finding` ✅ — Находка (финальная, клиентская)
То, что реально видит заказчик как результат пентеста. Отличие от `FindingCandidate`: `Finding` привязан не к техническому `Execution`, а к бизнес-уровню — `Assessment` и `Target` напрямую. Содержит `severity` (info/low/medium/high/critical), `status` (open/resolved/accepted/false_positive), `remediation` (что исправить).

**Ключевая идея архитектуры, которую стоит прочувствовать:** `FindingCandidate` → `Finding` — это **намеренный барьер** между "сканер что-то нашёл" и "клиент это увидел". Не любой технический кандидат автоматически становится отчётной находкой — должен быть явный шаг "повышения" (promotion), который, скорее всего, будет либо человеческой проверкой (аналитик подтверждает), либо автоматическим правилом с высоким порогом уверенности. Без этого барьера в отчёт клиенту попадал бы шум и ложные срабатывания напрямую от сканера.

**Связи:** принадлежит `Assessment` и `Target`.

---

## Слой 5 — Отчётность

### `Report` ✅ — Отчёт
Финальный документ по `Assessment`. `report_type` (technical/executive/developer — разная подача одних и тех же находок для разных читателей), `storage_key` — ссылка на файл в Object Storage (сам PDF/HTML не хранится в Postgres).
**Связи:** принадлежит `Assessment`.

---

## Полная цепочка одной картинкой

```
Organization → Project → Target → TargetVerification
                   │
                   └──→ Assessment ←── AssessmentTarget ──→ Target
                            │
                            ├──→ Execution
                            │       │
                            │       ├──→ TargetSnapshot
                            │       │
                            │       ├──→ Job ──→ Observation ──→ Evidence
                            │       │
                            │       ├──→ SecurityHypothesis ←── (Observation)
                            │       │         │
                            │       │         └──→ ValidationPlan
                            │       │                   │
                            │       │                   └──→ ValidationRun ──→ ValidationResult
                            │       │
                            │       └──→ FindingCandidate ←── (Observation, Hypothesis, ValidationRun)
                            │                 │
                            │                 │ "promotion" — явный барьер
                            │                 ▼
                            ├──────────────→ Finding
                            │
                            └──→ Report
```

---

## Новые сущности, которых в коде нет вообще — дизайн + схемы

### `AuditLog` 🆕 — Журнал аудита

Зачем: раздел 17 плана требует обязательного аудита каждого действия Validation Service (кто, когда, что именно сделал против какой цели) — сейчас фиксировать это физически негде.

```python
# app/db/models/audit.py
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Пользователь, инициировавший действие.
    # None — для системных действий (например, автоматический Celery-воркер).
    user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Execution, в рамках которого произошло действие — для трассировки.
    execution_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("executions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Тип действия, например:
    # validation_run_started / validation_run_completed /
    # scope_approved / user_login / finding_promoted
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Полиморфная ссылка на сущность, к которой относится действие
    # (чтобы не заводить отдельную таблицу аудита под каждую модель).
    entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)

    # Дополнительные структурированные детали действия.
    # Названо "details", а не "metadata" — "metadata" зарезервировано
    # в SQLAlchemy declarative (Base.metadata), использовать как имя поля нельзя.
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
```

```python
# app/schemas/audit.py
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None
    execution_id: UUID | None
    action: str
    entity_type: str | None
    entity_id: UUID | None
    details: dict[str, Any] | None
    ip_address: str | None
    created_at: datetime
```

Намеренно нет `AuditLogCreate` — записи создаёт только сама система (сервисный код/middleware), не пользователь через API, поэтому отдельной "входной" схемы не нужно.

### `VulnerabilityRecord` 🆕 — Запись об уязвимости (CVE-кэш)

Зачем: без неё `ValidationPlan` для гипотезы "устаревший компонент" физически нечем проверять — нужен локальный кэш данных из NVD/CVE feed (раздел 11 плана), синхронизируемый периодически, не на каждый scan.

```python
# app/db/models/vulnerability.py
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VulnerabilityRecord(Base):
    __tablename__ = "vulnerability_records"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Идентификатор CVE, например "CVE-2024-12345".
    cve_id: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
        index=True,
    )

    # Нормализованное название затронутого продукта —
    # то, с чем будет сверяться результат banner grabbing.
    product: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # Диапазон затронутых версий.
    affected_versions: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # critical / high / medium / low
    severity: Mapped[str | None] = mapped_column(String(50), nullable=True)

    cvss_score: Mapped[float | None] = mapped_column(nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Когда запись синхронизирована из NVD (не дата публикации CVE).
    synced_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
```

```python
# app/schemas/vulnerability.py
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class VulnerabilityRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cve_id: str
    product: str
    affected_versions: dict[str, Any] | None
    severity: str | None
    cvss_score: float | None
    description: str | None
    synced_at: datetime
```

Тоже без `Create`-схемы по той же причине — заполняется периодическим Celery-таском синхронизации с NVD, не через пользовательский POST.
