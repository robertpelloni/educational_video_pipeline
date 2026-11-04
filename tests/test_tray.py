import sys
from unittest.mock import patch, MagicMock
from src.tray_icon import (
    create_tray_image,
    kill_process_by_pattern,
    open_dashboard,
    get_service_health,
    restart_services,
    stop_all_services,
    build_tray_icon,
)


def test_create_tray_image():
    img = create_tray_image()
    assert img.size == (64, 64)
    assert img.mode == "RGBA"


@patch("subprocess.run")
@patch("os.kill")
def test_kill_process_by_pattern(mock_kill, mock_run):
    mock_run.return_value = MagicMock(stdout="12345 67890\n")
    with patch("os.getpid", return_value=99999):
        killed = kill_process_by_pattern(["dummy_process"])
        assert killed == [12345, 67890]
        assert mock_kill.call_count == 2


@patch("webbrowser.open")
def test_open_dashboard(mock_web_open):
    url = open_dashboard()
    assert url == "http://localhost:5173"
    mock_web_open.assert_called_once_with("http://localhost:5173")


@patch("urllib.request.urlopen")
def test_get_service_health_online(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = (
        b'{"status": "online", "api_version": "0.4.0", "redis_connected": true}'
    )
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    health = get_service_health()
    assert "Online (API v0.4.0, Redis: True)" in health


@patch("urllib.request.urlopen")
def test_get_service_health_offline(mock_urlopen):
    mock_urlopen.side_effect = Exception("Connection refused")
    health = get_service_health()
    assert "Offline / Unreachable" in health


@patch("subprocess.Popen")
@patch("os.path.exists", return_value=True)
def test_restart_services(mock_exists, mock_popen):
    res = restart_services()
    assert res is True
    assert mock_popen.called


@patch("src.tray_icon.kill_process_by_pattern")
def test_stop_all_services(mock_kill):
    mock_icon = MagicMock()
    res = stop_all_services(mock_icon)
    assert res is True
    assert mock_kill.called
    assert mock_icon.stop.called


def test_build_tray_icon_mocked():
    mock_pystray = MagicMock()
    with patch.dict(sys.modules, {"pystray": mock_pystray}):
        icon = build_tray_icon()
        assert mock_pystray.Icon.called
        assert icon is not None
