# Security Baseline: Budget Checker 2.0

## 1. Принцип

Безопасность не добавляется в конце.
Она является частью архитектуры и требований к каждому модулю.

## 2. Основные угрозы

Для нашего продукта критичны:

- кража аккаунтов;
- доступ к чужим кабинетам;
- подмена цен и каталогов;
- загрузка вредоносных файлов;
- SSRF через внешние URL и импорты;
- CSV/XLSX/XML injection;
- IDOR;
- злоупотребление admin endpoint;
- утечка секретов;
- небезопасные фоновые задачи;
- poisoning данных через фальшивые прайсы;
- фрод со стороны невалидных поставщиков или подрядчиков.

## 3. Базовая модель доступа

Роли:

- `guest`
- `customer`
- `merchant_member`
- `merchant_admin`
- `contractor_member`
- `contractor_admin`
- `support_admin`
- `ops_admin`
- `super_admin`

Принципы:

- least privilege;
- deny by default;
- action audit на чувствительные действия;
- строгая проверка organization boundary.

## 4. Аутентификация

Обязательно:

- безопасное хеширование паролей (`Argon2id` или `bcrypt` с актуальными параметрами);
- email verification;
- `register` не должен раскрывать, существует ли email в системе;
- повторная отправка verification email ограничивается на уровне БД и бизнес-логики, а не только внешнего rate limiting;
- optional 2FA для админов и партнёров;
- session rotation;
- refresh-token rotation;
- device/session management;
- ограничение количества неудачных логинов;
- rate limiting по session/token bucket с IP как вторичным сигналом;
- анонимные compare/estimate session tokens должны храниться в `httpOnly cookie`, а не в `localStorage`;
- CAPTCHA/anti-bot только где реально нужно.

Нельзя:

- хранить пароли или токены в открытом виде;
- использовать статические admin secrets как основной механизм доступа;
- смешивать user session и service integration token.

### Статус реалізації (2026-04-20)

Реалізовано:

- **Email verification** — повний flow: SMTP (`smtp.gmail.com:587`, STARTTLS), лист з клікабельним посиланням `{BC_APP_BASE_URL}/verify-email?token=...`, фронтенд-сторінка `/verify-email` автоматично підтверджує токен.
- **`BC_APP_BASE_URL`** — обов'язкова змінна оточення для production; використовується при формуванні посилань в листах.
- **From / Reply-To** — `BC_EMAIL_FROM_ADDRESS` налаштовує From (напр. `Budget Checker <support@budcheck.com.ua>`); `BC_EMAIL_REPLY_TO` — необов'язковий Reply-To для маршрутизації відповідей.
- **Rate limiting** — `slowapi` на критичних ендпоїнтах: `POST /estimates/upload` (10/год на сесію), `POST /compare/materials` і `POST /compare/services` (30/год), `POST /auth/token` (20/год на IP).
- **Rate limiting (розширено)** — додаткові ліміти на `POST /auth/register`, `POST /auth/2fa/confirm-login`, `POST /auth/verify-email`, `POST /auth/resend-verification`, `POST /auth/refresh`, `GET /locations/suggest/*`, `POST /compare/track-click`.
- **LegalConsent** — при реєстрації фіксується факт прийняття кожного документа в таблиці `legal_consents` з IP-адресою, user_agent, версією документа та timestamp.
- **Soft-delete акаунту** — `DELETE /api/v1/auth/me`: відзив всіх refresh-токенів, `is_active=False`, анонімізація email, очищення password_hash.
- **Security events stream + Discord alerts** — `SecurityEvent` модель: невдалі логіни, blocked login, failed 2FA, invalid refresh token і Turnstile failures записуються окремо (не тільки в логи), доступні в адмін через `GET /admin/security-events` і відправляються в `ALERT_WEBHOOK_URL_SECURITY` з fallback на critical/warning webhook.
- **Sensitive probe alerts** — backend відправляє `http.sensitive_path_probe` для спроб доступу до службових шляхів (`/api/.env`, `.git`, `.ssh`, `wp-config.php`, `actuator`), навіть якщо запит не входить у `/api/v1`.
- **Frontend Server Action probe hardening** — Next.js middleware блокує підозрілі `Next-Action` запити `404`. Discord alert для таких probe-запитів вимкнений за замовчуванням, щоб фонові scanner-запити не створювали шум; для діагностики вмикається через `BC_ALERT_SERVER_ACTION_PROBES=true`.
- **Російський каталог Discord alert texts** — формулювання для каналів, рівнів, security events, причин і HTTP-статусів зберігаються в `backend/core/alert_messages.py`; нові алерти додаються через цей каталог. Discord-сповіщення не залежать від URL locale або `Accept-Language` і завжди формуються російською.
- **Audit log** — `AuditEvent` + `write_audit_event()`: кожна ручна дія в адмінці (верифікація, блокування, перезапуск імпорту) фіксується з actor_id, target_id, timestamp.
- **Email DNS для `budcheck.com.ua`** — SPF `v=spf1 include:_spf.mx.cloudflare.net ~all`, DKIM `cf2024-1._domainkey` і DMARC `p=quarantine` налаштовані; mail-tester підтвердив score 10/10.
- **Анонімний ліміт** — `BC_ANONYMOUS_ESTIMATE_CHECKS_PER_MONTH` (default 3): анонімні сесії обмежені місячним лімітом безкоштовних перевірок.
- **Readiness probe** — `GET /api/v1/health/ready` перевіряє DB connection (`SELECT 1`), повертає `status=ok` або `status=degraded`.
- **Cloudflare Turnstile** — захист від ботів на формах логіну і реєстрації; вимкнено до додавання production-ключів (`CF_TURNSTILE_ENABLED=true`).
- **2FA (TOTP) для ops_admin і super_admin** — setup через QR-код, підтвердження при кожному логіні.
- **Блокування після 5 невдалих спроб входу** — lockout на 15 хвилин (`failed_login_attempts`, `locked_until`).
- **Trusted hosts + proxy chain trust** — бекенд приймає лише дозволені `Host` (`BC_TRUSTED_HOSTS`) і довіряє `X-Forwarded-*` лише від trusted proxy (`BC_PROXY_TRUSTED_HOSTS`), щоб rate limiting та audit IP працювали коректно.
- **Docs hardening** — `/docs`, `/redoc`, `/openapi.json` за замовчуванням вимкнені в production (`BC_API_DOCS_ENABLED`), а на edge-рівні `/docs` і `/openapi.json` додатково обмежені loopback-доступом.
- **Nginx anti-DDoS baseline** — `limit_req` + `limit_conn` + жорсткіші timeout-и, окремо посилені ліміти для auth endpoints.
- **Політика повернень** — зафіксована в юридичних документах (`user-agreement.md`, `business-rules.md`).

Ще не реалізовано (roadmap):

- device/session management UI.

## 5. Авторизация

Каждый запрос должен проверять:

- кто пользователь;
- к какой организации он относится;
- имеет ли он право на действие;
- имеет ли право на объект.

Обязательные проверки:

- merchant не видит чужие import jobs;
- contractor не видит чужие service offers;
- customer не видит внутренние admin данные;
- support admin не может делать destructive ops без расширенного права;
- super admin действия логируются отдельно.

## 6. Загрузка файлов

Все пользовательские и партнёрские файлы опасны по умолчанию.

Обязательные меры:

- allowlist форматов;
- limit по размеру;
- limit по количеству файлов;
- нормализация имени файла;
- хранение вне web root;
- MIME + content sniff validation;
- антивирусная или sandbox-проверка, если внедрим позже;
- отдельный pipeline text extraction;
- запрет исполнения файлов;
- удаление метаданных, где нужно;
- генерация internal storage key.

Особое внимание:

- `xlsx`, `csv`, `xml`, `docx`, `pdf` должны обрабатываться безопасными библиотеками;
- XML parser только с отключёнными внешними сущностями;
- CSV formula injection должна экранироваться на export.

## 7. Интеграции магазинов и подрядчиков

При загрузке catalog/feed/API данных обязательно:

- проверять организацию-источник;
- привязывать импорт к конкретному integration key;
- хранить audit trail;
- валидировать schema;
- валидировать цены и количества;
- отсеивать аномальные значения;
- ставить suspicious flags на выбросы;
- не принимать "тихую" подмену чужого external ID.

Если используется crawl:

- изолировать crawler;
- ограничивать outbound;
- задавать timeout/retry;
- логировать source failures;
- не выполнять сторонний JS без строгой необходимости.

## 8. Секреты и конфигурация

Секреты:

- не хранятся в репозитории;
- не логируются;
- не попадают в client bundle;
- ротируются;
- разделены по средам.

Отдельно хранить:

- DB credentials;
- Redis credentials;
- SMTP/API keys;
- S3 keys;
- partner integration tokens;
- admin bootstrap secrets.

## 9. Admin и backoffice

Admin endpoints должны быть:

- отделены от public API;
- защищены role checks;
- логируемы;
- ограничены rate limiting;
- закрыты от случайного прямого доступа.

Критичные действия:

- удаление данных;
- manual override цен;
- изменение ролей;
- верификация партнёров;
- повторный импорт;
- force publish / unpublish.

Для них нужны:

- audit events;
- actor ID;
- target ID;
- before/after snapshot где применимо;
- timestamp;
- IP / request meta;
- reason/comment.

## 10. Безопасность фоновых задач

Background jobs обязаны:

- получать только serializable validated payload;
- не выполнять произвольный код;
- не подтягивать невалидные URL без фильтра;
- иметь timeout;
- иметь retry policy;
- иметь dead-letter strategy;
- писать structured logs;
- не тащить в лог чувствительные данные.

## 11. Защита данных и приватность

Минимизируем хранение персональных данных.

Должны быть:

- политика хранения документов;
- политика удаления;
- soft delete там, где нужен аудит;
- redact/mask там, где есть чувствительные данные;
- разграничение между public result и internal audit.

### 11.1. Удаление аккаунта пользователем (реализовано 2026-04-17)

Эндпоинт: `DELETE /api/v1/auth/me`

Алгоритм soft-delete:

1. Аутентификация по `access_token` из заголовка `Authorization`.
2. Отзыв всех активных refresh-токенов пользователя (`revoked_at = now`).
3. Деактивация аккаунта (`is_active = False`).
4. Анонимизация email: `deleted_{user_id}@deleted.invalid`.
5. Обнуление `password_hash`.
6. Коммит транзакции.

Это обеспечивает: невозможность повторного входа, сохранность ссылочной целостности БД, минимальное хранение персональных данных.

### Базовая политика хранения

- исходный файл сметы: 30 дней после завершения джоба;
- estimate jobs и связанные строки: 90 дней, затем soft delete;
- soft-deleted estimate data: физическое удаление по отдельной retention-задаче;
- audit logs: не менее 1 года;
- price snapshots: хранятся как рыночная аналитика по отдельной политике обезличивания.

## 12. Observability и инциденты

Обязательно:

- structured logs;
- error tracking;
- security events stream;
- alerting по критичным сбоям;
- monitoring очередей и импорта;
- monitoring auth anomalies.

Нужны runbooks для:

- компрометации токена;
- массового сбоя импорта;
- подозрительной активности партнёра;
- всплеска ошибок логина;
- повреждения или потери данных.

## 13. Базовые secure coding rules

Нельзя:

- доверять данным клиента;
- собирать SQL строками;
- отдавать stack trace пользователю;
- использовать небезопасный file path join;
- открывать внутренние объекты по guessable ID без проверки прав;
- делать admin action без аудита;
- логировать secrets;
- смешивать domain logic и security checks в хаотичном виде.

Нужно:

- central auth middleware;
- central permission checks;
- central validation schemas;
- typed DTOs;
- transactional sensitive operations;
- tests на auth/authz.

## 14. Минимальный security gate перед запуском

До первого production-like запуска обязательно проверить:

- auth и RBAC;
- file upload validation;
- secret handling;
- admin audit logs;
- org boundary isolation;
- rate limiting;
- backup/restore;
- import validation;
- basic dependency scanning;
- basic SAST/secret scan.

Если хотя бы один из этих пунктов провален, запуск откладывается.
