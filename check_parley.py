"""Verify Parley authentication and discover the exact GPT-5.5 model ID."""

import os

from openai import OpenAI

from transit_agent import PARLEY_BASE_URL


def main() -> None:
    key = os.getenv("TRANSIT_LLM_API_KEY")
    if not key:
        raise SystemExit(
            "TRANSIT_LLM_API_KEY is not available in this shell. Export it and retry."
        )
    client = OpenAI(api_key=key, base_url=PARLEY_BASE_URL)
    matches = [
        item.id for item in client.models.list().data if "gpt-5.5" in item.id.lower()
    ]
    if not matches:
        raise SystemExit("Parley authentication worked, but GPT-5.5 was not listed.")
    print("GPT-5.5 model ID:", matches[0])
    print("Set TRANSIT_LLM_MODEL to this value only if automatic discovery is unwanted.")


if __name__ == "__main__":
    main()
