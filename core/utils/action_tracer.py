import os
import json
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

_local = threading.local()


class ActionTracer:
    """
    Time-Travel Action Tracer for Enterprise UI & API Observability.
    
    Captures a high-resolution, millisecond-by-millisecond timeline of every
    action (clicks, keystrokes, navigations, waits, validations) executed
    during a test session.
    
    Thread-safe and process-safe for massive parallel test execution (pytest-xdist).
    Exports rich interactive HTML timelines for Allure attachments and
    machine-readable JSON artifacts for reporting dashboards.
    """

    @classmethod
    def _get_buffer(cls) -> List[Dict[str, Any]]:
        if not hasattr(_local, "trace_buffer"):
            _local.trace_buffer = []
        return _local.trace_buffer

    @classmethod
    def start_trace(cls, test_id: str):
        """Initializes a new chronological trace recording for the active thread."""
        _local.test_id = test_id
        _local.trace_start_time = time.time()
        _local.trace_buffer = []
        _local.step_counter = 0

    @classmethod
    def record_action(
        cls,
        action: str,
        page: str = "",
        element: str = "",
        locator: Any = None,
        duration_ms: float = 0,
        status: str = "PASS",
        details: str = "",
    ):
        """
        Appends an action event to the current test trace.
        """
        buffer = cls._get_buffer()
        _local.step_counter = getattr(_local, "step_counter", 0) + 1
        
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S.") + f"{int(now.microsecond / 1000):03d}"

        entry = {
            "step": _local.step_counter,
            "timestamp": timestamp,
            "action": action,
            "page": page or "App",
            "element": str(element),
            "locator": str(locator) if locator else "",
            "duration_ms": round(duration_ms, 2),
            "status": status.upper(),
            "details": details,
        }
        buffer.append(entry)

    @classmethod
    def stop_trace(cls) -> List[Dict[str, Any]]:
        """Stops the active trace and returns the raw recorded action sequence."""
        return list(cls._get_buffer())

    @classmethod
    def export_json(cls, test_id: str = None) -> Optional[str]:
        """
        Saves the recorded trace to `reports/traces/<test_id>_trace.json`.
        Returns the absolute file path.
        """
        tid = test_id or getattr(_local, "test_id", "test")
        buffer = cls._get_buffer()
        if not buffer:
            return None

        output_dir = os.path.abspath("reports/traces")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{tid}_trace.json")

        summary = {
            "test_id": tid,
            "total_actions": len(buffer),
            "generated_at": datetime.now().isoformat(),
            "actions": buffer,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        return file_path

    @classmethod
    def generate_html_timeline(cls, test_id: str = None) -> str:
        """
        Generates an interactive, modern HTML Action Timeline card styled
        specifically for Allure Report attachments.
        """
        tid = test_id or getattr(_local, "test_id", "UnknownTest")
        buffer = cls._get_buffer()
        if not buffer:
            return "<div style='font-family: sans-serif; padding: 12px;'>No action traces recorded.</div>"

        total_actions = len(buffer)
        total_time_ms = sum(item.get("duration_ms", 0) for item in buffer)

        rows_html = ""
        for item in buffer:
            status = item["status"]
            badge_color = "#10b981" if status == "PASS" else ("#ef4444" if status in ("FAIL", "ERROR") else "#f59e0b")
            bg_color = "rgba(16, 185, 129, 0.08)" if status == "PASS" else ("rgba(239, 68, 68, 0.08)" if status in ("FAIL", "ERROR") else "rgba(245, 158, 11, 0.08)")
            
            dur_text = f"{item['duration_ms']} ms" if item["duration_ms"] > 0 else "< 1 ms"

            rows_html += f"""
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.06); transition: background 0.15s ease;">
              <td style="padding: 10px 12px; font-weight: 700; color: #94a3b8; font-family: monospace;">#{item['step']:02d}</td>
              <td style="padding: 10px 12px; font-family: monospace; color: #cbd5e1; font-size: 0.85rem;">{item['timestamp']}</td>
              <td style="padding: 10px 12px;">
                <span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 800; background: #3b82f6; color: white; letter-spacing: 0.5px;">
                  {item['action']}
                </span>
              </td>
              <td style="padding: 10px 12px; font-weight: 600; color: #f1f5f9;">{item['page']}</td>
              <td style="padding: 10px 12px; color: #94a3b8; font-size: 0.88rem;">
                <div style="color: #e2e8f0; font-weight: 500;">{item['element']}</div>
                {f"<div style='font-family: monospace; font-size: 0.75rem; color: #64748b; margin-top: 2px;'>{item['locator']}</div>" if item['locator'] else ""}
              </td>
              <td style="padding: 10px 12px; text-align: right; font-family: monospace; color: #38bdf8; font-weight: 600; font-size: 0.85rem;">{dur_text}</td>
              <td style="padding: 10px 12px; text-align: center;">
                <span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 800; background: {badge_color}; color: white;">
                  {status}
                </span>
              </td>
            </tr>
            """

        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; border-radius: 8px; padding: 18px; border: 1px solid #1e293b; max-width: 1000px; margin: 0 auto;">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 14px; margin-bottom: 14px;">
            <div>
              <span style="font-size: 0.75rem; font-weight: 800; letter-spacing: 1px; color: #38bdf8; text-transform: uppercase;">Time-Travel Action Tracing</span>
              <h2 style="margin: 4px 0 0; font-size: 1.25rem; font-weight: 700; color: #ffffff;">{tid} — Flight Recorder Timeline</h2>
            </div>
            <div style="display: flex; gap: 14px; text-align: right;">
              <div style="background: #1e293b; padding: 6px 12px; border-radius: 6px;">
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Total Acciones</div>
                <div style="font-size: 1.1rem; font-weight: 800; color: #38bdf8;">{total_actions}</div>
              </div>
              <div style="background: #1e293b; padding: 6px 12px; border-radius: 6px;">
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Tiempo UI Acumulado</div>
                <div style="font-size: 1.1rem; font-weight: 800; color: #10b981;">{total_time_ms:.1f} ms</div>
              </div>
            </div>
          </div>

          <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem;">
              <thead>
                <tr style="border-bottom: 2px solid #334155; color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">
                  <th style="padding: 8px 12px;">Paso</th>
                  <th style="padding: 8px 12px;">Hora</th>
                  <th style="padding: 8px 12px;">Acción</th>
                  <th style="padding: 8px 12px;">Página</th>
                  <th style="padding: 8px 12px;">Elemento / Localizador</th>
                  <th style="padding: 8px 12px; text-align: right;">Duración</th>
                  <th style="padding: 8px 12px; text-align: center;">Estado</th>
                </tr>
              </thead>
              <tbody>
                {rows_html}
              </tbody>
            </table>
          </div>
        </div>
        """
        return html

