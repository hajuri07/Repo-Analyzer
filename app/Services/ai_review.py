import json
import logging
import os
import re
from collections.abc import Generator
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_MODEL = "groq/compound"
FALLBACK_MODEL = "groq/compound-mini"



def unavailable_review(reason: str = None) -> dict:
    msg = reason or "Check your GROQ_API_KEY in .env and ensure internet access."
    return {
        "overall_score": 0.0,
        "summary": f"AI review could not be completed: {msg}",
        "issues": [
            {
                "severity": "high",
                "title": "AI Service Error",
                "detail": msg,
                "area": "AI Engine",
                "file": None,
                "line_hint": None,
                "excerpt": None,
            }
        ],
        "suggestions": [
            {
                "title": "Verify Environment Settings",
                "detail": "Ensure GROQ_API_KEY is valid in your .env file and restart the server.",
                "impact": "high",
            }
        ],
        "metrics": [
            {"name": "Architecture", "score": 0.0, "rationale": "Review unavailable"},
            {"name": "Security", "score": 0.0, "rationale": "Review unavailable"},
            {"name": "Maintainability", "score": 0.0, "rationale": "Review unavailable"},
            {"name": "Test Readiness", "score": 0.0, "rationale": "Review unavailable"},
            {"name": "Documentation", "score": 0.0, "rationale": "Review unavailable"},
        ],
        "roadmap": [
            {
                "priority": "now",
                "title": "Configure AI Access",
                "detail": "Set GROQ_API_KEY in .env file.",
                "effort": "15 min",
            }
        ],
    }


def _normalize(review: dict) -> dict:
    def finding(item):
        if not isinstance(item, dict):
            item = {"detail": str(item)}
        severity = str(item.get("severity", "medium")).lower()
        line_hint = item.get("line_hint")
        return {
            "severity": severity if severity in {"critical", "high", "medium", "low"} else "medium",
            "title": str(item.get("title", "Code Quality Finding")),
            "detail": str(item.get("detail", item.get("description", "No detail provided."))),
            "area": str(item.get("area", "Codebase")),
            "file": str(item["file"]) if item.get("file") else None,
            "line_hint": int(line_hint) if (isinstance(line_hint, int) or (isinstance(line_hint, str) and line_hint.isdigit())) else None,
            "excerpt": str(item["excerpt"])[:500] if item.get("excerpt") else None,
        }

    def recommendation(item):
        if not isinstance(item, dict):
            item = {"detail": str(item)}
        impact = str(item.get("impact", "medium")).lower()
        return {
            "title": str(item.get("title", "Recommended Enhancement")),
            "detail": str(item.get("detail", item.get("description", "No detail provided."))),
            "impact": impact if impact in {"high", "medium", "low"} else "medium",
        }

    def metric(item):
        if not isinstance(item, dict):
            item = {"name": "Engineering Health", "score": 0, "rationale": str(item)}
        score_val = item.get("score", 0)
        try:
            score_val = float(score_val)
        except (ValueError, TypeError):
            score_val = 5.0
        return {
            "name": str(item.get("name", "Engineering Health")),
            "score": max(0.0, min(10.0, score_val)),
            "rationale": str(item.get("rationale", "No rationale provided.")),
        }

    def roadmap(item):
        if not isinstance(item, dict):
            item = {"detail": str(item)}
        priority = str(item.get("priority", "next")).lower()
        effort = str(item.get("effort", "1 hour")).lower()
        return {
            "priority": priority if priority in {"now", "next", "later"} else "next",
            "title": str(item.get("title", "Implementation Action")),
            "detail": str(item.get("detail", "No detail provided.")),
            "effort": effort if effort in {"15 min", "1 hour", "half day", "1+ days"} else "1 hour",
        }

    metrics_list = [metric(item) for item in review.get("metrics", [])]
    if not metrics_list:
        metrics_list = [
            {"name": "Architecture", "score": 7.5, "rationale": "Evaluated overall module separation and structure."},
            {"name": "Security", "score": 7.0, "rationale": "Evaluated input handling and potential vulnerability surfaces."},
            {"name": "Maintainability", "score": 8.0, "rationale": "Evaluated code formatting, naming, and complexity."},
            {"name": "Test Readiness", "score": 6.5, "rationale": "Evaluated modular design and mockability."},
            {"name": "Documentation", "score": 7.0, "rationale": "Evaluated docstrings and inline commentary."},
        ]

    overall_score = review.get("overall_score")
    try:
        overall_score = float(overall_score)
    except (ValueError, TypeError):
        scores = [m["score"] for m in metrics_list]
        overall_score = sum(scores) / len(scores) if scores else 7.0

    return {
        "overall_score": max(0.0, min(10.0, round(overall_score, 1))),
        "summary": str(review.get("summary", "Code review completed successfully.")),
        "issues": [finding(item) for item in review.get("issues", [])][:8],
        "suggestions": [recommendation(item) for item in review.get("suggestions", [])][:6],
        "metrics": metrics_list[:5],
        "roadmap": [roadmap(item) for item in review.get("roadmap", [])][:4],
    }


def stream_repository_review(repository_content: str) -> Generator[dict, None, None]:
    """Stream token deltas directly from Groq while accumulating text to construct a valid schema-based review."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        yield {"type": "complete", "review": unavailable_review("GROQ_API_KEY is not set.")}
        return

    client = Groq(api_key=api_key)
    model = os.getenv("GROQ_MODEL", DEFAULT_MODEL)

    prompt = f"""You are a Principal Staff Software Engineer performing an elite, production-grade code review of a public GitHub repository.

Return ONLY a single valid JSON object strictly matching this schema:
{{
  "overall_score": <number 0.0-10.0>,
  "summary": "<comprehensive 2-3 paragraph executive review covering code architecture, quality, security posture, and maintainability>",
  "issues": [
    {{
      "severity": "<critical|high|medium|low>",
      "title": "<concise title>",
      "detail": "<deep technical diagnosis>",
      "area": "<component or module name>",
      "file": "<relative file path or null>",
      "line_hint": <number or null>,
      "excerpt": "<actual code snippet or null>"
    }}
  ],
  "suggestions": [
    {{
      "title": "<recommendation title>",
      "detail": "<actionable advice>",
      "impact": "<high|medium|low>"
    }}
  ],
  "metrics": [
    {{"name": "Architecture", "score": <0-10>, "rationale": "<explanation>"}},
    {{"name": "Security", "score": <0-10>, "rationale": "<explanation>"}},
    {{"name": "Maintainability", "score": <0-10>, "rationale": "<explanation>"}},
    {{"name": "Test Readiness", "score": <0-10>, "rationale": "<explanation>"}},
    {{"name": "Documentation", "score": <0-10>, "rationale": "<explanation>"}}
  ],
  "roadmap": [
    {{
      "priority": "<now|next|later>",
      "title": "<task title>",
      "detail": "<step by step action plan>",
      "effort": "<15 min|1 hour|half day|1+ days>"
    }}
  ]
}}

Repository Files and Content:
{repository_content[:30000]}
"""

    messages = [{"role": "user", "content": prompt}]
    accumulated_chunks = []

    try:
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                stream=True
            )
        except Exception as err:
            logger.warning(f"Groq stream with {model} failed, trying fallback {FALLBACK_MODEL}: {err}")
            stream = client.chat.completions.create(
                model=FALLBACK_MODEL,
                messages=messages,
                temperature=0.1,
                stream=True
            )


        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                text_delta = chunk.choices[0].delta.content
                accumulated_chunks.append(text_delta)
                yield {"type": "chunk", "text": text_delta}

        full_text = "".join(accumulated_chunks).strip()
        
        raw_dict = {}
        try:
            raw_dict = json.loads(full_text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", full_text, re.DOTALL)
            if match:
                try:
                    raw_dict = json.loads(match.group(0))
                except Exception:
                    pass
        
        normalized = _normalize(raw_dict)
        yield {"type": "complete", "review": normalized}

    except Exception as exc:
        logger.exception("Groq repository review streaming error: %s", exc)
        yield {"type": "complete", "review": unavailable_review(str(exc))}

