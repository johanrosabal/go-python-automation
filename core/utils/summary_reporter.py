"""
Summary Reporter for Pytest Execution.
Generates an enterprise-grade tabular summary of all executed test cases
displaying Test ID, Name, Status (PASSED/FAILED/SKIPPED), Duration, and Error Details.
"""
from typing import Dict, List, Optional, Any
import logging


class SummaryReporter:
    _records: Dict[str, Dict[str, Any]] = {}
    logger = logging.getLogger("SummaryReporter")

    @classmethod
    def reset(cls):
        """Clears accumulated records for a fresh session."""
        cls._records.clear()

    @classmethod
    def record_test_result(cls, item: Any, call: Any, rep: Any):
        """
        Records the outcome of a test case from pytest_runtest_makereport.
        Guarantees that each test nodeid has a single consolidated entry.
        """
        nodeid = item.nodeid
        func = getattr(item, "function", None)
        wrapped = getattr(func, "__wrapped__", func) if func else None

        # Resolve Test ID: @test_case(id="...") -> item._test_id -> N/A
        test_id = getattr(func, "_test_id", getattr(wrapped, "_test_id", None))
        if not test_id:
            test_id = getattr(item, "_test_id", "N/A")

        # Resolve Test Name / Title
        meta = getattr(func, "_test_metadata", getattr(wrapped, "_test_metadata", {}))
        test_name = getattr(func, "__name__", item.name)
        test_title = meta.get("title") or getattr(func, "_test_arg_title", getattr(wrapped, "_test_arg_title", None)) or test_name

        # Determine Outcome & Error Details
        duration = getattr(rep, "duration", 0.0)
        error_msg = ""

        if rep.passed:
            status = "PASSED"
        elif rep.failed:
            status = "FAILED"
            # Extract clean, concise error line
            if call and call.excinfo:
                val = str(call.excinfo.value).strip()
                exc_type = getattr(call.excinfo.type, "__name__", "Error")
                if val:
                    first_line = val.splitlines()[0]
                    error_msg = f"{exc_type}: {first_line}" if not first_line.startswith(exc_type) else first_line
                else:
                    error_msg = exc_type
            if not error_msg and getattr(rep, "longreprtext", None):
                lines = [l.strip() for l in rep.longreprtext.splitlines() if l.strip()]
                for line in reversed(lines):
                    if line.startswith("E   ") or "Error:" in line or "Exception:" in line or "Failed:" in line:
                        error_msg = line.replace("E   ", "").strip()
                        break
                if not error_msg and lines:
                    error_msg = lines[-1]
            if rep.when == "setup":
                error_msg = f"[Setup Failed] {error_msg}".strip()
            elif rep.when == "teardown":
                error_msg = f"[Teardown Failed] {error_msg}".strip()
        elif rep.skipped:
            status = "SKIPPED"
            error_msg = getattr(rep, "wasxfail", "") or "Skipped"
        else:
            status = "UNKNOWN"

        # Update or set record
        if rep.when == "call" or rep.failed or nodeid not in cls._records:
            cls._records[nodeid] = {
                "nodeid": nodeid,
                "id": str(test_id),
                "name": str(test_name),
                "title": str(test_title),
                "status": status,
                "duration": duration,
                "error": error_msg,
            }

    @classmethod
    def render_table(cls) -> str:
        """
        Renders the execution summary as a structured, monospaced ASCII table.
        """
        records = list(cls._records.values())
        if not records:
            return ""

        id_w = max([len(r["id"]) for r in records] + [7])
        id_w = min(max(id_w, 10), 18)

        name_w = max([len(r["name"]) for r in records] + [15])
        name_w = min(max(name_w, 24), 46)

        status_w = 11
        time_w = 9
        err_w = 46

        total_w = id_w + name_w + status_w + time_w + err_w + 16

        sep = "+" + "-" * (id_w + 2) + "+" + "-" * (name_w + 2) + "+" + "-" * (status_w + 2) + "+" + "-" * (time_w + 2) + "+" + "-" * (err_w + 2) + "+"
        header = f"| {'TEST ID':<{id_w}} | {'TEST CASE NAME':<{name_w}} | {'STATUS':<{status_w}} | {'DURATION':<{time_w}} | {'ERROR / DETAILS':<{err_w}} |"

        lines = [
            "",
            "=" * total_w,
            f"{'📊 TEST EXECUTION SUMMARY':^{total_w}}",
            "=" * total_w,
            sep,
            header,
            sep,
        ]

        passed = 0
        failed = 0
        skipped = 0
        total_time = 0.0

        for r in records:
            total_time += r.get("duration", 0.0)
            st = r["status"].upper()
            if st == "PASSED":
                passed += 1
                badge = "✅ PASSED"
            elif st == "FAILED":
                failed += 1
                badge = "❌ FAILED"
            else:
                skipped += 1
                badge = "⚠️ SKIPPED"

            name = r["name"]
            if len(name) > name_w:
                name = name[:name_w - 3] + "..."

            err = r.get("error", "") or "-"
            if len(err) > err_w:
                err = err[:err_w - 3] + "..."

            t_str = f"{r.get('duration', 0.0):.2f}s"
            row = f"| {r['id']:<{id_w}} | {name:<{name_w}} | {badge:<{status_w}} | {t_str:<{time_w}} | {err:<{err_w}} |"
            lines.append(row)

        lines.append(sep)
        summary_footer = f"TOTAL: {len(records)} | PASSED: {passed} | FAILED: {failed} | SKIPPED: {skipped} | TOTAL DURATION: {total_time:.2f}s"
        lines.append(f"  {summary_footer}")
        lines.append("=" * total_w)
        lines.append("")

        return "\n".join(lines)

    @classmethod
    def print_summary(cls, terminalreporter=None):
        """Prints the summary table to the terminal reporter and/or stdout."""
        table = cls.render_table()
        if not table:
            return

        if terminalreporter:
            terminalreporter.write_line(table)
        else:
            print(table)
