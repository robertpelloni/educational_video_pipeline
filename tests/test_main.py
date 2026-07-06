import sys
from unittest.mock import patch


def test_main_pipeline_execution_with_config():
    """
    Tests the main.py entrypoint to ensure the pipeline functions are called sequentially
    without actually running the heavy media/network logic.
    """
    # Create a mock config dictionary to return from load_config
    mock_config = {
        "project_id": "test_integration",
        "youtube_metadata": {"title": "Test"},
    }

    # We patch the sys.argv to simulate running the script from the command line
    test_args = [
        "main.py",
        "--config",
        "dummy_config.json",
        "--output",
        "dummy_out.mp4",
    ]

    with patch.object(sys, "argv", test_args), patch(
        "main.load_config", return_value=mock_config
    ) as mock_load_config, patch(
        "main.generate_all_voiceovers"
    ) as mock_generate_audio, patch(
        "main.compile_video"
    ) as mock_compile_video, patch(
        "main.youtube_upload"
    ) as mock_youtube_upload:

        # Import main locally so patches apply correctly
        from main import main

        main()

        # Verify the sequential pipeline calls
        mock_load_config.assert_called_once_with("dummy_config.json")
        mock_generate_audio.assert_called_once_with(mock_config)
        mock_compile_video.assert_called_once_with(
            mock_config, output_path="dummy_out_landscape.mp4", canvas_format="landscape"
        )
        mock_youtube_upload.assert_called_once_with(
            "dummy_out_landscape.mp4", mock_config["youtube_metadata"]
        )


@patch("main.os.path.exists", return_value=False)
def test_main_pipeline_execution_with_topic(mock_exists):
    """
    Tests the main.py entrypoint when using the --topic flag for end-to-end generation.
    """
    test_args = [
        "main.py",
        "--topic",
        "Heart",
        "--output",
        "dummy_out.mp4",
        "--skip-upload",
    ]

    mock_llm_config = {
        "project_id": "heart",
        "canvas_format": "landscape",
        "background_music": "assets/music/default_background.mp3",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "The heart is an organ.",
                "image_path": "assets/images/heart_scene_1.png",
                "voiceover_path": "assets/audio/heart_scene_1.mp3",
            }
        ],
        "youtube_metadata": {
            "title": "Automated Educational Video: heart",
            "description": "Generated autonomously from public domain text.",
            "tags": ["education", "automated", "science"],
            "category_id": "27",
        },
    }

    with patch.object(sys, "argv", test_args), patch(
        "main.fetch_wikipedia_summary", return_value="The heart is an organ."
    ) as mock_fetch, patch(
        "main.generate_script_from_text", return_value=mock_llm_config
    ) as mock_generate_script, patch(
        "main.generate_image_from_prompt"
    ) as mock_generate_image, patch(
        "main.generate_all_voiceovers"
    ) as mock_generate_audio, patch(
        "main.compile_video"
    ) as mock_compile_video, patch(
        "main.youtube_upload"
    ) as mock_youtube_upload:

        from main import main

        main()

        # Verify the sequential pipeline calls
        mock_fetch.assert_called_once_with("Heart")
        mock_generate_script.assert_called_once_with(
            "The heart is an organ.", project_id="heart"
        )
        mock_generate_image.assert_called_once_with(
            "Educational illustration regarding: The heart is an organ.",
            "assets/images/heart_scene_1.png",
        )

        mock_generate_audio.assert_called_once_with(mock_llm_config)
        mock_compile_video.assert_called_once_with(
            mock_llm_config, output_path="dummy_out_landscape.mp4", canvas_format="landscape"
        )
        mock_youtube_upload.assert_not_called()


def test_main_pipeline_skip_upload():
    """
    Tests the main.py entrypoint to ensure the upload is skipped when the flag is present.
    """
    mock_config = {"project_id": "test_integration"}

    test_args = ["main.py", "--config", "dummy_config.json", "--skip-upload"]

    with patch.object(sys, "argv", test_args), patch(
        "main.load_config", return_value=mock_config
    ), patch("main.generate_all_voiceovers"), patch("main.compile_video"), patch(
        "main.youtube_upload"
    ) as mock_youtube_upload:

        from main import main

        main()

        # Verify upload was skipped
        mock_youtube_upload.assert_not_called()
