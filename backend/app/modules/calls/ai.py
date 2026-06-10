import json
import logging

from openai import AsyncOpenAI

from app.core.config import settings
from app.modules.calls.schema import CallLabel

logger = logging.getLogger(__name__)

LABEL_VALUES = [label.value for label in CallLabel]


async def enrich_call_from_transcript(transcript: str) -> tuple[str, CallLabel] | None:
    try:
        if not settings.openai_api_key:
            logger.warning("OPENAI_API_KEY is not set; skipping AI enrichment")
            return None

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        labels_str = ", ".join(LABEL_VALUES)

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You analyze phone call transcripts. Return JSON with exactly two keys: "
                        '"summary" (a 2-3 sentence summary) and "label" (exactly one of: '
                        f"{labels_str})."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Transcript:\n{transcript}",
                },
            ],
        )

        content = response.choices[0].message.content
        if not content:
            logger.warning("OpenAI returned empty content")
            return None

        data = json.loads(content)
        summary = data.get("summary")
        label_str = data.get("label")

        if not summary or not label_str:
            logger.warning("OpenAI response missing summary or label: %s", data)
            return None

        if label_str not in LABEL_VALUES:
            logger.warning("OpenAI returned invalid label: %s", label_str)
            return None

        return summary, CallLabel(label_str)
    except Exception:
        logger.exception("Failed to enrich call from transcript")
        return None
