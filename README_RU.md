# Lab #10 — Python CI Pipeline + Secret Management

Это НОВЫЙ проект, соответствующий инструкции для Lab #10, но на **Python вместо Spring Boot**.

## Требования лабораторной

| Этап | Реализация |
|---|---|
| Репозиторий | Публичный GitHub репозиторий |
| 2 SAST | Semgrep (`p/python` + пример собственного правила), CodeQL (Python) |
| 1 SCA | Trivy (`vuln,secret`) |
| Сборка | Flask-приложение + `unittest` + ZIP |
| Artifacts | `lab10-built-app`, `lab10-semgrep-report`, `lab10-codeql-report`, `lab10-trivy-report` |
| Вынесенные секреты | Локальный `.env` не коммитится, приложение читает переменные |
| Децентрализованный | **SOPS + age**: шифротекст в Git, приватный ключ отдельно |
| Централизованный | **Vault KV v2** в Docker dev режиме, временный токен только на чтение |

**Важно:** Vault dev mode существует только для демонстрации. Он не подходит для хранения реальных секретов. Для учебного проекта используются только фиктивные значения.

## Шаг 1. GitHub-репозиторий

Создай новый **Public** репозиторий `lab10-python-security` через https://github.com/new. Новый удобнее, чтобы не смешивать Java/Python/старые workflows, но можно использовать старый после удаления старых файлов.

Сначала распакуй ZIP. Внутри корня проекта должны быть `.github`, `app.py`, `config.py`, `requirements.txt`, `scripts`, `tests`. НЕ загружай ZIP как файл. Загружай содержимое, сохраняя скрытую папку `.github`.

Самый надёжный способ (нужны Git и PowerShell, команды из корня распакованного проекта):

```powershell
git init
git branch -M main
git add .
git commit -m "Lab10 Python initial CI"
git remote add origin https://github.com/<USERNAME>/lab10-python-security.git
git push -u origin main
```

Если используешь старый репозиторий, НЕ выполняй `git init` в нём повторно; скопируй новые файлы в существующую рабочую папку, удали старый workflow и закоммить.

## Шаг 2. Два SAST, один SCA

- **Semgrep**: проверяет Python-код через набор `p/python` плюс `.semgrep.yml`. В `examples/insecure_demo.py` специально есть небезопасный `eval()` для доказательства, что правила действительно срабатывают. Пример никогда не вызывается приложением.
- **CodeQL**: официальный CodeQL GitHub для языка `python` c `security-extended`. Для личного GitHub-аккаунта репозиторий должен быть **Public**.
- **Trivy**: сканирует зависимости и ищет утечки секретов в файловой системе репозитория. Если находит проблемы, сохраняет их в отчёт.

## Шаг 3. Сборка Python-приложения (вместо Maven)

На Windows в PowerShell в каталоге проекта:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/build.py
python app.py
```

Приложение откроется на `http://127.0.0.1:5000`. Проверь `/api/health` и `/api/config-status`. Останови `Ctrl+C`. В CI эти же проверки запустятся автоматически.

Если PowerShell запрещает активацию, используй `\.venv\Scripts\python.exe` вместо `python`, активация не обязательна.

## Шаг 4. GitHub Actions и отчёты

Workflow находится в `.github/workflows/ci.yml`.

После `git push` открой **Actions → Lab 10 - Python CI, SAST, SCA and Secrets**. Там будет **5 jobs**: `build`, `semgrep`, `codeql`, `trivy`, `secrets-demo`.

В конце в **Artifacts** ожидаются архив приложения, Semgrep JSON, CodeQL SARIF, Trivy JSON. Эти названия подтверждай по фактическому запуску. Security findings **не ломают** сборку, но ошибки инструментов/проверок — ломают.

## Шаг 5. Секреты вне кода: `.env`

Создай локальный `.env` из шаблона (фейковое значение):

```powershell
Copy-Item .env.example .env
```

В `config.py` используется `python-dotenv` + `os.environ`; секрет НЕ хранится в `app.py`. Проверь:

```powershell
python scripts/check_secret.py
git status --short --ignored
```

`.env` должен быть в списке **ignored**, НЕ commit. Секрет не печатается и веб-страница его не показывает.

## Шаг 6. Децентрализованное хранилище: SOPS + age

1. Установи `age` (включая `age-keygen`) с https://github.com/FiloSottile/age/releases и `sops` с https://github.com/getsops/sops/releases. На Windows выбирай `windows_amd64`/`win64`, распакуй в папку, которая находится в PATH. Перезапусти PowerShell.
2. Запусти в каталоге проекта:

```powershell
.\scripts\setup-sops.ps1
```

Скрипт генерирует ключ **вне Git**: `%USERPROFILE%\.lab10-private\age-key.txt`, создаёт `secrets/secrets.enc.env` (реальный зашифрованный файл), и `.sops.yaml` с **публичным** ключом.
3. Посмотри содержимое `secrets/secrets.enc.env`: вместо открытого значения должны быть данные формата `ENC[...]` и метаданные `sops`.
4. В GitHub открой **Settings → Secrets and variables → Actions → New repository secret**. Имя `LAB10_AGE_PRIVATE_KEY`. Значение — **полное содержимое** `age-key.txt` (вводи прямо на GitHub, не присылай в чат).
5. Коммить **только** `secrets/secrets.enc.env` и `.sops.yaml`, никогда не коммить приватный ключ, `.env` или временные нешифрованные файлы.
6. После push workflow должен вывести **SOPS: PASS** в Summary. Если сначала нет encrypted файла — job покажет **NOT CONFIGURED**, это ещё не выполненный этап.

## Шаг 7. Централизованное хранилище: HashiCorp Vault

Job `secrets-demo` автоматически поднимает Vault dev server в Docker на GitHub runner, добавляет секрет в **KV v2**, создаёт **read-only policy**, выдаёт токен на **10 минут**. `config.py` читает секрет через HTTP API Vault; тест записи с тем же токеном должен закончиться `HTTP 403`.

В логах ищи:

```text
PASS: Vault stored a random demo secret; scoped token READ allowed, WRITE 403.
PASS: app read Vault KV v2 via token; no secret values were logged.
```

Dev Vault в этом варианте НЕ постоянный сервер, но это реальный HashiCorp Vault и реальный токен ограниченного доступа. Для production требуется отдельный защищённый сервер, TLS, аудит и нормальный auth flow.

## Шаг 8. Отчёт и защита

Сделай скриншоты: (1) зелёный Actions run, (2) 4 Artifacts, (3) Semgrep JSON, (4) CodeQL SARIF / Security alerts, (5) Trivy JSON, (6) `ENC[...]` в зашифрованном файле, (7) `SOPS: PASS`, (8) `Vault... READ allowed, WRITE 403`.

**Пока новый pipeline реально не прошёл в GitHub, нельзя писать в отчёте, что все проверки успешны.** Фиксируй только результаты настоящего запуска.
