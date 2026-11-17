from typing import Type, TypeVar
from core.ui.common.base_app import BaseApp
from core.ui.actions.ui_element import UIElement
from core.ui.actions.selenium.navigation_actions import NavigationActions
from selenium.webdriver.remote.webdriver import WebDriver

TComponent = TypeVar("TComponent", bound="BaseComponent")


class BaseComponent(BaseApp):
    """
    Foundational Base class for reusable UI Components / Widgets (e.g., Sidebar, Header, Modal).

    Supports declarative `find_by` descriptors and contextual logging, allowing shared
    UI sections to be composed cleanly inside multiple Page Objects without duplicating locators.
    """

    def __init__(self, page_object=None, driver: WebDriver = None):
        self.page_object = page_object
        self._navigation = None

    @property
    def navigation(self) -> NavigationActions:
        if self._navigation is None:
            self._navigation = NavigationActions(self.driver)
        return self._navigation

    def element(self, locator: tuple) -> UIElement:
        """Creates a `UIElement` facade bound to this component."""
        return UIElement(self.driver, locator, page_object=self)


class ComponentDescriptor:
    """
    Declarative descriptor that lazily instantiates and caches a `BaseComponent`
    bound to the owning Page Object and active WebDriver.
    """

    def __init__(self, component_cls: Type[TComponent]):
        self.component_cls = component_cls
        self.attr_name = None

    def __set_name__(self, owner, name: str):
        self.attr_name = name

    def __get__(self, instance, owner=None) -> TComponent:
        if instance is None:
            return self
        cache = getattr(instance, "_component_instance_cache", None)
        if cache is None:
            cache = {}
            instance._component_instance_cache = cache
        cache_key = (self.attr_name or id(self), id(instance.driver))
        if cache_key not in cache:
            cache[cache_key] = self.component_cls(page_object=instance)
        return cache[cache_key]


def component(component_cls: Type[TComponent]) -> TComponent:
    """
    Declaratively attaches a reusable `BaseComponent` to a `BasePage`.

    Example:
        class InventoryPage(BasePage):
            sidebar = component(SidebarComponent)
    """
    return ComponentDescriptor(component_cls)


