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
- живой технический статус фиксируется в `docs/IMPLEMENTATION_STATUS.md`;
- инвесторский статус фиксируется в `docs/PROJECT_PRESENTATION.html`.
- реальное commercial completion фиксируется отдельно в `docs/REAL_COMPLETION_CHECKLIST.md`, потому что часть фаз зависит не от кода, а от внешних production-доступов, ключей и партнёров.

## 2. Фаза 0. Зафиксировать продуктовый контракт ✅ завершена

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

## 3. Фаза 1. Новый технический фундамент ✅ завершена

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

## 4. Фаза 2. Auth, роли и организации ✅ завершена

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

## 5. Фаза 3. Материальный каталог V1 ✅ завершена

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

## 6. Фаза 4. Матчинг и compare материалов ✅ завершена (baseline)

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

## 7. Фаза 5. Интеграции торговых сетей 🔄 code-ready / data-pending

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

- адаптеры для 2 production-кандидатов;
- реальные production-ready интеграции после получения feed/API доступов;
- метрики актуальности;
- логи ошибок;
- quality score источников.

### Критерий готовности

- code-ready критерий уже закрыт: адаптеры, конфиги, sync foundation, health statuses, reprocess и тесты есть;
- commercial-ready критерий ещё открыт: нужны реальные feed/API источники Epicentr + Nova Liniya;
- данные обновляются стабильно;
- цена, наличие и ссылка проходят валидацию;
- обновления не зависят от ручного шаманства.

### Осталось до закрытия фазы

- получить реальный Epicentr YML/XML feed;
- получить реальный Nova Liniya partner API / JSON endpoint;
- настроить production `feed_url` / `api_url` в `BranchIntegrationConfig`;
- провести первый production sync;
- довести оба источника до `healthy`;
- подтвердить, что реальные предложения появляются в пользовательском результате кошториса.

## 8. Фаза 6. Каталог услуг и compare работ ✅ завершена

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

### Что уже есть сейчас

- foundation для `service compare API` уже собран:
  - `POST /api/v1/compare/services`;
  - `GET /api/v1/compare/services/{job_id}`;
- добавлен `ServiceCompareJob`;
- реализован `ServiceMatchEngine` с тем же explainability-паттерном, что и у материалов;
- добавлена фильтрация по `region_code` и `contractor_profile_ids`;
- подрядчик уже может загрузить прайс работ через CSV/XLSX import endpoint:
  - `POST /api/v1/organizations/{organization_id}/contractor-service-offers/import`;
- на фронте уже есть отдельный contractor import screen с in-memory login и разбором ошибок по строкам;
- на фронте уже есть публичный UI compare работ:
  - `/services`;
  - `/services/{job_id}`;
- contractor service offers уже получают market/anomaly flags:
  - absolute low/high price checks;
  - deviation from market median по похожим услугам;
  - non-UAH prices явно помечаются как риск для compare totals;
- suspicious flags уже видны и в contractor import UI, и в public compare result по услугам;
- dev seed теперь поднимает demo contractor account и demo contractor organization для ручного тестирования;
- **смешанные сметы**: `POST /api/v1/estimates/upload` теперь матчит строки сразу на материалы и работы:
  - `classifier.py` — keyword-based классификатор строк (монтаж, укладка, штукатурка и др.);
  - `line_type` сохраняется на каждой строке (`"material"` / `"service"`);
  - result screen разделён на две секции: «Материалы» и «Работы»;
  - snapshot считает `material_lines_count` и `service_lines_count`;
- покрыто интеграционными тестами.

### Deliverables

- service catalog;
- contractor price import;
- compare API по работам;
- UI сравнения услуг.

### Критерий готовности

- подрядчик может загрузить прайс;
- пользователь видит сравнение по работам;
- система считает отклонение от рынка.

## 9. Фаза 7. Полная админка и операционный контур ✅ завершена

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

### Что уже есть

- `GET /admin/moderation-queue` — очередь на верификацию: все pending shops + contractor profiles в одном запросе, сортировка по дате создания;
- `GET /admin/import-jobs?status=failed&offset=N` — список последних N import jobs по всем магазинам с фильтром по статусу и offset-пагинацией;
- `GET /admin/audit-events?target_type=shop&offset=N` — лента security/audit событий с фильтром по типу цели и пагинацией;
- `GET /admin/security-events?event_type=auth.login_failed&offset=N` — security event review с фильтром по типу события и пагинацией;
- `PATCH /admin/shops/{id}/verification` + `PATCH /admin/contractor-profiles/{id}/verification` — ручная верификация партнёров с записью в audit;
- `POST /admin/moderation-queue/{item_type}/{item_id}/action` — одна кнопка verify/suspend прямо из очереди, с записью в audit;
- `POST /admin/import-jobs/{job_id}/reprocess` — перезапуск failed integration import job;
- `AuditEvent` модель + `write_audit_event()` — каждое ручное действие в админке фиксируется;
- `SecurityEvent` модель + запись событий из `auth/service.py` — неуспешные логины и blocked login теперь не прячутся в исключениях, а попадают в отдельную ленту;
- import quality summary — `GET /admin/import-quality-summary` с integration health counts и recent_problem_jobs;
- frontend screen `/dashboard/admin/operations` — один ops-экран с polling, фильтрами по типу/статусу и prev/next пагинацией по всем четырём секциям;
- shop branches integration configs management — `GET/PUT /admin/shop-branches/{id}/integrations/{type}`;
- currency rates management — `GET/POST /admin/currency-rates`.

### Deliverables

- админ-панель без legacy мусора;
- инструменты модерации;
- quality dashboards;
- action audit.

### Критерий готовности

- админ управляет качеством системы;
- важные процессы не скрыты в логах;
- ручное вмешательство прозрачно и безопасно.

## 10. Фаза 8. Отчёты, лиды и коммерческий контур ✅ завершена (foundation)

### Цель

Подключить бизнес-ценность для партнёров.

### Что сделали (foundation scope)

- переходы на магазины;
- переходы к подрядчикам;
- лид-метки;
- отчёты по спросу;
- базовая партнёрская аналитика и dashboard.

### Что уже есть

- `POST /api/v1/compare/track-click` — запись клика на оффер (offer_id, offer_type, session_token/user_id, estimate_job_id, compare_job_id);
- `GET /api/v1/partner/{organization_id}/analytics` — аналитика для merchant/contractor: total_clicks, top-5 офферов по кликам за период;
- `GET /api/v1/partner/{organization_id}/analytics` теперь также возвращает `top_leads` (lead-метки по `estimate_job_id`/`compare_job_id`);
- `GET /api/v1/partner/{organization_id}/analytics/demand` — top material/service запросов из `estimate_lines` и compare jobs за период;
- frontend page `/dashboard/partner/[organizationId]/analytics` — partner dashboard с total_clicks, top_offers и demand report;
- маршрут добавлен в `dev-nav-bar` и `GET /api/v1/dev/routes`;
- кнопка «Перейти в магазин» в estimate result: вызывает track-click и открывает URL магазина;
- кнопка «Связаться с подрядчиком» в estimate result и service compare result: вызывает track-click;
- покрыто 10 тестами для Phase 8; полный backend test suite зелёный.

### Deliverables

- базовая партнёрская аналитика;
- трекинг кликов/переходов;
- отчёты по спросу;
- partner dashboard.

### Критерий готовности

- магазины и подрядчики получают понятную ценность от участия.

### DECISIONS_PENDING — Phase 8 extension

- региональная аналитика (по городам/регионам);
- monetization hooks (платные сценарии);
- drill-down UI для лидов.

## 11. Фаза 9. Production hardening ✅ завершена

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

### Что уже есть

- подключен `slowapi` foundation:
  - `POST /api/v1/estimates/upload` — `10/hour` на session/user;
  - `POST /api/v1/compare/materials` — `30/hour` на session/user;
  - `POST /api/v1/compare/services` — `30/hour` на session/user;
  - `POST /api/v1/auth/token` — `20/hour` на IP;
- расширен readiness probe `GET /api/v1/health/ready`:
  - проверяет DB connection (`SELECT 1`);
  - возвращает `status=ok` или `status=degraded` + `details`;
- добавлены incident runbooks:
  - `docs/runbooks/INCIDENT_TOKEN_COMPROMISE.md`;
  - `docs/runbooks/INCIDENT_IMPORT_FAILURE.md`;
  - `docs/runbooks/INCIDENT_DB_DEGRADED.md`;
- обновлён `.env.example` для production baseline:
  - добавлены `DATABASE_URL`, `REDIS_URL`, `SENTRY_DSN`;
  - добавлено напоминание о ротации `SECRET_KEY`;
  - добавлен блок `# Production checklist` (`BACKUP_SCHEDULE`, `ALERT_WEBHOOK_URL`, `MAX_UPLOAD_SIZE_MB`).

### Deliverables

- резервные копии;
- мониторинг;
- алерты;
- runbooks;
- security hardening.

### Критерий готовности

- система выдерживает нормальную эксплуатацию;
- команда понимает, как реагировать на сбои.

## 12. Після фаз 0–9 (реалізовано додатково, 2026-04-17) ✅

Наступні блоки реалізовані понад scope фаз 0–9:

### Публічний IA та landing

- сторінка `/` — лендінг з hero-секцією, CTA, поясненням продукту;
- `/for-stores` — landing для магазинів;
- `/for-contractors` — landing для підрядників;
- `/login` — вхід з JWT-авторизацією;
- `/register` — реєстрація з обов'язковим підтвердженням email і LegalConsent чекбоксами;
- `/verify-email?token=` — автоматичне підтвердження email по токену;
- `/check-estimate` — публічна сторінка перевірки кошторису (alias від `/`).

### Тарифні плани (/pricing)

- публічна сторінка `/pricing` з трьома секціями (Merchant / Contractor / Individual);
- toggle місяць/рік;
- FAQ-блок;
- CTA з кнопкою переходу в `/checkout`.

### Юридичні документи

- legal content лежить у `frontend/content/legal/` і має версії `uk` / `ru` / `en`: `user-agreement`, `privacy-policy`, `business-rules`;
- рендер на окремих сторінках `/legal/user-agreement`, `/legal/privacy-policy`, `/legal/business-rules` з підтримкою мовних URL `/uk`, `/ru`, `/en`;
- при реєстрації — обов'язкові чекбокси: базова угода + окремий для merchant/contractor;
- backend фіксує факт прийняття в `legal_consents` (IP, user_agent, версія документа, дата).

### LiqPay білінг (sandbox протестовано)

- `backend/app/billing/`: `BillingOrder`, `BillingWebhookEvent`, checkout service, webhook validation;
- `POST /api/v1/billing/liqpay/checkout` — генерація підписаного payload LiqPay;
- `POST /api/v1/billing/liqpay/webhook` — обробка webhook з валідацією signature;
- `GET /api/v1/billing/status` — поточний план користувача;
- `GET /api/v1/billing/my-orders` — остання 20 замовлень;
- фронтова сторінка `/checkout` формує і відправляє payload;
- після оплати — redirect до кабінету з банером успіху (`?payment=success`);
- секція «Тарифний план» у `/dashboard/account` з кольоровими статусами.

### Кабінети користувачів

- `/dashboard/account` — профіль для користувачів без організації (email, статус, тарифний план, DeleteAccountSection);
- `/dashboard/merchant` — кабінет мерчанта: дані організації, магазин, import stats, checklist, DeleteAccountSection;
- `/dashboard/contractor` — кабінет підрядника: аналогічно merchant;
- role-routing: після реєстрації merchant/contractor одразу потрапляють у правильний кабінет.

### Soft-delete акаунту

- `DELETE /api/v1/auth/me` — soft-delete: відзив всіх refresh-токенів, `is_active=False`, анонімізація email, очищення password_hash;
- `DeleteAccountSection` компонент у merchant/contractor кабінетах.

### Автооновлення JWT токена

- `isTokenExpired(token)` — парсинг JWT exp без бібліотек;
- при відновленні сесії з localStorage — автоматичний refresh якщо токен прострочений;
- при невалідному Bearer в estimates — тихий fallback до анонімного режиму.

### Ліміт 3 безкоштовні перевірки для незареєстрованих

- `EstimatesService.upload_estimate()` — місячний ліміт для anonymous session (session_token + user_id IS NULL);
- налаштовується через `BC_ANONYMOUS_ESTIMATE_CHECKS_PER_MONTH` (default 3);
- при перевищенні — HTTP 429 з поясненням.

### Локалізація uk/ru/en

- всі сторінки: лендінги, результати перевірки, кабінети, адмін-панель (усі 7 розділів), публічні сторінки, legal, футер;
- `locale-provider.tsx` — 100+ i18n-ключів, збереження мови між сесіями (localStorage);
- `admin-menu.tsx`, всі admin pages — усі тексти через `t()`.
- мовні URL `/uk`, `/ru`, `/en` працюють через middleware rewrite і зберігаються в header/footer/redirect-ах;
- backend API локалізує JSON-помилки по `Accept-Language`, email verification має `preferred_locale`;
- SEO metadata, sitemap і `hreflang` генеруються окремо для `uk`, `ru`, `en`.

### PWA (Progressive Web App)

- `public/manifest.json` — Web App Manifest з іконками 72–512px, shortcut на `/check-estimate`, versioned icon URLs для cache busting;
- `public/sw.js` — service worker `budcheck-v4`: network-first для `/api/v1/*`, navigation і `/_next/image`, cache-first для решти статики, офлайн-fallback;
- `app/layout.tsx` — реєстрація SW через `next/script afterInteractive`;
- `next.config.ts` — `Cache-Control: no-cache` для `sw.js`;
- `public/icons/` — 8 PNG-іконок з логотипу, favicon/apple-touch assets оновлені й версіоновані;
- встановлюється як нативний застосунок на Android та iOS.

### Мобільна оптимізація

- `app-header.tsx` — hamburger-кнопка (`md:hidden`), мобільний drawer з навігацією, language-switcher, auth-кнопками;
- `app-footer.tsx` — `flex-col → md:flex-row`, `grid-cols-2` для колонок;
- мінімальна висота touch-елементів 44px на всіх CTA;
- `font-size ≥ 16px` на всіх inputs (iOS no-zoom);
- адаптивні grid-layouts.

### Email

- `BC_EMAIL_FROM_ADDRESS` / `BC_EMAIL_REPLY_TO` — конфігурований From і Reply-To;
- `SMTPEmailSender` — `_apply_headers()` встановлює From, To і Reply-To (якщо задано) на всі листи;
- full email flow: send_verification з `{base_url}/verify-email?token=`, send_organization_invite.

### Nginx + deployment

- nginx конфіг: `location /api/` → backend (port 8000), `location /` → Next.js (port 3000);
- Next.js `rewrites()` — dev-режим проксирує `/api/` на `http://127.0.0.1:8000`;
- `BC_DEV_RESET_DB=false` — база зберігається між перезапусками.
- Канонічний домен — `https://budcheck.com.ua`; `www` не використовується.
- Legacy `budcheck.pp.ua` має віддавати тільки 301 redirect на `https://budcheck.com.ua$request_uri`.

## 13. Порядок реализации модулей

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
- нет незакрытых критичных дыр по безопасности;
- обновлён прогресс в PROJECT_PRESENTATION.html.
