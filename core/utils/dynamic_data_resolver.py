import re
import os
import time
import uuid
import random
import string
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

# Thread-local storage for test execution variable context (e.g. {{faker.email:save=email}} -> {{get:email}})
_context_local = threading.local()

# Regex to detect {{...}} placeholders
_DYNAMIC_PATTERN = re.compile(r"\{\{([^}]+)\}\}")

try:
    from faker import Faker
    _FAKER_AVAILABLE = True
    _FAKER_INSTANCES: Dict[str, Faker] = {}
except ImportError:
    _FAKER_AVAILABLE = False
    _FAKER_INSTANCES = {}


def _get_faker(locale: str = "es_MX") -> Optional[Any]:
    if not _FAKER_AVAILABLE:
        return None
    if locale not in _FAKER_INSTANCES:
        try:
            _FAKER_INSTANCES[locale] = Faker(locale)
        except Exception:
            _FAKER_INSTANCES[locale] = Faker()
    return _FAKER_INSTANCES[locale]


class DynamicDataResolver:
    """
    Enterprise Dynamic Data & Synthetic Mocking Resolver.
    
    Processes string templates containing `{{...}}` expressions in test data JSON files,
    resolving:
      - Relative Dates: `{{today}}`, `{{tomorrow}}`, `{{yesterday}}`, `{{date:offset}}`, `{{future_date:offset}}`
      - Date Formats: `{{today:format=%d/%m/%Y}}`, `{{date:7:format=%Y-%m-%d}}`
      - Synthetic Faker Data: `{{faker.name}}`, `{{faker.email}}`, `{{faker.phone}}`, etc.
      - Random Generators: `{{random_int:min:max}}`, `{{random_str:len}}`, `{{timestamp}}`, `{{uuid}}`
      - Contextual Variables: `{{faker.email:save=user_mail}}` paired with `{{get:user_mail}}`
    
    Thread-safe and deterministic across parallel workers (pytest-xdist).
    """

    @classmethod
    def get_context(cls) -> Dict[str, Any]:
        """Retrieves or initializes the thread-local variable cache for the current test."""
        if not hasattr(_context_local, "variables"):
            _context_local.variables = {}
        return _context_local.variables

    @classmethod
    def clear_context(cls):
        """Clears the thread-local variable cache (called at test teardown)."""
        if hasattr(_context_local, "variables"):
            _context_local.variables.clear()

    @classmethod
    def set_variable(cls, key: str, value: Any):
        """Stores a named variable in the current test context."""
        cls.get_context()[key.strip()] = value

    @classmethod
    def get_variable(cls, key: str, default: Any = None) -> Any:
        """Retrieves a named variable from the current test context."""
        return cls.get_context().get(key.strip(), default)

    @classmethod
    def resolve(cls, data: Any) -> Any:
        """
        Recursively resolves all dynamic `{{...}}` expressions in strings, dicts, and lists.
        """
        if isinstance(data, dict):
            return {k: cls.resolve(v) for k, v in data.items()}
        if isinstance(data, list):
            return [cls.resolve(item) for item in data]
        if isinstance(data, str) and "{{" in data and "}}" in data:
            return cls._resolve_string(data)
        return data

    @classmethod
    def _resolve_string(cls, text: str) -> Any:
        """
        Resolves dynamic placeholders in a single string.
        If the entire string is exactly one placeholder (e.g. "{{random_int:1:10}}"),
        returns the native primitive (int, bool) rather than converting to str.
        """
        # Exact single match
        exact_match = re.fullmatch(r"\{\{([^}]+)\}\}", text.strip())
        if exact_match:
            return cls._evaluate_token(exact_match.group(1).strip())

        # Substring replacement for composite strings (e.g. "Order-{{random_int:10:99}}-{{today}}")
        def _repl(match):
            val = cls._evaluate_token(match.group(1).strip())
            return str(val) if val is not None else ""

        return _DYNAMIC_PATTERN.sub(_repl, text)

    @classmethod
    def _evaluate_token(cls, token: str) -> Any:
        """
        Parses and evaluates an individual token without enclosing braces.
        Supports ':save=var_name' syntax.
        """
        save_var = None
        if ":save=" in token:
            parts = token.split(":save=")
            token = parts[0]
            save_var = parts[1].strip()

        value = cls._dispatch_token(token)

        if save_var:
            cls.set_variable(save_var, value)

        return value

    @classmethod
    def _dispatch_token(cls, token: str) -> Any:
        # 1. Variable Getter: {{get:var_name}} or {{var:var_name}}
        if token.startswith(("get:", "var:")):
            _, var_name = token.split(":", 1)
            return cls.get_variable(var_name, f"{{MISSING_VAR:{var_name}}}")

        # 2. Date: {{today}}, {{tomorrow}}, {{yesterday}}
        lower_token = token.lower()
        now = datetime.now()

        # Format helper
        def _parse_format_and_offset(token_str: str, default_offset: int = 0) -> tuple[int, str]:
            offset = default_offset
            date_format = "%Y-%m-%d"
            parts = token_str.split(":")
            for p in parts:
                p = p.strip()
                if p.startswith("format="):
                    date_format = p.replace("format=", "").strip()
                elif p.lstrip("-").isdigit():
                    offset = int(p)
            return offset, date_format

        if lower_token.startswith("today"):
            _, fmt = _parse_format_and_offset(token, 0)
            return now.strftime(fmt)

        if lower_token.startswith("tomorrow"):
            _, fmt = _parse_format_and_offset(token, 1)
            return (now + timedelta(days=1)).strftime(fmt)

        if lower_token.startswith("yesterday"):
            _, fmt = _parse_format_and_offset(token, -1)
            return (now - timedelta(days=1)).strftime(fmt)

        # 3. Relative Date: {{date:offset[:format=...]}} or {{future_date:offset[:format=...]}}
        if lower_token.startswith(("date:", "future_date:", "past_date:")):
            offset, fmt = _parse_format_and_offset(token, 0)
            target_date = now + timedelta(days=offset)
            return target_date.strftime(fmt)

        # 4. Datetime & Timestamps
        if lower_token in ("now", "datetime"):
            return now.strftime("%Y-%m-%d %H:%M:%S")

        if lower_token == "timestamp":
            return int(time.time())

        if lower_token == "timestamp_ms":
            return int(time.time() * 1000)

        if lower_token == "uuid":
            return str(uuid.uuid4())

        # 5. Random Numbers & Strings
        if lower_token.startswith("random_int:"):
            # {{random_int:min:max}}
            parts = token.split(":")
            if len(parts) >= 3:
                try:
                    min_val = int(parts[1])
                    max_val = int(parts[2])
                    return random.randint(min_val, max_val)
                except ValueError:
                    pass
            return random.randint(1000, 9999)

        if lower_token.startswith("random_str:"):
            # {{random_str:length}}
            parts = token.split(":")
            length = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 8
            chars = string.ascii_letters + string.digits
            return "".join(random.choice(chars) for _ in range(length))

        if lower_token.startswith("random_choice:"):
            # {{random_choice:op1|op2|op3}}
            parts = token.split(":", 1)
            if len(parts) == 2:
                options = [opt.strip() for opt in parts[1].split("|") if opt.strip()]
                if options:
                    return random.choice(options)
            return ""

        # 6. Faker Providers: {{faker.name}}, {{faker.email}}, {{faker.es_MX.phone}}
        if token.startswith("faker."):
            return cls._resolve_faker(token)

        # Unrecognized token - return untouched
        return f"{{{{{token}}}}}"

    @classmethod
    def _resolve_faker(cls, token: str) -> Any:
        """
        Resolves Faker providers dynamically, with locale support and zero-dependency fallbacks.
        Examples:
          {{faker.name}}
          {{faker.email}}
          {{faker.es_MX.address}}
        """
        parts = token.split(".")
        locale = "es_MX"
        method_name = parts[1]

        if len(parts) == 3:
            locale = parts[1]
            method_name = parts[2]

        # Alias mappings
        aliases = {
            "email": "email",
            "name": "name",
            "first_name": "first_name",
            "last_name": "last_name",
            "phone": "phone_number",
            "phone_number": "phone_number",
            "address": "address",
            "street": "street_address",
            "city": "city",
            "country": "country",
            "postcode": "postcode",
            "company": "company",
            "job": "job",
            "text": "sentence",
            "description": "paragraph",
            "url": "url",
            "ipv4": "ipv4",
        }
        resolved_method = aliases.get(method_name.lower(), method_name)

        # 1. Try real Faker if installed
        faker_inst = _get_faker(locale)
        if faker_inst and hasattr(faker_inst, resolved_method):
            try:
                result = getattr(faker_inst, resolved_method)()
                return result
            except Exception:
                pass

        # 2. Native Fallback (Zero-Dependency)
        rand_num = random.randint(100, 9999)
        first_names = ["Carlos", "Ana", "Sofia", "Alejandro", "Mateo", "Valentina", "Diego", "Lucia"]
        last_names = ["Ramirez", "Gomez", "Fernandez", "Rodriguez", "Morales", "Herrera", "Vargas"]
        companies = ["Innovatech", "Acme Corp", "Apex Solutions", "Global Logistic", "Nexus QA"]

        if resolved_method in ("name",):
            return f"{random.choice(first_names)} {random.choice(last_names)}"
        if resolved_method in ("first_name",):
            return random.choice(first_names)
        if resolved_method in ("last_name",):
            return random.choice(last_names)
        if resolved_method in ("email",):
            fn = random.choice(first_names).lower()
            return f"{fn}_{rand_num}@testqa.com"
        if resolved_method in ("phone_number", "phone"):
            return f"+506 {random.randint(6000, 8999)}-{random.randint(1000, 9999)}"
        if resolved_method in ("company",):
            return f"{random.choice(companies)} S.A."
        if resolved_method in ("city",):
            return random.choice(["San Jose", "Bogota", "Mexico DF", "Madrid", "Lima", "Buenos Aires"])
        if resolved_method in ("country",):
            return random.choice(["Costa Rica", "Colombia", "Mexico", "Espana", "Chile", "Peru"])
        if resolved_method in ("address", "street_address"):
            return f"Avenida {random.randint(1, 50)}, Calle {random.randint(1, 100)}, Edificio #{rand_num}"
        if resolved_method in ("sentence", "text", "description", "paragraph"):
            return f"Registro automatizado de prueba {rand_num} generado exitosamente."

        return f"Mock-{method_name}-{rand_num}"

