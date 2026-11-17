import time
from typing import Union, List, Dict, Optional
import allure
from core.ui.actions.playwright.base_action import BaseAction

class TableActions(BaseAction):
    """
    Playwright-native specialized component for interacting with HTML Tables and Grids.

    Provides high-performance cell reading, header introspection, row checking,
    and cell action dispatching using Playwright's native locator engine.
    """

    def _get_column_index(self, column: Union[int, str]) -> int:
        """
        Resolves a column identifier (1-based index or header name) to its 1-based index.

        Args:
            column: 1-based integer index or column header string.

        Returns:
            int: 1-based column index.
        """
        if isinstance(column, int):
            return column

        headers = self.get_table_headers()
        try:
            index = headers.index(column) + 1
            self.logger.info(f"Resolved column '{column}' to index {index}")
            return index
        except ValueError:
            self.logger.error(f"Column name '{column}' not found in table headers: {headers}")
            raise ValueError(f"Column '{column}' not found in table headers.")

    def get_cell_text(self, row: int, col: Union[int, str]) -> str:
        """
        Retrieves the text from a specific cell within a table.

        Args:
            row (int): 1-based row index.
            col (Union[int, str]): 1-based column index or column name.

        Returns:
            str: Visible cell text.
        """
        try:
            target_col = self._get_column_index(col)
            cell_locator = self.get_locator().locator(f"tr:nth-of-type({row}) td:nth-of-type({target_col})")
            if cell_locator.count() == 0:
                # Fallback to xpath if nth-of-type semantics differ across thead/tbody
                cell_locator = self.get_locator().locator(f"xpath=.//tr[{row}]/td[{target_col}]")
            text = cell_locator.inner_text(timeout=self._current_timeout)
            return text.strip()
        except Exception as e:
            self._handle_exception(e, "get_cell_text")

    @allure.step("Getting row count")
    def get_row_count(self) -> int:
        """
        Returns the total number of rows (<tr>) currently present in the table.

        Returns:
            int: Row count.
        """
        try:
            count = self.get_locator().locator("tr").count()
            self.logger.info(f"Table row count: {count}")
            return count
        except Exception as e:
            self._handle_exception(e, "get_row_count")

    def get_table_headers(self) -> List[str]:
        """
        Retrieves the visible text of all table headers (<th>).

        Returns:
            List[str]: List of header names.
        """
        try:
            headers = self.get_locator().locator("th").all_inner_texts()
            cleaned = [h.strip() for h in headers]
            self.logger.info(f"Table headers found: {cleaned}")
            return cleaned
        except Exception as e:
            self._handle_exception(e, "get_table_headers")

    @allure.step("Clicking table header")
    def click_header(self, text: Optional[str] = None, index: Optional[int] = None) -> "TableActions":
        """
        Clicks a table header by text content or 1-based index.

        Args:
            text (str, optional): Exact text of the header.
            index (int, optional): 1-based index of the header.

        Returns:
            TableActions: The current instance for method chaining.
        """
        try:
            headers_loc = self.get_locator().locator("th")
            if text:
                headers_loc.filter(has_text=text).first.click(timeout=self._current_timeout)
            elif index is not None:
                headers_loc.nth(index - 1).click(timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "click_header")

    @allure.step("Getting all table data")
    def get_table_data(self) -> List[Dict[str, str]]:
        """
        Extracts all table data into a list of dictionaries mapped by column header.

        Returns:
            List[Dict[str, str]]: Table rows mapped to headers.
        """
        try:
            headers = self.get_table_headers()
            rows_loc = self.get_locator().locator("tbody tr" if self.get_locator().locator("tbody tr").count() > 0 else "tr")
            count = rows_loc.count()

            data = []
            start_idx = 1 if not self.get_locator().locator("tbody").count() and self.get_locator().locator("th").count() else 0

            for i in range(start_idx, count):
                row = rows_loc.nth(i)
                cells = row.locator("td").all_inner_texts()
                if cells:
                    row_dict = {}
                    for col_idx, cell_text in enumerate(cells):
                        key = headers[col_idx] if col_idx < len(headers) else f"Column_{col_idx+1}"
                        row_dict[key] = cell_text.strip()
                    data.append(row_dict)

            self.logger.info(f"Extracted {len(data)} rows from table.")
            return data
        except Exception as e:
            self._handle_exception(e, "get_table_data")

    @allure.step("Checking all rows in table (Column {column})")
    def table_check_all(self, column: Union[int, str] = 1) -> "TableActions":
        """
        Interacts with the 'Select All' checkbox in header or first row.

        Args:
            column: 1-based column index or header name.

        Returns:
            TableActions: The current instance for method chaining.
        """
        try:
            col_idx = self._get_column_index(column)
            chk = self.get_locator().locator(f"xpath=(.//th[{col_idx}]|.//tr[1]/td[{col_idx}])//input[@type='checkbox']").first
            if not chk.is_checked():
                chk.check(timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "table_check_all")

    @allure.step("Checking row {index} (Column {column})")
    def table_check_row(self, index: int, column: Union[int, str] = 1) -> "TableActions":
        """
        Checks the checkbox inside a specific row and column.

        Args:
            index (int): 1-based row index.
            column: 1-based column index or header name.

        Returns:
            TableActions: The current instance for method chaining.
        """
        try:
            col_idx = self._get_column_index(column)
            chk = self.get_locator().locator(f"xpath=.//tr[{index}]/td[{col_idx}]//input[@type='checkbox']").first
            if not chk.is_checked():
                chk.check(timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "table_check_row")

    @allure.step("Clicking button in row {row}, col {col}")
    def table_click_button(self, row: int, col: Union[int, str], text: Optional[str] = None) -> "TableActions":
        """
        Clicks a button inside a specific cell.

        Args:
            row (int): 1-based row index.
            col: 1-based column index or header name.
            text (str, optional): Text filter for button.

        Returns:
            TableActions: The current instance for method chaining.
        """
        try:
            col_idx = self._get_column_index(col)
            if text:
                xpath = f".//tr[{row}]/td[{col_idx}]//*[(self::button or (self::input and (@type='button' or @type='submit'))) and (contains(text(), '{text}') or contains(@value, '{text}'))]"
            else:
                xpath = f".//tr[{row}]/td[{col_idx}]//*[self::button or (self::input and (@type='button' or @type='submit'))]"

            self.get_locator().locator(f"xpath={xpath}").first.click(timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "table_click_button")

    @allure.step("Clicking link in row {row}, col {col}")
    def table_click_link(self, row: int, col: Union[int, str], text: Optional[str] = None) -> "TableActions":
        """
        Clicks an anchor link inside a specific cell.

        Args:
            row (int): 1-based row index.
            col: 1-based column index or header name.
            text (str, optional): Text filter for anchor.

        Returns:
            TableActions: The current instance for method chaining.
        """
        try:
            col_idx = self._get_column_index(col)
            if text:
                xpath = f".//tr[{row}]/td[{col_idx}]//a[contains(text(), '{text}')]"
            else:
                xpath = f".//tr[{row}]/td[{col_idx}]//a"

            self.get_locator().locator(f"xpath={xpath}").first.click(timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "table_click_link")

    @allure.step("Waiting for table to have {expected_count} rows")
    def table_wait_for_rows(self, expected_count: int, timeout: Optional[int] = None) -> "TableActions":
        """
        Waits until the table has the expected row count.

        Args:
            expected_count (int): Target row count.
            timeout (int, optional): Timeout in seconds.

        Returns:
            TableActions: The current instance for method chaining.
        """
        max_time = timeout or (self._current_timeout / 1000)
        start = time.time()
        while time.time() - start < max_time:
            if self.get_row_count() == expected_count:
                return self
            time.sleep(0.2)
        raise TimeoutError(f"Table row count did not reach {expected_count} within {max_time} seconds.")

    @allure.step("Waiting for table to not be empty")
    def table_wait_not_empty(self, timeout: Optional[int] = None) -> "TableActions":
        """
        Waits until the table contains at least one row beyond the header.

        Args:
            timeout (int, optional): Timeout in seconds.

        Returns:
            TableActions: The current instance for method chaining.
        """
        max_time = timeout or (self._current_timeout / 1000)
        start = time.time()
        while time.time() - start < max_time:
            if self.get_row_count() > 1:
                return self
            time.sleep(0.2)
        raise TimeoutError(f"Table remained empty after {max_time} seconds.")

