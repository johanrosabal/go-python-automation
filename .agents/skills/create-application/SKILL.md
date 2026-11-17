---
name: create-application
description: >-
  Creates a new Web UI or REST API application module inside 'applications/web/<app_name>' or 'applications/api/<app_name>' following the framework's mandatory folder structure, YAML environment files (dev, qa, uat, prod), App Orchestrator (<app_name>_app.py), application decorator (utils/decorators.py), and initial smoke test. Use this skill whenever the user asks to create, initialize, or onboard a new application or project into the framework.
---

# Skill: Create Application Module (Web UI or API)

Follow these exact steps whenever creating a new application under `applications/`:

## 1. Web UI Application Blueprint (`applications/web/<app_name>/`)

Create the following directory and file hierarchy (where `<app_name>` is lowercase `snake_case`, e.g., `go_hotel` and `<AppPascal>` is `PascalCase`, e.g., `GoHotel`):

```text
applications/web/<app_name>/
├── __init__.py
├── app/
│   ├── __init__.py
│   └── <app_name>_app.py
├── components/
│   └── __init__.py
├── config/
│   ├── __init__.py
│   └── environments/
│       ├── dev.yaml
│       ├── qa.yaml
│       ├── uat.yaml
│       └── prod.yaml
├── data/
│   ├── __init__.py
│   └── json/
├── fixtures/
│   ├── __init__.py
│   └── preconditions.py
├── pages/
│   └── __init__.py
├── tests/
│   └── __init__.py
└── utils/
    ├── __init__.py
    └── decorators.py
```

### A. App Orchestrator (`applications/web/<app_name>/app/<app_name>_app.py`)
```python
from core.ui.common.base_app import BaseApp


class <AppPascal>App(BaseApp):
    """
    App Orchestrator for the <AppPascal> application.
    Centralizes lazy-loaded access to all Page Objects via `self.app`.
    """
    pass
```

### B. Application Decorator (`applications/web/<app_name>/utils/decorators.py`)
```python
from core.utils.test_decorators import project_config
from applications.web.<app_name>.app.<app_name>_app import <AppPascal>App


def <app_name>(cls):
    """
    Decorator to configure default parameters for '<app_name>' application tests.
    """
    cls.profile = "qa"
    cls.browser = "chrome"
    return project_config(app_name="<app_name>", app_class=<AppPascal>App)(cls)
```

### C. Environment YAML Files (`applications/web/<app_name>/config/environments/qa.yaml`)
Create `dev.yaml`, `qa.yaml`, `uat.yaml`, and `prod.yaml` with:
```yaml
name: <AppPascal> Application
tms: https://tms.example.com/project/cases/
web:
  base_url: https://example.com/

default:
  browser: chrome

video:
  enable_local: false
  fps: 10
  monitor_index: 1

visual:
  enable: false

users:
  default_role: standard
  roles:
    standard:
      username: standard_user
      password: "b64:c2VjcmV0X3NhdWNl"
      description: "Default application user role"

databases:
  default_connection: primary
  connections:
    primary:
      engine: sqlite
      database: "resources/data/test.db"
      description: "Primary database connection"

messages: {}
```

---

## 2. REST API Application Blueprint (`applications/api/<app_name>/`)

When creating an API project, create:
```text
applications/api/<app_name>/
├── __init__.py
├── client.py                   # API Client Orchestrator exposing endpoints as @property
├── config/
│   └── environments/
│       ├── dev.yaml
│       ├── qa.yaml
│       ├── uat.yaml
│       └── prod.yaml
├── data/
│   └── qa/
├── endpoints/                  # Endpoint classes inheriting from BaseEndpoint
│   └── __init__.py
└── tests/                      # Test suites inheriting from BaseAPITest
    └── __init__.py
```

