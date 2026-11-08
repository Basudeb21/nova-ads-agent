
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.model_adapters.llm.ollama_adapter import OllamaAdapter


async def main() -> None:
    adapter = OllamaAdapter()

    print("=" * 60)
    print("NOVA - OLLAMA ADAPTER TEST")
    print("=" * 60)

    text = await adapter.generate_text(
        system_prompt="You are a helpful assistant.",
        user_prompt="Reply with exactly: NOVA ADAPTER WORKING",
    )

    print("1. Text generation:")
    print(text)

    data = await adapter.generate_json(
        system_prompt=(
            "You are a structured data extraction assistant. "
            "Return only a valid JSON object."
        ),
        user_prompt=(
            "Extract the following information into JSON: "
            "The user wants an Instagram story advertisement "
            "for a perfume product. "
            "Use keys platform, placement, product_category."
        ),
    )

    print("\n2. JSON generation:")
    print(data)

    assert isinstance(data, dict)
    assert data.get("platform") is not None
    assert data.get("placement") is not None

    print("\nOLLAMA ADAPTER TEST SUCCESSFUL")


if __name__ == "__main__":
    asyncio.run(main())
