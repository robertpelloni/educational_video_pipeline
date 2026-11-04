"""
Desktop System Tray Controller for Educational Video Pipeline.
Provides a persistent status icon, menu actions to launch dashboard,
restart services, query system health, and cleanly shut down servers.
"""

import argparse
import logging
import os
import signal
import subprocess
import sys
import webbrowser

logger = logging.getLogger(__name__)


def create_tray_image():
    """Generates a dynamic 64x64 RGBA PIL icon with an artistic video slate/play theme."""
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Outer rounded circle / backdrop
    draw.ellipse(
        (4, 4, 60, 60), fill=(26, 35, 126, 255), outline=(63, 81, 181, 255), width=2
    )
    # Inner Play triangle
    draw.polygon([(24, 18), (24, 46), (48, 32)], fill=(0, 229, 255, 255))
    return image


def kill_process_by_pattern(patterns):
    """Gracefully terminates processes matching given command line patterns."""
    killed = []
    for pattern in patterns:
        try:
            result = subprocess.run(
                ["pgrep", "-f", pattern],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            pids = result.stdout.strip().split()
            current_pid = str(os.getpid())
            for pid_str in pids:
                if pid_str and pid_str != current_pid:
                    try:
                        pid = int(pid_str)
                        os.kill(pid, signal.SIGTERM)
                        killed.append(pid)
                    except ProcessLookupError:
                        pass
                    except PermissionError:
                        logger.warning(f"Permission denied to kill PID {pid_str}")
        except Exception as e:
            logger.error(f"Error terminating process with pattern '{pattern}': {e}")
    return killed


def open_dashboard():
    """Opens the local web dashboard in the system default browser."""
    url = "http://localhost:5173"
    logger.info(f"Opening dashboard URL: {url}")
    webbrowser.open(url)
    return url


def get_service_health():
    """Queries backend service health."""
    import urllib.request
    import json

    try:
        req = urllib.request.Request("http://127.0.0.1:8000/status")
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return f"Online (API v{data.get('api_version', '0.4.0')}, Redis: {data.get('redis_connected', False)})"
    except Exception as e:
        return f"Offline / Unreachable: {e}"
    return "Unknown"


def restart_services():
    """Executes the start_services script to reboot local uvicorn, redis, and celery."""
    logger.info("Restarting services via start_services.sh...")
    script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "start_services.sh"
    )
    if os.path.exists(script_path):
        subprocess.Popen(
            ["bash", script_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    return False


def stop_all_services(icon=None):
    """Terminates uvicorn, redis-server, celery workers, and tray icon."""
    logger.info("Stopping all video pipeline services...")
    kill_process_by_pattern(
        ["uvicorn.*src.api_router", "celery.*src.worker", "redis-server"]
    )
    if icon is not None:
        try:
            icon.stop()
        except Exception as e:
            logger.warning(f"Error stopping tray icon: {e}")
    return True


def build_tray_icon():
    """Constructs the pystray.Icon instance with contextual menu items."""
    import pystray

    image = create_tray_image()

    def on_dashboard(icon, item):
        open_dashboard()

    def on_status(icon, item):
        status_msg = get_service_health()
        logger.info(f"Pipeline Status: {status_msg}")
        try:
            icon.notify(f"Status: {status_msg}", title="Video Pipeline")
        except Exception:
            pass

    def on_restart(icon, item):
        restart_services()

    def on_quit(icon, item):
        stop_all_services(icon)

    menu = pystray.Menu(
        pystray.MenuItem("Open Dashboard", on_dashboard),
        pystray.MenuItem("Check Service Status", on_status),
        pystray.MenuItem("Restart Services", on_restart),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit All Services", on_quit),
    )

    icon = pystray.Icon(
        "video_pipeline_tray", image, "Educational Video Pipeline", menu=menu
    )
    return icon


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    parser = argparse.ArgumentParser(
        description="Educational Video Pipeline System Tray Manager"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run status check without interactive tray",
    )
    parser.add_argument(
        "--stop", action="store_true", help="Stop all background services and exit"
    )
    args = parser.parse_args()

    if args.stop:
        logger.info("Triggering full service stop...")
        stop_all_services()
        sys.exit(0)

    if args.headless:
        logger.info("Headless status check mode:")
        health = get_service_health()
        logger.info(f"System Health: {health}")
        sys.exit(0)

    try:
        icon = build_tray_icon()
        logger.info("Starting System Tray Icon...")
        icon.run()
    except Exception as e:
        logger.warning(
            f"Unable to run graphical system tray (likely headless display): {e}"
        )
        logger.info("Falling back to headless service controller.")


if __name__ == "__main__":
    main()
