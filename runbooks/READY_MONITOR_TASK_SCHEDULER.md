# READY_MONITOR_TASK_SCHEDULER

Runbook for periodic readiness monitoring on Windows via Task Scheduler.

## Goal

Run `scripts/monitor_ready.py` every 5 minutes and optionally send webhook alerts
when readiness is degraded/unavailable.

## Quick Start

From repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/register_ready_monitor_task.ps1
```

With custom webhook:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/register_ready_monitor_task.ps1 `
  -WebhookUrl "https://example.com/webhook"
```

With PROD/STAGING webhooks:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/register_ready_monitor_task.ps1 `
  -AlertEnv PROD `
  -ProdWebhookUrl "https://discord.com/api/webhooks/<prod_id>/<prod_token>" `
  -StagingWebhookUrl "https://discord.com/api/webhooks/<staging_id>/<staging_token>"
```

Create separate tasks for PROD and STAGING:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/register_ready_monitor_task.ps1 `
  -TaskName "BudgetChecker-ReadyMonitor-PROD" `
  -AlertEnv PROD

powershell -ExecutionPolicy Bypass -File scripts/register_ready_monitor_task.ps1 `
  -TaskName "BudgetChecker-ReadyMonitor-STAGING" `
  -AlertEnv STAGING
```

Note: the script stores webhooks in user env vars:
- `ALERT_WEBHOOK_URL_PROD`
- `ALERT_WEBHOOK_URL_STAGING`
- `BC_ALERT_ENV`
- `BC_READY_ENDPOINT_PROD`
- `BC_READY_ENDPOINT_STAGING`
- `BC_ALERT_SERVICE_NAME`
- `BC_ALERT_INSTANCE_ID`

Task Scheduler command stays short and avoids `/TR` length limits.
Discord alerts include environment tag, service name, instance id, host name and Kyiv timestamp. Template text is Russian-only.

## What gets created

- Task names (recommended):
  - `BudgetChecker-ReadyMonitor-PROD`
  - `BudgetChecker-ReadyMonitor-STAGING`
- Schedule: every 5 minutes
- Command: `.venv\Scripts\python.exe scripts/monitor_ready.py --alert-env ...`

## Verify

```powershell
schtasks /Query /TN "BudgetChecker-ReadyMonitor-PROD" /V /FO LIST
schtasks /Query /TN "BudgetChecker-ReadyMonitor-STAGING" /V /FO LIST
```

Manual probe check:

```powershell
.\.venv\Scripts\python.exe scripts\monitor_ready.py --endpoint http://127.0.0.1:8000/api/v1/health/ready
```

## Update Schedule

Re-run registration with another interval:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/register_ready_monitor_task.ps1 -EveryMinutes 2
```

## Rollback

Delete scheduled tasks:

```powershell
schtasks /Delete /TN "BudgetChecker-ReadyMonitor-PROD" /F
schtasks /Delete /TN "BudgetChecker-ReadyMonitor-STAGING" /F
```
