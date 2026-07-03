import pytest
import os
import json
import base64
import urllib.error
from unittest.mock import patch, MagicMock
from src.image_engine import generate_image_from_prompt

@patch("src.image_engine.urllib.request.urlopen")
def test_generate_image_success(mock_urlopen, tmp_path):
    # Mock a base64 encoded dummy image
    dummy_image_data = b"dummy_png_bytes"
    base64_encoded = base64.b64encode(dummy_image_data).decode('utf-8')

    mock_response = MagicMock()
    mock_data = json.dumps({"images": [base64_encoded]}).encode('utf-8')
    mock_response.read.return_value = mock_data
    mock_urlopen.return_value.__enter__.return_value = mock_response

    output_path = str(tmp_path / "test_image.png")

    # Run the engine
    success = generate_image_from_prompt("A detailed medical illustration of a heart", output_path)

    assert success is True
    assert os.path.exists(output_path)

    with open(output_path, "rb") as f:
        saved_data = f.read()
    assert saved_data == dummy_image_data
    mock_urlopen.assert_called_once()

def test_generate_image_empty_inputs():
    with pytest.raises(ValueError, match="Image prompt cannot be empty."):
        generate_image_from_prompt("", "out.png")

    with pytest.raises(ValueError, match="Output path cannot be empty."):
        generate_image_from_prompt("test", "")

@patch("src.image_engine.urllib.request.urlopen")
def test_generate_image_missing_image_array(mock_urlopen, tmp_path):
    # Mock API returning unexpected structure
    mock_response = MagicMock()
    mock_data = json.dumps({"parameters": {}, "info": ""}).encode('utf-8')
    mock_response.read.return_value = mock_data
    mock_urlopen.return_value.__enter__.return_value = mock_response

    output_path = str(tmp_path / "test_image_fail.png")

    success = generate_image_from_prompt("test", output_path)
    assert success is False
    assert not os.path.exists(output_path)

@patch("src.image_engine.urllib.request.urlopen")
def test_generate_image_connection_error(mock_urlopen, tmp_path):
    # Simulate connection refused / API offline
    error_mock = urllib.error.URLError(reason="Connection refused")
    mock_urlopen.side_effect = error_mock

    output_path = str(tmp_path / "test_image_error.png")

    success = generate_image_from_prompt("test", output_path)
    assert success is False
