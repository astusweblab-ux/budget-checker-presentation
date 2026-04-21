# Real Completion Checklist

Цей документ фіксує різницю між **технічно зібраним продуктом** і **реально завершеним комерційним запуском**.

Актуально на: **21 квітня 2026**.

## Поточний висновок

Кодова база Budget Checker 2.0 готова до першого комерційного пілоту: основний сценарій перевірки кошторису, кабінети, адмінка, локалізація, legal, billing foundation, security hardening, алерти та SEO foundation вже реалізовані.

Проект ще не можна вважати повністю завершеним у комерційному сенсі, доки не закриті зовнішні production-залежності:

- реальні feed/API джерела для Epicentr і Nova Liniya;
- production-ключі LiqPay і реальний платіжний smoke;
- production-ключі Cloudflare Turnstile;
- перший реальний партнер з бойовим імпортом каталогу;
- production-інфраструктура, backup/restore і фінальний deploy з smoke-перевіркою.

## Definition of Real Completion

Проект вважається реально завершеним, коли виконані всі пункти нижче:

1. Крайня гілка з поточними змінами злита в `main`, задеплоєна і перевірена на `https://budcheck.com.ua`.
2. Production frontend працює через `next build` + `next start`, без `next dev` і `webpack-hmr`.
3. Backend працює з production PostgreSQL, Redis/Celery, SMTP, storage і актуальними secrets.
4. Epicentr і Nova Liniya мають реальні джерела даних, регулярний sync і здоровий integration health.
5. LiqPay працює у production-режимі, webhook приймається, тариф користувача оновлюється після реальної оплати.
6. Cloudflare Turnstile увімкнений на login/register і дає очікувані security events при збої.
7. Принаймні один реальний магазин пройшов onboarding, verification, імпорт каталогу і дав реальні пропозиції в результатах кошторису.
8. Публічні сторінки, legal, sitemap/hreflang, robots, кабінети, admin, checkout, estimate flow і service flow пройшли production smoke.
9. Monitoring, Discord alerts, readiness checks, backups і incident runbooks перевірені в production-like режимі.
10. Перший комерційний пілот має зафіксовані результати: користувацький сценарій, partner clicks/leads, якість даних і список наступних business-рішень.

## 1. Merge, Release, Deploy

- Перевести PR з draft у ready state після фінального review.
- Перевірити, що GitHub checks зелені.
- Злити PR у `main`.
- На сервері підтягнути `main`.
- Прогнати міграції Alembic.
- Зібрати frontend:

```bash
npm ci --prefix frontend
npm run build --prefix frontend
```

- Перезапустити backend, frontend, Celery worker/beat і monitoring tasks.
- Перевірити, що `GET /api/v1/health/ready` повертає `status=ok`.

## 2. Production Environment

Обов'язково налаштувати і перевірити:

- `BC_APP_ENV=production`;
- `BC_DEBUG=false`;
- `BC_APP_BASE_URL=https://budcheck.com.ua`;
- новий `BC_SECRET_KEY`;
- `BC_TRUSTED_HOSTS` і `BC_PROXY_TRUSTED_HOSTS`;
- production `DATABASE_URL`, `BC_ASYNC_DATABASE_URL`, `BC_SYNC_DATABASE_URL`;
- production `REDIS_URL` / `BC_REDIS_URL`;
- Celery worker + beat без eager mode;
- SMTP з доменною адресою `support@budcheck.com.ua`;
- S3-compatible storage або інший production storage з backup;
- `SENTRY_DSN` або погоджена альтернатива error tracking;
- `BACKUP_SCHEDULE`;
- Discord webhook-и: startup, status, warning, critical, security;
- `BC_API_DOCS_ENABLED=false` або доступ до docs тільки з loopback.

## 3. Security Gate

- Увімкнути Cloudflare Turnstile:
  - `BC_CF_TURNSTILE_ENABLED=true`;
  - production site key у frontend env;
  - production secret key у backend env.
- Перевірити login/register з валідним Turnstile token.
- Перевірити негативний кейс Turnstile і появу `auth.turnstile_failed` у security events.
- Перевірити 2FA для `ops_admin` / `super_admin`.
- Перевірити rate limits на login/register/estimate/compare.
- Перевірити, що `/docs`, `/redoc`, `/openapi.json` не відкриті публічно.
- Перевірити sensitive probe alerts.
- Перевірити, що `POST /` з `Next-Action: x` блокується `404` і не створює Discord noise за замовчуванням.

## 4. LiqPay Production

- Пройти LiqPay merchant verification.
- Отримати production public/private keys.
- Встановити:
  - `BC_LIQPAY_PUBLIC_KEY`;
  - `BC_LIQPAY_PRIVATE_KEY`;
  - `BC_LIQPAY_SANDBOX=false`;
  - за потреби `BC_LIQPAY_SERVER_URL`;
  - за потреби `BC_LIQPAY_RESULT_URL`.
- Перевірити, що webhook URL доступний зовні:
  - `https://budcheck.com.ua/api/v1/billing/liqpay/webhook`.
- Провести малий реальний платіж.
- Перевірити:
  - створення `BillingOrder`;
  - запис `BillingWebhookEvent`;
  - валідну signature;
  - оновлення billing status у `/dashboard/account`;
  - redirect `?payment=success`;
  - сценарій failed/cancelled payment.
- Описати refund/chargeback операційний процес у legal/runbook, якщо правила зміняться після LiqPay verification.

## 5. Epicentr + Nova Liniya Production Data

Для Epicentr:

- Отримати реальний YML/XML feed або інший structured feed.
- Створити або вибрати реальний магазин/філію в адмінці.
- Додати `feed_url` у `BranchIntegrationConfig`.
- Запустити ручний sync.
- Перевірити import job rows, помилки, suspicious flags, ціну, наявність, URL.
- Увімкнути регулярний sync.

Для Nova Liniya:

- Отримати real partner API URL/credentials або погоджений JSON endpoint.
- Додати `api_url` у `BranchIntegrationConfig`.
- Запустити ручний sync.
- Перевірити mapping полів, external_id, stock, price, URL.
- Увімкнути регулярний sync.

Для обох джерел:

- Integration health має перейти у `healthy`.
- `last_synced_at` і `next_sync_due_at` мають оновлюватися.
- Failed job має коректно перезапускатися через admin reprocess.
- У результаті перевірки кошторису мають з'являтися реальні пропозиції з цих джерел.
- Дані мають пройти мінімальний QA: валюта, одиниці виміру, дублікати, занадто низькі/високі ціни, биті посилання.

## 6. First Real Partner Pilot

- Онбордити перший реальний магазин.
- Створити organization, shop, branch.
- Провести admin verification.
- Завантажити або синхронізувати реальний каталог.
- Перевірити partner dashboard і analytics.
- Перевірити click tracking з результатів кошторису.
- Узгодити комерційний сценарій:
  - підписка;
  - pay-per-lead;
  - trial period;
  - ручний invoice, якщо LiqPay ще не використовується для B2B.
- Зафіксувати перші бізнес-метрики: кількість імпортованих позицій, matched rate, clicks/leads, проблемні категорії.

## 7. Production Smoke

Публічна частина:

- `/uk`, `/ru`, `/en`;
- `/check-estimate`;
- `/services`;
- `/for-stores`;
- `/for-contractors`;
- `/pricing`;
- legal pages у трьох мовах;
- `sitemap.xml`;
- `robots.txt`;
- OpenGraph preview.

Користувацькі сценарії:

- register + email verification;
- login/logout/refresh token;
- password/profile/security page;
- anonymous estimate limit;
- authorized estimate history;
- mixed estimate: materials + labor;
- correction of `needs_review` line;
- service compare;
- checkout + account billing status.

Партнерські сценарії:

- merchant onboarding;
- contractor onboarding;
- manual catalog import;
- integration config;
- sync trigger;
- import reprocess;
- partner analytics.

Admin:

- moderation queue;
- shops/contractors verification;
- imports;
- integrations health;
- audit events;
- security events;
- operations hub.

Mobile/PWA:

- header/drawer/logo;
- installability;
- status bar/theme color;
- service worker cache behavior after deploy.

## 8. SEO And Indexing

- Перевірити production `sitemap.xml` з `/uk`, `/ru`, `/en`, `hreflang`, `x-default`.
- Перевірити canonical URL на публічних сторінках.
- Перевірити `robots.txt`, щоб приватні маршрути були закриті.
- Надіслати sitemap у Google Search Console.
- Запустити URL inspection для головної, `/uk`, `/ru`, `/en`, `/pricing`, `/check-estimate`.
- Перевірити, що legacy domain redirect працює через 301.

## 9. Backup, Restore, Monitoring

- Налаштувати backup DB за `BACKUP_SCHEDULE`.
- Провести restore drill на окрему базу або staging.
- Перевірити storage backup.
- Зареєструвати readiness monitor у Task Scheduler.
- Зареєструвати server status monitor.
- Перевірити Discord startup/status/warning/critical/security канали.
- Перевірити incident runbooks:
  - `INCIDENT_DB_DEGRADED.md`;
  - `INCIDENT_IMPORT_FAILURE.md`;
  - `INCIDENT_TOKEN_COMPROMISE.md`.

## 10. Post-Launch Acceptance

Перші 7 днів після production launch:

- щодня перевіряти readiness, error rate, security events, failed imports;
- щодня перевіряти matched rate по реальних кошторисах;
- збирати feedback першого партнера;
- фіксувати рядки, які користувачі виправляють вручну;
- перевіряти LiqPay orders і webhook events;
- перевіряти SEO indexing status;
- оновити `docs/IMPLEMENTATION_STATUS.md` після завершення пілотного тижня.

## Не входить у V1 real completion

Ці пункти не блокують перший реальний запуск:

- повна геомодель КАТОТТГ;
- Rozetka і crawl-first джерела;
- LLM-assisted parsing;
- A/B testing ranking algorithms;
- глибока регіональна аналітика;
- окремі мікросервіси.
