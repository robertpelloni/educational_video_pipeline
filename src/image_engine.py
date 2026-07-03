import os
import json
import base64
import urllib.request
import urllib.error
import logging

logger = logging.getLogger(__name__)

def generate_image_from_prompt(prompt: str, output_path: str, api_url: str = "http://127.0.0.1:7860/sdapi/v1/txt2img") -> bool:
    """
    Interfaces with a standard local Stable Diffusion WebUI API (AUTOMATIC1111)
    to generate an image from a text prompt and save it to disk.

    Args:
        prompt (str): The visual prompt describing the desired image.
        output_path (str): The file path where the resulting PNG should be saved.
        api_url (str): The URL of the SD WebUI API endpoint.

    Returns:
        bool: True if the image was successfully generated and saved, False otherwise.

    Raises:
        ValueError: If the prompt or output path is empty.
    """
    if not prompt:
        raise ValueError("Image prompt cannot be empty.")
    if not output_path:
        raise ValueError("Output path cannot be empty.")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    payload = {
        "prompt": prompt,
        "steps": 20,
        "width": 1080,  # Defaulting to portrait/Shorts width
        "height": 1920, # Defaulting to portrait/Shorts height
        "cfg_scale": 7.0,
        "sampler_name": "Euler a"
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        api_url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    logger.info(f"Requesting image generation for prompt: '{prompt[:30]}...'")

    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))

            if 'images' in response_data and len(response_data['images']) > 0:
                # The API returns the image as a base64 encoded string
                image_data = base64.b64decode(response_data['images'][0])

                with open(output_path, "wb") as f:
                    f.write(image_data)

                logger.info(f"Successfully generated and saved image to {output_path}")
                return True
            else:
                logger.error("API response did not contain 'images' array.")
                return False

    except urllib.error.URLError as e:
        logger.error(f"Failed to connect to image generation API at {api_url}: {e}")
        # In a real pipeline, we might return False to trigger a fallback or raise depending on strictness
        return False
