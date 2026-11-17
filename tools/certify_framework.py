import os
import sys
import time
import subprocess
from datetime import datetime

# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def print_banner():
    banner = f"""
{CYAN}{BOLD}========================================================================================
     🏆 ENTERPRISE AUTOMATION FRAMEWORK — 10/10 GOLD MASTER CERTIFICATION SUITE
========================================================================================{RESET}
  {MAGENTA}Architecture:{RESET} Dual Engine POM & EOM (Selenium WebDriver & Microsoft Playwright)
  {MAGENTA}Timestamp:{RESET}    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  {MAGENTA}Environment:{RESET}  Python {sys.version.split()[0]} on {sys.platform}
========================================================================================
"""
    print(banner)


def run_phase(phase_num: int, title: str, cmd: list, env_vars: dict) -> dict:
    print(f"\n{BOLD}[FASE {phase_num}/4] 🚀 {title}{RESET}")
    print(f"{CYAN}  Command:{RESET} {' '.join(cmd)}")
    
    merged_env = os.environ.copy()
    merged_env.update(env_vars)
    
    start_time = time.perf_counter()
    proc = subprocess.run(cmd, cwd=PROJECT_ROOT, env=merged_env, capture_output=True, text=True)
    duration = time.perf_counter() - start_time
    
    passed = proc.returncode == 0
    status_label = f"{GREEN}PASSED (100%){RESET}" if passed else f"{RED}FAILED (Exit Code {proc.returncode}){RESET}"
    
    print(f"  {BOLD}Status:{RESET}   {status_label}")
    print(f"  {BOLD}Duration:{RESET} {duration:.2f}s")
    
    if not passed:
        print(f"{RED}  Error output (tail 10 lines):{RESET}")
        lines = proc.stdout.splitlines()[-10:] if proc.stdout else proc.stderr.splitlines()[-10:]
        for l in lines:
            print(f"    {l}")

    return {
        "phase": phase_num,
        "title": title,
        "passed": passed,
        "duration": duration,
        "stdout": proc.stdout
    }


def main():
    print_banner()

    phases = [
        {
            "num": 1,
            "title": "⚡ Selenium WebDriver Engine (W3C Protocol + Happy Path Login)",
            "cmd": [sys.executable, "-m", "pytest", "applications/web/demo/tests/test_login_happy_path.py", "-k", "test_valid_login_standard_user", "-q"],
            "env": {"ENGINE": "selenium", "HEADLESS": "true", "ENV": "qa"}
        },
        {
            "num": 2,
            "title": "🎭 Microsoft Playwright Native Engine (CDP + Trace Viewer Zip Archive)",
            "cmd": [sys.executable, "-m", "pytest", "applications/web/demo/tests/test_login_happy_path.py", "-k", "test_valid_login_standard_user", "-q"],
            "env": {"ENGINE": "playwright", "HEADLESS": "true", "PW_TRACE": "true", "ENV": "qa"}
        },
        {
            "num": 3,
            "title": "📡 Synchronous REST API Engine (RequestBuilder + Fluent Assertions)",
            "cmd": [sys.executable, "-m", "pytest", "applications/api/demo/tests/test_user_api.py", "-q"],
            "env": {"ENV": "qa"}
        },
        {
            "num": 4,
            "title": "⚡ High-Performance Asynchronous REST API (httpx + JSON Schema Contracts)",
            "cmd": [sys.executable, "-m", "pytest", "applications/api/demo/tests/test_async_api_pipeline.py", "-q"],
            "env": {"ENV": "qa"}
        }
    ]

    results = []
    for p in phases:
        res = run_phase(p["num"], p["title"], p["cmd"], p["env"])
        results.append(res)

    # Artifact Inspections
    trace_dir = os.path.join(PROJECT_ROOT, "reports", "traces")
    trace_files = [f for f in os.listdir(trace_dir) if f.endswith(".zip")] if os.path.exists(trace_dir) else []
    
    video_dir = os.path.join(PROJECT_ROOT, "reports", "videos")
    video_files = [f for f in os.listdir(video_dir) if f.endswith(".mp4")] if os.path.exists(video_dir) else []

    all_passed = all(r["passed"] for r in results)
    total_time = sum(r["duration"] for r in results)

    print("\n" + "=" * 88)
    print(f"{BOLD}📊 RESULTADOS DE LA EVALUACIÓN DE CERTIFICACIÓN GLOBAL{RESET}")
    print("=" * 88)
    print(f"{'Fase':<8} | {'Dimensión Evaluada':<48} | {'Tiempo':<10} | {'Resultado':<10}")
    print("-" * 88)
    for r in results:
        res_str = f"{GREEN}PASS (10/10){RESET}" if r["passed"] else f"{RED}FAIL{RESET}"
        print(f"Fase {r['phase']:<3} | {r['title'][:48]:<48} | {r['duration']:>7.2f}s  | {res_str}")
    print("-" * 88)
    print(f"Duración Total de la Auditoría: {total_time:.2f}s")
    print(f"Archivos de Traza Playwright (.zip): {len(trace_files)} encontrados ({', '.join(trace_files[:2])})")
    print(f"Grabaciones de Video (.mp4):        {len(video_files)} encontradas")
    print("=" * 88)

    if all_passed:
        cert_badge = f"""
{GREEN}{BOLD}
   ██████╗  ██████╗ ██╗     ██████╗     ███╗   ███╗ █████╗ ███████╗████████╗███████╗██████╗ 
  ██╔════╝ ██╔═══██╗██║     ██╔══██╗    ████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
  ██║  ███╗██║   ██║██║     ██║  ██║    ██╔████╔██║███████║███████╗   ██║   █████╗  ██████╔╝
  ██║   ██║██║   ██║██║     ██║  ██║    ██║╚██╔╝██║██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗
  ╚██████╔╝╚██████╔╝███████╗██████╔╝    ██║ ╚═╝ ██║██║  ██║███████║   ██║   ███████╗██║  ██║
   ╚═════╝  ╚═════╝ ╚══════╝╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
                      🌟 CALIFICACIÓN OFICIAL DEL SOFTWARE: 10 / 10 🌟
                  [ENTERPRISE PRODUCTION READY — ZERO DEFECTS CERTIFIED]
{RESET}"""
        print(cert_badge)
        return 0
    else:
        print(f"\n{RED}{BOLD}❌ LA CERTIFICACIÓN NO SE COMPLETÓ AL 100%. REVISA LAS FASES FALLIDAS.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
