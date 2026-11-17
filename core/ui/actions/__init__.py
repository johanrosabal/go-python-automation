from core.ui.actions.factory import ActionFactory
from core.ui.actions.ui_element import UIElement
from core.ui.actions.selenium import (
    BaseAction,
    AlertActions,
    CheckActions,
    ClickActions,
    CookieActions,
    DiagnosticsActions,
    DropdownActions,
    ElementsActions,
    FrameActions,
    GetTextActions,
    NavigationActions,
    RadioActions,
    ScreenshotActions,
    ScriptActions,
    ScrollActions,
    SendKeysActions,
    StorageActions,
    SwitchWindowsActions,
    TableActions,
    UploadActions,
)

__all__ = [
    "ActionFactory",
    "UIElement",
    "BaseAction",
    "AlertActions",
    "CheckActions",
    "ClickActions",
    "CookieActions",
    "DiagnosticsActions",
    "DropdownActions",
    "ElementsActions",
    "FrameActions",
    "GetTextActions",
    "NavigationActions",
    "RadioActions",
    "ScreenshotActions",
    "ScriptActions",
    "ScrollActions",
    "SendKeysActions",
    "StorageActions",
    "SwitchWindowsActions",
    "TableActions",
    "UploadActions",
]

# Dynamic backward-compatibility resolver for legacy action module imports
# (e.g., from core.ui.actions.Click import Click, from core.ui.actions import SendKeys)
# Keeps the core/ui/actions/ directory clean without loose shim files.
import sys
import types
from importlib.abc import Loader, MetaPathFinder

class _LegacyActionFinder(MetaPathFinder):
    _MAP = {
        "Click": "LegacyClick",
        "SendKeys": "LegacySendKeys",
        "GetText": "LegacyGetText",
        "Navigation": "LegacyNavigation",
        "Screenshot": "LegacyScreenshot",
        "Dropdown": "LegacyDropdown",
        "Checkbox": "LegacyCheckbox",
        "Radio": "LegacyRadio",
        "Table": "LegacyTable",
        "AlertPrompt": "LegacyAlert",
        "Frame": "LegacyFrame",
        "SwitchWindow": "LegacySwitchWindow",
        "UploadFile": "LegacyUploadFile",
        "Scroll": "LegacyScroll",
        "Screeenshot": "LegacyScreenshot",
        "Element": "LegacyElement",
        "ElementHighlighter": "LegacyElementHighlighter",
        "VerifyLocators": "LegacyVerifyLocators",
    }

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith("core.ui.actions."):
            sub = fullname.split(".")[-1]
            if sub in self._MAP:
                from importlib.machinery import ModuleSpec
                return ModuleSpec(fullname, _LegacyActionLoader(sub, self._MAP[sub]))
        return None

class _LegacyActionLoader(Loader):
    def __init__(self, name, target_cls):
        self.name = name
        self.target_cls = target_cls

    def create_module(self, spec):
        mod = types.ModuleType(spec.name)
        from core.ui.adapters.legacy import actions
        cls = getattr(actions, self.target_cls, None)
        setattr(mod, self.name, cls)
        if self.name == "Screeenshot":
            setattr(mod, "Screenshot", cls)
        return mod

    def exec_module(self, module):
        pass

# Register the meta path finder once
if not any(isinstance(f, _LegacyActionFinder) for f in sys.meta_path):
    sys.meta_path.append(_LegacyActionFinder())

def __getattr__(name: str):
    if name in _LegacyActionFinder._MAP:
        from core.ui.adapters.legacy import actions
        return getattr(actions, _LegacyActionFinder._MAP[name])
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

