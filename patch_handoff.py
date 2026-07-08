import re

with open("HANDOFF.md", "r") as f:
    content = f.read()

content = content.replace(
    "- **Phase 5 (Multi-Platform Syndication):**",
    "- **Phase 6 (Interactive Web Player):** Initialized interactive web player. Scaffolded React stub `InteractivePlayer.jsx` and introduced Pydantic `BranchChoice` arrays to allow LLM engines to map branching narratives. Connected branching video segments dynamically by tracking sequence offsets.\n- **Security:** Implemented `slowapi` rate limiting on the FastAPI backend (5 requests per minute) to protect the Celery queue from DoS attacks.\n- **Phase 5 (Multi-Platform Syndication):**"
)

content = content.replace(
    "Phases 1, 2, 3, 4, and 5 are now fully functionally stubbed and architected.",
    "Phases 1, 2, 3, 4, 5, and 6 are now fully functionally stubbed and architected."
)

with open("HANDOFF.md", "w") as f:
    f.write(content)
