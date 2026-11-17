import cv2
import numpy as np
import mss
import threading
import time
import os
import base64
from datetime import datetime
from core.utils.logger_config import setup_logger
from core.utils.config_manager import ConfigManager

class VideoRecorder:
    """
    Dual-Mode Video Recorder for Enterprise UI Observability.
    
    Supports two recording engines:
      1. Desktop MSS Engine: Captures the physical monitor via MSS (ideal for local execution with visible GUI).
      2. Browser CDP Screencast Engine: Captures frames directly from Chromium via Chrome DevTools Protocol (CDP),
         producing pristine .mp4 video inside Docker containers, headless pipelines, or environments without a physical display.
    """
    def __init__(self, name="test_execution", driver=None, mode=None):
        self.logger = setup_logger(self.__class__.__name__)
        self.name = name
        self.driver = driver
        
        # Priority: Environment Variable > Config Manager
        env_enabled = os.getenv("VIDEO_ENABLED", "").lower()
        if env_enabled != "":
            self.enabled = env_enabled == "true"
        else:
            try:
                self.enabled = ConfigManager.get("video.enable_local") or False
            except ValueError:
                self.enabled = True

        try:
            self.fps = ConfigManager.get("video.fps") or 10
            cfg_mode = ConfigManager.get("video.mode") or "auto"
        except ValueError:
            self.fps = 10
            cfg_mode = "auto"

        self.recording = False
        self.thread = None
        self.output_path = ""
        self.out = None

        configured_mode = (mode or cfg_mode).lower()
        if configured_mode == "cdp":
            self.use_cdp = True
        elif configured_mode == "mss":
            self.use_cdp = False
        else:
            self.use_cdp = self._detect_cdp_suitability()

    def _detect_cdp_suitability(self) -> bool:
        """Auto-detects whether CDP Screencast should be preferred over desktop capture."""
        if not self.driver or not hasattr(self.driver, "execute_cdp_cmd"):
            return False
        # In Chrome / Chromium browsers, CDP Screencast captures viewport frames directly
        # from the compositor buffer, guaranteeing crystal-clear video even in background sessions,
        # headless modes, multi-monitor setups, or locked desktops where GDI/MSS returns pitch-black frames.
        return True

    def start(self):
        """Starts the recording in a background thread."""
        if not self.enabled or self.recording:
            return

        self.recording = True
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_dir = os.path.abspath("reports/videos")
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)
            
        self.output_path = os.path.join(video_dir, f"{self.name}_{timestamp}.mp4")
        target_fn = self._record_cdp if self.use_cdp else self._record_mss
        mode_label = "CDP Screencast (Headless/Docker)" if self.use_cdp else "Desktop MSS"
        
        self.thread = threading.Thread(target=target_fn)
        self.thread.start()
        self.logger.info(f"Video recording started ({mode_label}): {self.output_path}")

    def _record_cdp(self):
        """Internal recording loop using Chrome DevTools Protocol Screencast (Headless/Docker)."""
        self.logger.info("Context: Recording via Chrome DevTools Protocol (CDP Screencast)")
        
        # Capture first frame to determine dimensions
        try:
            res = self.driver.execute_cdp_cmd("Page.captureScreenshot", {"format": "jpeg", "quality": 80})
            img_bytes = base64.b64decode(res["data"])
            first_frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
            height, width = first_frame.shape[:2]
            width = (width // 2) * 2
            height = (height // 2) * 2
            self.logger.info(f"CDP Video resolution: {width}x{height} pixels")
        except Exception as e:
            self.logger.warning(f"Failed to capture initial CDP frame: {e}. Falling back to MSS.")
            return self._record_mss()

        if not self.output_path.endswith(".mp4"):
            self.output_path = os.path.splitext(self.output_path)[0] + ".mp4"

        codecs = ['avc1', 'H264', 'X264', 'mp4v', 'XVID']
        for code in codecs:
            try:
                fourcc = cv2.VideoWriter_fourcc(*code)
                test_out = cv2.VideoWriter(self.output_path, fourcc, self.fps, (width, height))
                if test_out.isOpened():
                    self.out = test_out
                    self.logger.info(f"Initialized CDP VideoWriter with codec: '{code}'")
                    break
                else:
                    test_out.release()
            except Exception:
                pass

        if not self.out:
            self.logger.error("CRITICAL: Failed to initialize VideoWriter for CDP screencast.")
            return

        frame_count = 0
        total_capture_time = 0

        while self.recording:
            start_time = time.time()
            try:
                res = self.driver.execute_cdp_cmd("Page.captureScreenshot", {"format": "jpeg", "quality": 75})
                img_bytes = base64.b64decode(res["data"])
                frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
                if frame is not None:
                    if frame.shape[1] != width or frame.shape[0] != height:
                        frame = cv2.resize(frame, (width, height))
                    self.out.write(frame)
                    frame_count += 1
            except Exception:
                break

            capture_duration = time.time() - start_time
            total_capture_time += capture_duration
            sleep_time = (1.0 / self.fps) - capture_duration
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.out.release()
        avg_fps = frame_count / (total_capture_time + 0.001)
        self.logger.info(f"CDP Recording Finished. Total frames: {frame_count}. Avg Capture Speed: {avg_fps:.2f} FPS")

    def _record_mss(self):
        """Internal recording loop using MSS desktop monitor capture."""
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            try:
                sct_instance = mss.mss()
            except Exception as e:
                self.logger.warning(f"MSS initialization failed (no display?): {e}.")
                if self.driver and hasattr(self.driver, "execute_cdp_cmd"):
                    self.logger.info("Retrying recording via CDP Screencast fallback...")
                    return self._record_cdp()
                return

        with sct_instance as sct:
            monitor_index = ConfigManager.get("video.monitor_index") or 0
            if monitor_index >= len(sct.monitors):
                monitor_index = 0
            
            monitor = sct.monitors[monitor_index]
            self.logger.info(f"Context: Recording monitor {monitor_index} (logical: {monitor['width']}x{monitor['height']})")
            
            try:
                first_img = np.array(sct.grab(monitor))
                # Check if captured desktop frame is all black (Session 0 / background runner / locked desktop)
                if np.max(first_img[:, :, :3]) == 0:
                    self.logger.warning("MSS captured an all-black frame (non-interactive desktop/background session).")
                    if self.driver and hasattr(self.driver, "execute_cdp_cmd"):
                        self.logger.info("Auto-switching to Chrome DevTools Protocol (CDP) Screencast for crystal-clear video...")
                        return self._record_cdp()
                height, width = first_img.shape[:2]
                width = (width // 2) * 2
                height = (height // 2) * 2
                self.logger.info(f"Video resolution: {width}x{height} pixels")
            except Exception as e:
                self.logger.error(f"Failed to capture initial frame: {e}")
                return

            if not self.output_path.endswith(".mp4"):
                self.output_path = os.path.splitext(self.output_path)[0] + ".mp4"

            codecs = ['avc1', 'H264', 'X264', 'mp4v', 'XVID']
            for code in codecs:
                try:
                    fourcc = cv2.VideoWriter_fourcc(*code)
                    test_out = cv2.VideoWriter(self.output_path, fourcc, self.fps, (width, height))
                    if test_out.isOpened():
                        self.out = test_out
                        self.logger.info(f"Initialized VideoWriter with codec: '{code}'")
                        break
                    else:
                        test_out.release()
                except Exception:
                    pass

            if not self.out:
                self.logger.error("CRITICAL: Failed to initialize any VideoWriter codec.")
                return

            frame_count = 0
            total_capture_time = 0
            while self.recording:
                start_time = time.time()
                try:
                    sct_img = sct.grab(monitor)
                    img = np.array(sct_img)
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    if frame.shape[1] != width or frame.shape[0] != height:
                        frame = cv2.resize(frame, (width, height))
                    self.out.write(frame)
                    frame_count += 1
                except Exception as e:
                    self.logger.error(f"Error capturing frame: {e}")
                    break
                
                capture_duration = time.time() - start_time
                total_capture_time += capture_duration
                sleep_time = (1.0 / self.fps) - capture_duration
                if sleep_time > 0:
                    time.sleep(sleep_time)

            self.out.release()
            avg_fps = frame_count / (total_capture_time + 0.001)
            self.logger.info(f"Recording Finished. Total frames: {frame_count}. Avg Capture Speed: {avg_fps:.2f} FPS")

    def stop(self):
        """Stops the recording thread."""
        if not self.enabled or not self.recording:
            return

        self.recording = False
        if self.thread:
            self.thread.join()
        
        # Calculate real duration using OpenCV
        duration_str = "00:00"
        try:
            cap = cv2.VideoCapture(self.output_path)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                if fps > 0:
                    duration_sec = frame_count / fps
                    mins = int(duration_sec // 60)
                    secs = int(duration_sec % 60)
                    duration_str = f"{mins:02d}:{secs:02d}"
                cap.release()
        except:
            pass

        self.logger.info(f"Video saved: {self.output_path} | Duration: {duration_str}")
