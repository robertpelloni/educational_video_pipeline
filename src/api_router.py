import os
import jsonschema
import logging
import re
import secrets
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from src.config import load_config, SCHEMA
from src.audio_engine import generate_all_voiceovers
from src.ffmpeg_engine import compile_video
from src.youtube_publisher import upload_video
from src.ingestion_engine import fetch_wikipedia_summary
from src.llm_engine import generate_script_from_text
from src.image_engine import generate_image_from_prompt

logger = logging.getLogger(__name__)

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Simple hardcoded authentication to protect the generation endpoint."""
    # In a production environment, this would validate against a database/OAuth
    # using timing-attack resistant comparisons.
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "supersecretpipeline")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

app = FastAPI(
    title="Educational Video Pipeline API",
    description="REST endpoint to trigger autonomous video generation",
    version="0.1.0"
)

class GenerateRequest(BaseModel):
    topic: str
    skip_upload: bool = True

def run_pipeline(topic: str, skip_upload: bool):
    """
    Executes the end-to-end video pipeline in the background.
    """
    logger.info(f"API Background Task: Initiating autonomous end-to-end generation for topic: '{topic}'")
    try:
        # 1a. Ingestion
        raw_text = fetch_wikipedia_summary(topic)

        # 1b. LLM Structure
        # Sanitize project_id to prevent Path Traversal vulnerabilities
        project_id = re.sub(r'[^a-zA-Z0-9]', '_', topic.lower())
        config = generate_script_from_text(raw_text, project_id=project_id)
        jsonschema.validate(instance=config, schema=SCHEMA)

        # 1c. Image Generation
        logger.info("Generating visual assets...")
        for scene in config.get("scenes", []):
            image_path = scene.get("image_path")
            if image_path and not os.path.exists(image_path):
                prompt = f"Educational illustration regarding: {scene.get('text')}"
                generate_image_from_prompt(prompt, image_path)

        # 2: Generate TTS audio clips
        logger.info("Checking and generating voiceovers...")
        generate_all_voiceovers(config)

        # 3: Compile video
        output_path = f"assets/exports/{project_id}.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"Compiling video to {output_path}...")
        compile_video(config, output_path=output_path)

        # 4: Upload to YouTube (if not skipped)
        if not skip_upload:
            logger.info("Initiating YouTube upload...")
            upload_video(output_path, config.get("youtube_metadata", {}))
        else:
            logger.info("Skipping YouTube upload as requested.")

        logger.info(f"Pipeline API execution completed successfully for topic '{topic}'.")
    except Exception as e:
        logger.error(f"Pipeline API background task failed: {e}", exc_info=True)

@app.post("/generate")
async def generate_video(request: GenerateRequest, background_tasks: BackgroundTasks, username: str = Depends(verify_credentials)):
    topic_clean = request.topic.strip()
    if not topic_clean:
        raise HTTPException(status_code=400, detail="The provided topic cannot be empty.")

    # Kick off the heavy processing in the background so the frontend doesn't timeout
    background_tasks.add_task(run_pipeline, topic_clean, request.skip_upload)

    return {
        "status": "success",
        "message": f"Pipeline generation started for topic: '{topic_clean}'",
        "topic": topic_clean
    }
