import sys
from unittest.mock import patch, MagicMock

def test_main_pipeline_execution():
    """
    Tests the main.py entrypoint to ensure the pipeline functions are called sequentially
    without actually running the heavy media/network logic.
    """
    # Create a mock config dictionary to return from load_config
    mock_config = {
        "project_id": "test_integration",
        "youtube_metadata": {"title": "Test"}
    }

    # We patch the sys.argv to simulate running the script from the command line
    test_args = ["main.py", "--config", "dummy_config.json", "--output", "dummy_out.mp4"]

    with patch.object(sys, 'argv', test_args), \
         patch("main.load_config", return_value=mock_config) as mock_load_config, \
         patch("main.generate_all_voiceovers") as mock_generate_audio, \
         patch("main.compile_video") as mock_compile_video, \
         patch("main.upload_video") as mock_upload_video:

        # Import main locally so patches apply correctly
        from main import main

        main()

        # Verify the sequential pipeline calls
        mock_load_config.assert_called_once_with("dummy_config.json")
        mock_generate_audio.assert_called_once_with(mock_config)
        mock_compile_video.assert_called_once_with(mock_config, output_path="dummy_out.mp4")
        mock_upload_video.assert_called_once_with("dummy_out.mp4", mock_config["youtube_metadata"])

def test_main_pipeline_skip_upload():
    """
    Tests the main.py entrypoint to ensure the upload is skipped when the flag is present.
    """
    mock_config = {"project_id": "test_integration"}

    test_args = ["main.py", "--config", "dummy_config.json", "--skip-upload"]

    with patch.object(sys, 'argv', test_args), \
         patch("main.load_config", return_value=mock_config), \
         patch("main.generate_all_voiceovers"), \
         patch("main.compile_video"), \
         patch("main.upload_video") as mock_upload_video:

        from main import main
        main()

        # Verify upload was skipped
        mock_upload_video.assert_not_called()
