import os
import subprocess
import json
import ast
import re
import cv2
from datetime import datetime
import requests
from urllib.parse import urljoin, urlparse
from flask import Flask, render_template, request, Response, jsonify, send_from_directory, make_response, redirect
import sys

app = Flask(__name__)
active_process = None

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Absolute path to the root of the automation framework
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
PLANS_DIR = os.path.join(PROJECT_ROOT, "tools", "test_runner", "plans")

# Add PROJECT_ROOT and tools directory to sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "tools"))
import scaffold

if not os.path.exists(PLANS_DIR):
    os.makedirs(PLANS_DIR)

def extract_metadata(file_path, test_method_name):
    """Extracts metadata (id, title, description) from a test method using AST."""
    metadata = {"id": None, "title": test_method_name, "description": ""}
    try:
        normalized_path = file_path.replace("/", os.sep).replace("\\", os.sep)
        abs_path = os.path.join(PROJECT_ROOT, normalized_path)
        if not os.path.exists(abs_path): return metadata
        with open(abs_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == test_method_name:
                metadata["description"] = ast.get_docstring(node) or ""
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and getattr(decorator.func, 'id', '') == 'test_case':
                        for kw in decorator.keywords:
                            if kw.arg == 'id' and isinstance(kw.value, ast.Constant):
                                metadata["id"] = kw.value.value
                                break
    except Exception: pass
    return metadata

@app.route("/")
def index():
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/docs")
def docs_redirect():
    return redirect("/docs/")

@app.route("/docs/")
@app.route("/docs/<path:filename>")
def serve_docs(filename="index.html"):
    docs_dir = os.path.join(PROJECT_ROOT, "docs")
    if not filename or filename.endswith("/"):
        filename += "index.html"
    response = make_response(send_from_directory(docs_dir, filename))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Automation Sandbox Routes (Health Check)
@app.route("/sandbox", strict_slashes=False)
def serve_sandbox():
    response = make_response(render_template("sandbox.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/sandbox/iframe", strict_slashes=False)
def serve_sandbox_iframe():
    response = make_response(render_template("sandbox_iframe.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route("/sandbox/newtab", strict_slashes=False)
def serve_sandbox_newtab():
    response = make_response(render_template("sandbox_newtab.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route("/sandbox/download/sample.csv", strict_slashes=False)
def serve_sandbox_download():
    content = "id,name,role,status\n101,Alice Smith,Admin,ACTIVE\n102,Bob Jones,Viewer,ACTIVE\n103,Charlie Brown,Editor,PENDING\n"
    response = make_response(content)
    response.headers["Content-Disposition"] = "attachment; filename=sandbox_report.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

import yaml

@app.route("/api/apps", strict_slashes=False)
def list_apps():
    apps = []
    # Folders to ignore
    ignore = ["__pycache__", ".pytest_cache", ".venv", "common", "shared", "__init__.py"]
    
    for app_type in ["web", "api"]:
        apps_dir = os.path.join(PROJECT_ROOT, "applications", app_type)
        if not os.path.exists(apps_dir):
            continue
            
        for d in os.listdir(apps_dir):
            if d in ignore or not os.path.isdir(os.path.join(apps_dir, d)):
                continue
                
            app_info = {
                "name": f"[{app_type.upper()}] {d.replace('_', ' ').title()}",
                "folder": d,
                "type": app_type,
                "path": f"applications/{app_type}/{d}/tests",
                "environments": {}
            }
            
            # Scan all environments for this app
            env_dir = os.path.join(apps_dir, d, "config", "environments")
            if os.path.exists(env_dir):
                for env_file in os.listdir(env_dir):
                    if env_file.endswith(".yaml") or env_file.endswith(".yml"):
                        env_name = os.path.splitext(env_file)[0]
                        try:
                            with open(os.path.join(env_dir, env_file), "r") as f:
                                cfg = yaml.safe_load(f)
                                if not cfg: continue
                                
                                # Detect URL based on app type
                                url = None
                                if app_type == "web" and "web" in cfg:
                                    url = cfg["web"].get("base_url")
                                elif app_type == "api" and "api" in cfg:
                                    url = cfg["api"].get("base_url")
                                
                                if url:
                                    app_info["environments"][env_name] = url
                        except Exception:
                            pass
            
            # Fallback if no specific environments found
            if not app_info["environments"]:
                app_info["environments"]["qa"] = "https://example.com"
                
            apps.append(app_info)
            
    return jsonify({"status": "success", "apps": apps})

def get_test_data(file_path, test_id):
    """
    Looks for the <test_id>.json file under applications/<mode>/<app>/data/<env>/
    and returns the contents of the 'data' key as a dict.
    """
    if not test_id:
        return None
    try:
        parts = file_path.replace("\\", "/").split("/")
        if len(parts) >= 3:
            app_type = parts[1] # web or api
            app_name = parts[2] # busisness_partners_portal or other
            env = request.args.get("env", "qa")
            data_file = os.path.join(PROJECT_ROOT, "applications", app_type, app_name, "data", env, f"{test_id}.json")
            if os.path.exists(data_file):
                with open(data_file, "r", encoding="utf-8") as f:
                    data_json = json.load(f)
                    return data_json.get("tests", {}).get("data", {})
    except Exception:
        pass
    return None

@app.route("/api/tests")
def list_tests():
    app_path = request.args.get("app_path", "applications/web/demo/tests")
    full_path = os.path.join(PROJECT_ROOT, app_path)
    files_tree = {}
    
    if os.path.exists(full_path):
        for root, _, files in os.walk(full_path):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT).replace("\\", "/")
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                        classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
                        
                        file_tests = []
                        for cls in classes:
                            methods = [n.name for n in cls.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
                            for m in methods:
                                meta = extract_metadata(rel_path, m)
                                test_data = get_test_data(rel_path, meta.get("id"))
                                file_tests.append({
                                    "id": f"{rel_path}::{cls.name}::{m}",
                                    "name": m,
                                    "class": cls.name,
                                    "file": rel_path,
                                    "test_id": meta.get("id"),
                                    "title": meta.get("title"),
                                    "description": meta.get("description"),
                                    "test_data": test_data
                                })
                        
                        if file_tests:
                            display_name = os.path.basename(rel_path)
                            files_tree[display_name] = file_tests
                            
    return jsonify({"status": "success", "files": files_tree})

@app.route("/api/plans", methods=["GET", "POST", "DELETE"])
def manage_plans():
    if request.method == "POST":
        data = request.json
        name = data.get("name", f"Plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        file_path = os.path.join(PLANS_DIR, f"{name}.json")
        with open(file_path, "w") as f:
            json.dump(data, f)
        return jsonify({"status": "success", "message": "Plan saved"})
    
    if request.method == "DELETE":
        name = request.args.get("name")
        file_path = os.path.join(PLANS_DIR, f"{name}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"status": "success", "message": "Plan deleted"})
        return jsonify({"status": "error", "message": "Plan not found"}), 404

    plans = []
    if os.path.exists(PLANS_DIR):
        for f in os.listdir(PLANS_DIR):
            if f.endswith(".json"):
                with open(os.path.join(PLANS_DIR, f), "r") as json_file:
                    plans.append(json.load(json_file))
    return jsonify({"status": "success", "plans": plans})

@app.route("/api/media", methods=["DELETE"])
def delete_media():
    path = request.args.get("path")
    full_path = os.path.join(PROJECT_ROOT, path)
    if os.path.exists(full_path):
        os.remove(full_path)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "File not found"}), 404

def get_all_tests_catalog():
    """Builds a lookup table of test_method_name -> metadata across all tests in applications/."""
    catalog = {}
    apps_root = os.path.join(PROJECT_ROOT, "applications")
    if os.path.exists(apps_root):
        for root, _, files in os.walk(apps_root):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT).replace("\\", "/")
                    base_name = os.path.basename(file)
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            tree = ast.parse(f.read())
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                                    meta = extract_metadata(rel_path, node.name)
                                    catalog[node.name] = {
                                        "file": base_name,
                                        "suite": base_name,
                                        "rel_path": rel_path,
                                        "test_id": meta.get("id") or "",
                                        "title": meta.get("title") or node.name.replace("_", " ").title(),
                                        "description": meta.get("description") or ""
                                    }
                    except Exception:
                        pass
    return catalog

def get_video_duration_str(file_path):
    """Calculates video duration in mm:ss using OpenCV."""
    try:
        cap = cv2.VideoCapture(file_path)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            if fps and fps > 0:
                duration_sec = int(frame_count / fps)
                mins = duration_sec // 60
                secs = duration_sec % 60
                return f"{mins:02d}:{secs:02d}"
    except Exception:
        pass
    return "00:00"

def find_test_json(test_id):
    """Finds and parses the <test_id>.json file anywhere under applications/."""
    if not test_id:
        return None
    for root, _, files in os.walk(os.path.join(PROJECT_ROOT, "applications")):
        if f"{test_id}.json" in files:
            try:
                with open(os.path.join(root, f"{test_id}.json"), "r", encoding="utf-8") as jf:
                    data = json.load(jf)
                    return data.get("tests", data)
            except Exception:
                pass
    return None

@app.route("/api/test/metadata")
def get_test_metadata():
    test_id = request.args.get("test_id", "")
    metadata = find_test_json(test_id)
    if metadata:
        return jsonify({"status": "success", "metadata": metadata})
    return jsonify({"status": "error", "message": "Metadata not found"}), 404

@app.route("/api/reports/list")
def list_reports():
    catalog = get_all_tests_catalog()
    media = []
    
    video_dir = os.path.join(REPORTS_DIR, "videos")
    if os.path.exists(video_dir):
        for f in os.listdir(video_dir):
            if f.endswith(".mp4") or f.endswith(".avi"):
                file_path = os.path.join(video_dir, f)
                base_name = os.path.splitext(f)[0]
                method_name = re.sub(r'_\d{8}_\d{6}$', '', base_name)
                match = catalog.get(method_name, {})
                
                test_id = match.get("test_id", "")
                suite_file = match.get("file", "Other Captures")
                test_name = match.get("title") or method_name.replace("_", " ").title()
                
                if not test_id:
                    id_match = re.search(r'(CT-[A-Z0-9-]+|TC\d+|PC-[A-Z0-9-]+|ADV-[A-Z0-9-]+)', f, re.IGNORECASE)
                    if id_match:
                        test_id = id_match.group(1).upper()

                test_meta = find_test_json(test_id)
                if test_meta and test_meta.get("title"):
                    test_name = test_meta.get("title")

                duration = get_video_duration_str(file_path)

                media.append({
                    "type": "video",
                    "path": f"reports/videos/{f}",
                    "name": f,
                    "timestamp": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%I:%M:%S %p"),
                    "testName": test_name,
                    "testId": test_id,
                    "suite": suite_file,
                    "method": method_name,
                    "duration": duration,
                    "metadata": test_meta
                })
    
    screenshot_dir = os.path.join(REPORTS_DIR, "screenshots")
    if os.path.exists(screenshot_dir):
        for f in os.listdir(screenshot_dir):
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                file_path = os.path.join(screenshot_dir, f)
                base_name = os.path.splitext(f)[0]
                method_name = re.sub(r'_\d{8}_\d{6}$', '', base_name)
                match = catalog.get(method_name, {})
                
                test_id = match.get("test_id", "")
                suite_file = match.get("file", "Other Captures")
                test_name = match.get("title") or method_name.replace("_", " ").title()

                if not test_id:
                    id_match = re.search(r'(CT-[A-Z0-9-]+|TC\d+|PC-[A-Z0-9-]+|ADV-[A-Z0-9-]+)', f, re.IGNORECASE)
                    if id_match:
                        test_id = id_match.group(1).upper()

                test_meta = find_test_json(test_id)
                if test_meta and test_meta.get("title"):
                    test_name = test_meta.get("title")

                media.append({
                    "type": "screenshot",
                    "path": f"reports/screenshots/{f}",
                    "name": f,
                    "timestamp": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%I:%M:%S %p"),
                    "testName": test_name,
                    "testId": test_id,
                    "suite": suite_file,
                    "method": method_name,
                    "metadata": test_meta
                })

    # Include Playwright Trace Archives (.zip)
    trace_dir = os.path.join(REPORTS_DIR, "traces")
    if os.path.exists(trace_dir):
        for f in os.listdir(trace_dir):
            if f.endswith(".zip"):
                file_path = os.path.join(trace_dir, f)
                base_name = os.path.splitext(f)[0]
                method_name = re.sub(r'_trace$', '', base_name)
                match = catalog.get(method_name, {})
                test_id = match.get("test_id", "")
                suite_file = match.get("file", "Playwright Trace")
                test_name = match.get("title") or method_name.replace("_", " ").title()

                if not test_id:
                    id_match = re.search(r'(CT-[A-Z0-9-]+|TC\d+|PC-[A-Z0-9-]+|ADV-[A-Z0-9-]+)', f, re.IGNORECASE)
                    if id_match:
                        test_id = id_match.group(1).upper()

                test_meta = find_test_json(test_id)
                if test_meta and test_meta.get("title"):
                    test_name = test_meta.get("title")

                size_kb = os.path.getsize(file_path) // 1024
                media.append({
                    "type": "trace",
                    "path": f"reports/traces/{f}",
                    "name": f,
                    "timestamp": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%I:%M:%S %p"),
                    "testName": f"🎭 Playwright Trace ({test_id})",
                    "testId": test_id,
                    "suite": suite_file,
                    "method": method_name,
                    "duration": f"{size_kb} KB",
                    "metadata": test_meta
                })
    
    media.sort(key=lambda x: os.path.getmtime(os.path.join(PROJECT_ROOT, x["path"])), reverse=True)
    return jsonify({"status": "success", "media": media})

@app.route("/api/traces/open", methods=["POST"])
def open_trace_viewer():
    """Launches Playwright show-trace in background for the specified zip or the latest one."""
    data = request.get_json(silent=True) or {}
    trace_file = data.get("trace_file")
    trace_dir = os.path.join(REPORTS_DIR, "traces")

    if not os.path.exists(trace_dir):
        return jsonify({"status": "error", "message": "No traces directory found."}), 404

    target_path = None
    if trace_file:
        candidate = os.path.join(PROJECT_ROOT, trace_file) if not os.path.isabs(trace_file) else trace_file
        if os.path.exists(candidate):
            target_path = candidate
        else:
            candidate2 = os.path.join(trace_dir, os.path.basename(trace_file))
            if os.path.exists(candidate2):
                target_path = candidate2

    if not target_path:
        zip_files = [os.path.join(trace_dir, f) for f in os.listdir(trace_dir) if f.endswith(".zip")]
        if zip_files:
            zip_files.sort(key=os.path.getmtime, reverse=True)
            target_path = zip_files[0]

    if not target_path:
        return jsonify({"status": "error", "message": "No trace archives (.zip) found in reports/traces/"}), 404

    try:
        subprocess.Popen(["playwright", "show-trace", target_path], shell=True)
        return jsonify({
            "status": "success",
            "message": f"Launched Playwright Trace Viewer for {os.path.basename(target_path)}",
            "trace": os.path.basename(target_path)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Could not launch Playwright Trace Viewer: {e}"}), 500

@app.route("/api/allure-results")
def get_allure_results():
    results = []
    allure_dir = os.path.join(REPORTS_DIR, "allure-results")
    if os.path.exists(allure_dir):
        for f in os.listdir(allure_dir):
            if f.endswith("-result.json"):
                try:
                    with open(os.path.join(allure_dir, f), "r", encoding="utf-8") as file:
                        data = json.load(file)
                        results.append(data)
                except Exception:
                    pass
    return jsonify({"status": "success", "results": results})

@app.route("/api/diagnostics", strict_slashes=False)
def list_diagnostics():
    """Returns all available failure diagnostics."""
    diag_dir = os.path.join(REPORTS_DIR, "diagnostics")
    diagnostics = []
    if os.path.exists(diag_dir):
        for f in os.listdir(diag_dir):
            if f.endswith("_diagnostic.json"):
                try:
                    with open(os.path.join(diag_dir, f), "r", encoding="utf-8") as file:
                        diagnostics.append(json.load(file))
                except Exception:
                    pass
    return jsonify({"status": "success", "diagnostics": diagnostics})

@app.route("/api/diagnostics/<test_id>")
def get_test_diagnostic(test_id):
    """Fetches root-cause failure diagnostic for a specific test ID."""
    diag_dir = os.path.join(REPORTS_DIR, "diagnostics")
    if not os.path.exists(diag_dir):
        return jsonify({"status": "error", "message": "No diagnostics directory found"}), 404

    test_slug = test_id.replace(" ", "_")
    target_file = os.path.join(diag_dir, f"{test_slug}_diagnostic.json")
    if not os.path.exists(target_file):
        for f in os.listdir(diag_dir):
            if test_slug.lower() in f.lower() and f.endswith("_diagnostic.json"):
                target_file = os.path.join(diag_dir, f)
                break

    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify({"status": "success", "diagnostic": data})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "error", "message": f"Diagnostic for '{test_id}' not found"}), 404

@app.route("/api/traces/<test_id>")
def get_test_trace(test_id):
    """Fetches action trace JSON for a specific test ID."""
    trace_dir = os.path.join(REPORTS_DIR, "traces")
    if not os.path.exists(trace_dir):
        return jsonify({"status": "error", "message": "No traces directory found"}), 404

    test_slug = test_id.replace(" ", "_")
    target_file = os.path.join(trace_dir, f"{test_slug}_trace.json")
    if not os.path.exists(target_file):
        for f in os.listdir(trace_dir):
            if test_slug.lower() in f.lower() and f.endswith("_trace.json"):
                target_file = os.path.join(trace_dir, f)
                break

    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify({"status": "success", "trace": data})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "error", "message": f"Trace for '{test_id}' not found"}), 404

@app.route("/api/traces/<test_id>/html")
def get_test_trace_html(test_id):
    """Renders the HTML Flight Recorder Timeline card directly in the browser."""
    from core.utils.action_tracer import ActionTracer
    trace_dir = os.path.join(REPORTS_DIR, "traces")
    target_file = os.path.join(trace_dir, f"{test_id}_trace.json")
    if not os.path.exists(target_file):
        for f in os.listdir(trace_dir) if os.path.exists(trace_dir) else []:
            if test_id.lower() in f.lower() and f.endswith("_trace.json"):
                target_file = os.path.join(trace_dir, f)
                break

    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            ActionTracer.start_trace(test_id)
            for act in data.get("actions", []):
                ActionTracer.record_action(
                    action=act.get("action", ""),
                    page=act.get("page", ""),
                    element=act.get("element", ""),
                    locator=act.get("locator", ""),
                    duration_ms=act.get("duration_ms", 0),
                    status=act.get("status", "PASS"),
                    details=act.get("details", "")
                )
            html_card = ActionTracer.generate_html_timeline(test_id)
            page_wrap = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Time-Travel Action Timeline — {test_id}</title>
    <style>body {{ background: #090d16; margin: 0; padding: 24px; }}</style>
</head>
<body>
    {html_card}
</body>
</html>"""
            return page_wrap
        except Exception as e:
            return f"<h3>Error rendering trace: {e}</h3>", 500

    return f"<h3>No trace found for test '{test_id}'</h3>", 404

@app.route("/api/report/generate", methods=["POST"])
def generate_report():
    try:
        allure_results = os.path.join(REPORTS_DIR, "allure-results")
        allure_report = os.path.join(REPORTS_DIR, "allure-report")
        if not os.path.exists(allure_results):
            return jsonify({"status": "error", "message": "No allure results found. Run tests first."}), 400
        cmd = ["npx", "allure-commandline", "generate", allure_results, "-o", allure_report, "--clean"]
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"status": "error", "message": f"Failed: {result.stderr}"}), 500
        return jsonify({"status": "success", "url": "/reports/allure-report/index.html"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/reports/<path:filename>")
def serve_reports(filename):
    return send_from_directory(REPORTS_DIR, filename)

@app.route("/api/run", methods=["POST"])
def run_test():
    data = request.json
    test_ids = data.get("test_id", "applications/web/demo/tests")
    engine = data.get("engine", "selenium")
    browser = data.get("browser", "chrome")
    env_name = data.get("env", "qa")
    headless = bool(data.get("headless", False))
    video = data.get("video", False)
    
    print(f"DEBUG /api/run received: engine={engine}, browser={browser}, headless={headless}, video={video}")
    
    def generate_output():
        global active_process
        env_vars = os.environ.copy()
        env_vars.update({
            "ENGINE": engine,
            "BROWSER": browser,
            "ENV": env_name,
            "HEADLESS": "true" if headless else "false",
            "VIDEO_ENABLED": "true" if video else "false",
            "PYTHONPATH": PROJECT_ROOT,
            "PYTHONIOENCODING": "utf-8"
        })
        cmd = ["pytest", "-v", "--no-header", "--show-capture=no", "--alluredir=reports/allure-results", "--clean-alluredir", "-o", "log_cli=true", "-o", "log_cli_level=INFO"]
        if isinstance(test_ids, list): cmd.extend(test_ids)
        else: cmd.append(test_ids)
        
        process = None
        try:
            # On Windows, ensure interactive desktop flags so child processes (Chrome/Playwright)
            # are allowed to spawn visible GUI windows on the user's interactive desktop.
            startupinfo = None
            creationflags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 1  # SW_SHOWNORMAL

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=PROJECT_ROOT,
                env=env_vars,
                text=True,
                encoding="utf-8",
                bufsize=1,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            active_process = process
            yield f"data: {json.dumps({'type': 'start', 'message': 'Running pytest...'})}\n\n"
            for line in iter(process.stdout.readline, ""):
                if line: yield f"data: {json.dumps({'type': 'log', 'message': line.strip()})}\n\n"
            
            process.stdout.close()
            return_code = process.wait()
            yield f"data: {json.dumps({'type': 'end', 'status': 'DONE', 'code': return_code})}\n\n"
        except GeneratorExit:
            if process and process.poll() is None:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], capture_output=True)
                else:
                    process.terminate()
                    process.wait()
        finally:
            if active_process == process:
                active_process = None

    return Response(generate_output(), mimetype="text/event-stream")

@app.route("/api/stop", methods=["POST"])
def stop_test():
    global active_process
    if active_process and active_process.poll() is None:
        try:
            if os.name == 'nt':
                # Forcefully kill the process tree on Windows to clean up pytest and webdriver/browsers
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(active_process.pid)], capture_output=True)
            else:
                active_process.terminate()
            active_process.wait(timeout=3)
            active_process = None
            return jsonify({"status": "success", "message": "Test execution stopped successfully."})
        except subprocess.TimeoutExpired:
            if os.name == 'nt':
                pass
            else:
                active_process.kill()
            active_process = None
            return jsonify({"status": "success", "message": "Test execution force killed."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "No active test execution found."}), 400

# --- PAGE INSPECTOR ASSISTANT ---

@app.route("/inspector", strict_slashes=False)
@app.route("/assistant-v3", strict_slashes=False)
def assistant_v3_view():
    print("Serving FRESH Assistant V3 template...")
    resp = make_response(render_template("assistant_v3.html"))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

ACTIVE_INSPECTION_ORIGIN = None

import traceback

def perform_proxy(url):
    """Core proxy logic - acts as a transparent tunnel for all HTTP methods and sessions."""
    global ACTIVE_INSPECTION_ORIGIN
    
    if not url.startswith("http"): url = "http://" + url
    
    try:
        # 1. Forward headers from browser to target
        excluded_req = ['host', 'content-length', 'connection']
        headers = {k: v for k, v in request.headers.items() if k.lower() not in excluded_req}
        
        # Rewrite Referer and Origin to match target
        parsed_target = urlparse(url)
        target_origin = f"{parsed_target.scheme}://{parsed_target.netloc}"
        
        if 'Referer' in headers:
            # Keep the path but swap the domain
            u = urlparse(headers['Referer'])
            headers['Referer'] = urljoin(target_origin, u.path + ("?" + u.query if u.query else ""))
        if 'Origin' in headers:
            headers['Origin'] = target_origin
            
        print(f"Tunneling [{request.method}]: {url}")
        
        # 2. Forward request body
        data = request.get_data()
        
        # 3. Execute request
        resp = requests.request(
            method=request.method,
            url=url,
            data=data,
            headers=headers,
            timeout=30,
            verify=False,
            allow_redirects=False # We handle redirects manually for transparency
        )
        
        # Capture origin for session tracking
        parsed_resp = urlparse(resp.url)
        origin = f"{parsed_resp.scheme}://{parsed_resp.netloc}"
        if "api/proxy" in request.path:
            ACTIVE_INSPECTION_ORIGIN = origin
        
        # 4. Prepare response headers
        excluded_resp = [
            "content-security-policy", "x-frame-options", 
            "content-encoding", "transfer-encoding", "connection",
            "strict-transport-security"
        ]
        
        # Use a list of tuples to allow multiple Set-Cookie headers
        resp_headers = []
        for name, value in resp.raw.headers.items():
            if name.lower() not in excluded_resp:
                resp_headers.append((name, value))
        
        # Ensure CORS is permissive
        resp_headers.append(("Access-Control-Allow-Origin", "*"))
        resp_headers.append(("Access-Control-Allow-Credentials", "true"))
        
        # 5. Handle Content
        ctype = resp.headers.get("Content-Type", "").lower()
        
        # HTML Rewriting (Only for the main page)
        if "text/html" in ctype and "api/proxy" in request.path:
            content = resp.text
            proxy_prefix = f"{request.host_url.rstrip('/')}/api/proxy?url="
            
            # Rewrite all absolute paths to go through proxy
            content = content.replace('src="/', f'src="{proxy_prefix}{origin}/')
            content = content.replace('href="/', f'href="{proxy_prefix}{origin}/')
            content = content.replace('action="/', f'action="{proxy_prefix}{origin}/')
            content = content.replace('srcset="/', f'srcset="{proxy_prefix}{origin}/')
            
            # CSS patterns
            content = content.replace('url(/', f'url({proxy_prefix}{origin}/')
            content = content.replace('url("/', f'url("{proxy_prefix}{origin}/')
            content = content.replace("url('/", f"url('{proxy_prefix}{origin}/")
            
            # Injected script to fix missing assets in JS
            injection = f"""
            <script id="proxy-fix">
                window.__PROXY_ORIGIN__ = "{origin}";
                console.log("Assistant: Proxy active for {origin}");
            </script>
            """
            content = content.replace("<head>", "<head>" + injection)
            
            return Response(content, resp.status_code, resp_headers)
        
        # Transparent pass-through for assets/data
        return Response(resp.content, resp.status_code, resp_headers)

    except Exception as e:
        print(f"--- PROXY ERROR ---")
        traceback.print_exc()
        return f"Proxy Error: {str(e)}", 500

@app.route("/api/assistant/scaffold", methods=["POST"])
def scaffold_from_inspect():
    data = request.json
    app_name, page_name, subfolder, elements = data.get("app"), data.get("name"), data.get("subfolder", ""), data.get("elements", [])
    if not app_name or not page_name: return jsonify({"status": "error", "message": "Missing info"}), 400
    try:
        locators, methods = [], []
        for el in elements:
            # Use 'variableName' which is what inspector.html sends
            v_name = el.get("variableName", "ELEMENT").upper()
            l_type, l_val = el["locator_type"], el["locator_value"]
            
            locators.append(f"    {v_name} = (By.{l_type.upper()}, \"{l_val}\")")
            m_name = v_name.lower()
            if v_name.startswith("BTN_"): 
                methods.append(f"    def click_{m_name[4:]}(self):\n        self.element(self.{v_name}).click()\n        return self")
            elif v_name.startswith("INP_"): 
                methods.append(f"    def fill_{m_name[4:]}(self, value):\n        self.element(self.{v_name}).send_keys(value)\n        return self")
            elif v_name.startswith("LNK_"): 
                methods.append(f"    def navigate_to_{m_name[4:]}(self):\n        self.element(self.{v_name}).click()\n        return self")
            else: 
                methods.append(f"    def get_{m_name}(self):\n        return self.element(self.{v_name}).text")
        
        # Load template
        tmpl_path = os.path.join(PROJECT_ROOT, "templates", "page_object.tmpl")
        if not os.path.exists(tmpl_path):
            # Fallback inline template if file missing
            tmpl = """from selenium.webdriver.common.by import By\nfrom applications.web.common.base_page import BasePage\n\nclass {{ class_name }}(BasePage):\n    # Locators\n# EXAMPLE_BUTTON = (By.ID, \"example-id\")\n\n    # Actions\n# def click_example_button(self):\n    #     self.element(self.EXAMPLE_BUTTON).click()\n    #     return self\n"""
        else:
            with open(tmpl_path, "r") as f: tmpl = f.read()
            
        content = tmpl.replace("{{ class_name }}", page_name)
        content = content.replace("# EXAMPLE_BUTTON = (By.ID, \"example-id\")", "\n".join(locators))
        content = content.replace("# def click_example_button(self):\n    #     self.element(self.EXAMPLE_BUTTON).click()\n    #     return self", "\n\n".join(methods))
        
        snake = scaffold.to_snake_case(page_name)
        target_dir = os.path.join(PROJECT_ROOT, f"applications/web/{app_name}/pages", subfolder)
        os.makedirs(target_dir, exist_ok=True)
        f_path = os.path.join(target_dir, f"{snake}.py")
        with open(f_path, "w", encoding="utf-8") as f: f.write(content)
        scaffold.register_page(page_name, app_name, subfolder, snake)
        return jsonify({"status": "success", "message": f"Created: {f_path}"})
    except Exception as e: 
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/proxy", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_route():
    url = request.args.get("url")
    if not url: return "Missing URL", 400
    return perform_proxy(url)
@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def handle_catchall(path=None):
    """Catch all unknown paths and tunnel them to the current target origin."""
    global ACTIVE_INSPECTION_ORIGIN
    
    # ASSISTANT PROTECTION: Never proxy these prefixes
    p = request.path
    if p.startswith("/api/assistant") or p == "/inspector" or p == "/inspector/" or p == "/api/proxy":
        print(f"Direct API Match (Internal): {p}")
        return jsonify({"error": "Internal Route Not Found (404)", "path": p}), 404
        
    if not ACTIVE_INSPECTION_ORIGIN:
        print(f"Proxy Denied: No origin for {p}")
        return jsonify({"error": "No Active Origin Set", "path": p}), 404
        
    full_target_url = urljoin(ACTIVE_INSPECTION_ORIGIN, request.full_path)
    print(f"Tunneling -> {full_target_url}")
    return perform_proxy(full_target_url)

if __name__ == "__main__":
    print(f"Starting Test Runner GUI at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
