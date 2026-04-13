# Roadmap: Budget Checker 2.0

## 1. Правило дорожной карты

Мы больше не работаем в режиме:

- "быстро что-то подкрутить";
- "потом переделаем";
- "сначала костыль, потом архитектура".

Теперь правило такое:

- каждая фаза имеет фиксированный scope;
- каждая фаза имеет критерии готовности;
- следующая фаза не начинается, пока не закрыта предыдущая.

## 2. Фаза 0. Зафиксировать продуктовый контракт

### Цель

Сделать так, чтобы у проекта был один источник правды.

### Что делаем

- утверждаем `docs/MASTER_TZ.md`;
- утверждаем `docs/SECURITY_BASELINE.md`;
- утверждаем этот roadmap;
- фиксируем, что старый код и старая логика не возвращаются.

### Deliverables

- главный master-TZ;
- security baseline;
- дорожная карта;
- новый README.

### Критерий готовности

- команда понимает, что строим;
- нет конкурирующих трактовок продукта.
- статус: завершено.

## 3. Фаза 1. Новый технический фундамент

### Цель

Создать чистый каркас приложения.

### Что делаем

- поднимаем новую структуру репозитория;
- создаём backend skeleton;
- создаём frontend skeleton;
- подключаем PostgreSQL;
- подключаем migrations;
- подключаем очередь фоновых задач;
- поднимаем минимальный `Celery` foundation с UTC и time limits;
- подключаем конфиг и secrets management;
- подключаем базовое логирование и error tracking;
- настраиваем автоматическую генерацию `openapi.json`;
- закладываем генерацию фронтовых типов из OpenAPI.

### Deliverables

- новый backend;
- новый frontend;
- новая схема конфигурации;
- локальный dev setup;
- базовая CI-проверка;
- доступный `openapi.json`;
- документированный контракт обновления API-типов.

### Критерий готовности

- приложение стартует;
- миграции работают;
- конфиг не зависит от старого проекта.

## 4. Фаза 2. Auth, роли и организации

### Цель

Собрать нормальную модель пользователей и кабинетов.

### Что делаем

- регистрация и вход;
- подтверждение email через отдельные токены в БД (`email_verification_tokens` с `used_at` и `expires_at`);
- resend verification с бизнес-лимитом через `resend_count` и `last_resent_at`;
- `me` endpoint с ролями пользователя;
- logout по refresh token и управление активными сессиями;
- роли;
- организации;
- члены организаций;
- merchant organization -> shop -> shop branch foundation;
- кабинет магазина;
- contractor profile foundation;
- кабинет подрядчика;
- foundation для `service_categories` / `service_items`;
- ручной CRUD для `contractor_service_offers` без import pipeline;
- кабинет админа;
- базовая модерация.

### Deliverables

- RBAC;
- user/org модели;
- auth API;
- email verification flow с явной инвалидацией старых токенов;
- public register без email enumeration;
- `me`, `sessions`, revoke specific session;
- foundation для `Shop` и `ShopBranch` с `verification_status` и `location_code`;
- foundation для `ContractorProfile` с отдельным `verification_status`;
- partner partial `PATCH` для merchant/contractor кабинетов;
- admin moderation endpoints с audit trail для `verification_status`;
- foundation для каталога услуг и contractor service offers с `currency`, `uom`, `valid_from`, `valid_to`;
- страницы кабинетов;
- журнал административных действий.

### Критерий готовности

- роли разделены;
- магазин не видит данные подрядчика;
- подрядчик не видит данные магазина;
- админ работает через audit trail.

## 5. Фаза 3. Материальный каталог V1

### Цель

Создать первую рабочую модель каталога материалов.

### Что делаем

- material categories;
- material items;
- manual merchant CRUD for `retail_offers`;
- `external_id` uniqueness in scope of `shop_branch_id`;
- `stock_status` как `in_stock / out_of_stock / on_order`, а не булевый флаг;
- aliases;
- attributes;
- retail offers import pipeline;
- snapshots цен и наличия;
- currency rates;
- import jobs;
- import job rows;
- import validation;
- ручной upload для партнёра.

### Deliverables

- material catalog schema;
- foundation для `material_categories`, `material_items` и merchant `retail_offers`;
- partner кабинет может вручную создать и обновить retail offer по `material_item_id`;
- import pipeline v1;
- CSV/XLSX/API ingestion;
- импорт-логи;
- статус качества данных;
- конвертация валют через `currency_rates`;
- ручной admin CRUD для `currency_rates` без внешних API-интеграций;
- `retail_offer_price_snapshots` в той же транзакции, что и import/manual update;
- правило уникальности `external_id` в рамках `shop_branch`.

### Критерий готовности

- магазин может загрузить каталог;
- офферы попадают в систему;
- история цен сохраняется;
- сырые и нормализованные сущности не смешиваются.

## 6. Фаза 4. Матчинг и compare материалов

### Цель

Сделать публично полезное сравнение материалов.

### Что делаем

- parsing input lines;
- normalization;
- candidate search;
- ranking;
- explainability;
- machine-readable `match_reason` и line-level `needs_review`;
- async-ready compare jobs (`POST /compare/materials` + polling `GET /compare/materials/{job_id}`);
- compare by city/location code;
- mixed-cart logic;
- result export;
- golden test set для матчинга.

### Deliverables

- compare API по материалам;
- `material_compare_jobs` со snapshot результата и TTL;
- estimate upload flow (`POST /estimates/upload`, polling `GET /estimates/{job_id}`, correction endpoint);
- `Next.js` UI проверки списка: `/` upload screen + `/estimates/[jobId]` polling/result screen;
- backend summary в `result_snapshot.summary`, чтобы фронт не пересчитывал суммы самостоятельно;
- public catalog search endpoints: `GET /api/v1/catalog/materials?search=...` и `GET /api/v1/catalog/services?search=...`;
- ручная корзина на лендинге использует тот же `POST /estimates/upload` flow, а не отдельный compare endpoint;
- ручное подтверждение спорных строк;
- итоговые расчёты;
- regression suite для матчинга на golden set.

### Критерий готовности

- пользователь может загрузить список;
- минимум по двум источникам получает реальные предложения;
- спорные матчи явно помечаются.

## 7. Фаза 5. Интеграции торговых сетей

### Цель

Довести хотя бы две торговые сети до стабильного качества.

### Приоритетные каналы

1. Прямой кабинет/фид.
2. API / structured feed.
3. Crawl как fallback.

### Что делаем

- фиксируем первые 2 приоритетные сети: `Епіцентр` + `Нова Лінія`;
- делаем для них отдельные ingestion adapters;
- для `Епіцентр` идём через structured feed / YML ingestion как основной канал;
- для `Нова Лінія` идём через partner API как второй адаптер;
- `Rozetka` и crawl-first источники остаются следующей волной после этих двух интеграций;
- делаем health/status dashboards;
- делаем retry/reprocessing;
- делаем data quality metrics.

### Deliverables

- 2 production-ready интеграции;
- метрики актуальности;
- логи ошибок;
- quality score источников.

### Критерий готовности

- данные обновляются стабильно;
- цена, наличие и ссылка проходят валидацию;
- обновления не зависят от ручного шаманства.

## 8. Фаза 6. Каталог услуг и compare работ

### Цель

Добавить вторую половину продукта — сравнение работ.

### Что делаем

- service categories;
- service items;
- contractor service offers;
- импорт прайс-листов;
- compare по услугам;
- региональная логика;
- диапазоны рынка.

### Deliverables

- service catalog;
- contractor price import;
- compare API по работам;
- UI сравнения услуг.

### Критерий готовности

- подрядчик может загрузить прайс;
- пользователь видит сравнение по работам;
- система считает отклонение от рынка.

## 9. Фаза 7. Полная админка и операционный контур

### Цель

Дать команде нормальный контроль над платформой.

### Что делаем

- moderation queues;
- manual reviews;
- source health dashboards;
- import monitoring;
- security event review;
- partner verification;
- incident tools.

### Deliverables

- админ-панель без legacy мусора;
- инструменты модерации;
- quality dashboards;
- action audit.

### Критерий готовности

- админ управляет качеством системы;
- важные процессы не скрыты в логах;
- ручное вмешательство прозрачно и безопасно.

## 10. Фаза 8. Отчёты, лиды и коммерческий контур

### Цель

Подключить бизнес-ценность для партнёров.

### Что делаем

- переходы на магазины;
- переходы к подрядчикам;
- лид-метки;
- отчёты по спросу;
- аналитика по позициям и регионам.

### Deliverables

- базовая партнёрская аналитика;
- трекинг кликов/переходов;
- первые monetization hooks.

### Критерий готовности

- магазины и подрядчики получают понятную ценность от участия.

## 11. Фаза 9. Production hardening

### Цель

Подготовить систему к реальной нагрузке и эксплуатации.

### Что делаем

- performance profiling;
- rate limiting hardening;
- backup/restore;
- alerting;
- abuse protection;
- incident response runbooks;
- compliance checks.

### Deliverables

- резервные копии;
- мониторинг;
- алерты;
- runbooks;
- security hardening.

### Критерий готовности

- система выдерживает нормальную эксплуатацию;
- команда понимает, как реагировать на сбои.

## 12. Порядок реализации модулей

Строгий порядок:

1. Документы и правила.
2. Технический фундамент.
3. Auth и роли.
4. Материальный каталог.
5. Compare материалов.
6. Интеграции сетей.
7. Каталог услуг.
8. Compare работ.
9. Админка.
10. Аналитика и production hardening.

## 13. Что нельзя делать в процессе

Нельзя:

- снова разворачивать продукт вокруг маленького reference-набора;
- подключать кучу нестабильных источников раньше, чем готовы качественные 2 источника;
- строить кабинеты без RBAC;
- делать upload файлов без security baseline;
- делать compare без explainability;
- возвращать старый хаос в новую архитектуру.

## 14. Definition of Done для каждой фазы

Фаза считается завершённой только если:

- есть код;
- есть документация;
- есть миграции;
- есть тесты;
- есть метрики / логи для контроля;
- есть критерии ручной приёмки;
- нет незакрытых критичных дыр по безопасности.
