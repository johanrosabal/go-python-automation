---
name: create-environment-yaml
description: >-
  Creates or updates multi-environment YAML configuration files (dev.yaml, qa.yaml, uat.yaml, prod.yaml) inside 'applications/<web_or_api>/<app_name>/config/environments/' following the framework's strict enterprise standards: web/api base_url, role-based user management (users.default_role & users.roles), 3-tier password security (plain, b64:, ENC:), multi-database connections (databases.default_connection & databases.connections), video/visual settings, and expected validation messages. Use this skill whenever the user asks to create, configure, update, or onboard environment configuration files.
---

# Skill: Create Environment YAML Configuration (`dev.yaml`, `qa.yaml`, `uat.yaml`, `prod.yaml`)

This skill defines the mandatory schema and rules for authoring or updating environment configuration files in `applications/<web_or_api>/<app_name>/config/environments/<env>.yaml`.

---

## 0. Fundamental Rules & Principles

1. **Independent File per Environment**:
   - Every application **MUST** maintain separate YAML files: `dev.yaml`, `qa.yaml`, `uat.yaml`, and `prod.yaml`.
   - Never combine environments into a single monolithic YAML file.
2. **Strict Hierarchy (Prohibited Root Keys)**:
   - **PROHIBITED**: Defining root-level user keys like `user:`, `invalid_user:`, `locked_user:`, or `admin_user:`. All credentials **MUST** be nested under `users.roles.<role_name>`.
   - **PROHIBITED**: Defining root-level raw database keys like `database: url: ...` for applications connecting to databases. All databases **MUST** be defined under `databases.connections.<alias>`.
3. **No Negative / Test-Specific Inputs in YAML**:
   - Negative test scenarios (e.g. invalid username/password combinations) belong in the JSON test case (`tests.data`), **NOT** in the environment YAML. The YAML only stores valid infrastructure and environment configuration.
4. **3-Tier Password Security Standard**:
   - **Tier 1 (Plain text)**: `password: "secret"` (Only for public sandbox apps or local disposable mocks).
   - **Tier 2 (Base64 Obfuscation)**: `password: "b64:<base64_string>"` (Standard for dev/qa/demo repositories to prevent plain text exposure).
   - **Tier 3 (Authenticated Encryption)**: `password: "ENC:<token>"` (For sensitive uat/prod environments, decrypted at runtime via `FRAMEWORK_SECRET_KEY` in `.env` or CI/CD).
   - **Environment Variable Fallback**: `password: "${MY_APP_PASSWORD:b64:...}"` (Permitted and encouraged for CI/CD pipelines).

---

## 1. Complete Blueprint Schema (`qa.yaml`)

Use this comprehensive template when generating a YAML file for Web or API applications:

```yaml
# =============================================================================
# Environment Configuration - QA
# Application: <App Name>
# =============================================================================
name: "<App Name> - <App Subtitle>"
tms: "https://tms.example.com/project/cases/"

# --- Target Application Endpoints ---
web:
  base_url: "https://qa.example.com/"
  timeout: 10

# (If API application, use 'api:' instead of or alongside 'web:')
# api:
#   base_url: "https://api-qa.example.com/v1"
#   timeout: 15

# --- Local Browser Overrides ---
default:
  browser: "chrome"   # chrome | edge | firefox

browser:
  edge_path: "C:/ai/go-python-selenium-automation/resources/drivers/msedgedriver.exe"

# --- Execution & Media Features ---
video:
  enable_local: true
  fps: 10
  monitor_index: 1

visual:
  enable: false

# =============================================================================
# Role-Based User Management
# Consumed in tests via:
#   - self.username / self.password        -> Resolves users.default_role
#   - self.get_user("<role>")              -> Returns full user dict
#   - self.get_username("<role>")          -> Returns username string
#   - self.get_password("<role>")          -> Returns decoded/decrypted password
#   - self.app.<page>.login_as("<role>")   -> Dedicated Page Object composite
#   - self.app.<page>.fill_form({"role": "<role>"}) -> Smart Form auto-population
# =============================================================================
users:
  default_role: standard

  roles:
    standard:
      username: "standard_user"
      password: "b64:c2VjcmV0X3NhdWNl"
      description: "Standard customer or default end-user role"

    admin:
      username: "admin_user"
      password: "b64:YWRtaW5fcGFzc3dvcmQ="
      description: "Superuser / Administrative privileges"

    locked:
      username: "locked_out_user"
      password: "b64:c2VjcmV0X3NhdWNl"
      description: "Account with locked status for error testing"

# =============================================================================
# Multi-Database Connections Configuration
# Consumed in tests via:
#   - self.get_db()                        -> Resolves databases.default_connection
#   - self.get_db("<alias>")               -> Returns DBClient for named connection
# Supported methods:
#   - .fetch_one(sql, params)              -> Returns dict or None
#   - .fetch_all(sql, params)              -> Returns list of dicts
#   - .fetch_value(sql, params)            -> Returns single scalar value
#   - .execute(sql, params)                -> Executes INSERT/UPDATE/DELETE
# =============================================================================
databases:
  default_connection: primary

  connections:
    # Option A: SQLite Local File
    primary:
      engine: sqlite
      database: "resources/data/test.db"
      description: "Primary local SQLite database"

    # Option B: Structured Connection (PostgreSQL, MySQL, SQL Server, Oracle)
    orders_db:
      engine: postgresql                  # postgresql | mysql+pymysql | mssql+pyodbc | oracle+oracledb | sqlite
      host: "${ORDERS_DB_HOST:localhost}"
      port: 5432
      database: "orders_qa"
      username: "qa_reader"
      password: "b64:c2VjcmV0X3NhdWNl"    # Automatically resolved via b64: or ENC:
      pool_size: 5
      max_overflow: 10
      description: "Orders microservice database"

    audit_db:
      engine: mysql+pymysql
      host: "${AUDIT_DB_HOST:localhost}"
      port: 3306
      database: "audit_logs_qa"
      username: "audit_user"
      password: "b64:c2VjcmV0X3NhdWNl"
      description: "Security and audit logs database"

# =============================================================================
# Expected Messages & Oracles for Assertion Verification
# Consumed in tests via: self.config.get("messages.<key>")
# =============================================================================
messages:
  error_invalid: "Epic sadface: Username and password do not match any user in this service"
  error_locked: "Epic sadface: Sorry, this user has been locked out."
  error_username_required: "Epic sadface: Username is required"
  error_password_required: "Epic sadface: Password is required"
```

---

## 2. Generating Passwords with the CLI Utility

When creating YAML files, you can use the built-in CLI utility to generate `b64:` and `ENC:` values:

```powershell
# Convert a plain password to Base64 (b64:...)
python -m core.utils.base64_utils b64 "secret_sauce"
# Output: b64:c2VjcmV0X3NhdWNl

# Generate a new 256-bit Master Key for .env (if using ENC:...)
python -m core.utils.base64_utils genkey
# Output: FRAMEWORK_SECRET_KEY=k9X...

# Encrypt a password with the master key (ENC:...)
python -m core.utils.base64_utils enc "secret_sauce"
# Output: ENC:7aB9...
```

---

## 3. Checklist for Creating or Modifying YAML Files

When creating or modifying environment YAML files, always check:
- [ ] Are all 4 environment files present or accounted for (`dev.yaml`, `qa.yaml`, `uat.yaml`, `prod.yaml`)?
- [ ] Is `web.base_url` (or `api.base_url`) properly configured with the right scheme (`https://`)?
- [ ] Is `users.default_role` defined, and does each role in `users.roles` have `username` and `password`?
- [ ] Are passwords obfuscated or encrypted using `b64:...`, `ENC:...`, or `${ENV_VAR:...}` instead of clear text?
- [ ] If the application connects to databases, is `databases.default_connection` defined with valid aliases under `databases.connections`?
- [ ] Are assertion messages grouped under `messages.`?
- [ ] No test-specific negative data (e.g. wrong passwords or invalid user objects) is placed in the YAML.

