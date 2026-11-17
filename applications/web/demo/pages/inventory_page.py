from typing import Self
import allure
from core.ui.common.base_page import BasePage
from core.ui.common.base_component import component
from core.ui.common.find_by import find_by
from applications.web.demo.components.sidebar_component import SidebarComponent


class InventoryPage(BasePage):
    """
    3-Layer Page Object Model for the SauceDemo Inventory (Products) Page.
    """

    PAGE_PATH = "/inventory.html"

    # =========================================================================
    # LAYER 1: Declarative Locators (Prefix + Label + Anchor)
    # =========================================================================
    lbl_title = find_by(class_name="title", label="Products Page Title", anchor=True)
    btn_add_backpack = find_by(
        id="add-to-cart-sauce-labs-backpack", label="Add Backpack to Cart Button"
    )
    btn_add_product = find_by(
        xpath="//div[text()='{product}']/ancestor::div[@class='inventory_item']//button",
        label="Add '{product}' to Cart Button",
    )

    sidebar = component(SidebarComponent)

    # =========================================================================
    # LAYER 2: Granular Atomic Methods (Getters, Checks, Clicks)
    # =========================================================================
    def get_header_title(self) -> str:
        """Returns the text of the inventory page header title ('Products')."""
        return self.lbl_title.get_text()

    def is_title_visible(self) -> bool:
        """Checks if the inventory page title is visible."""
        return self.lbl_title.is_visible()

    @allure.step("Adding backpack to cart")
    def add_backpack_to_cart(self) -> Self:
        """Clicks the 'Add to cart' button for the backpack."""
        self.btn_add_backpack.click()
        return self

    @allure.step("Adding product '{product_name}' to cart")
    def click_add_product(self, product_name: str) -> Self:
        """Clicks 'Add to cart' for any product by name using dynamic selector."""
        self.btn_add_product.format(product=product_name).click()
        return self

    # =========================================================================
    # LAYER 3: Composite Business Methods
    # =========================================================================
    @allure.step("Logging out from inventory page")
    def logout(self):
        """Performs the logout sequence via the reusable sidebar component."""
        return self.sidebar.logout()

