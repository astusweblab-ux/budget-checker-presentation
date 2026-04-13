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
