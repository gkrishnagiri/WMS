"""Seed editable, non-authoritative OpenAI pricing assumptions."""
from datetime import date
from sqlalchemy import select
from app.core.config import get_settings
from app.db.session import DatabaseManager
from app.models.ai_config import AiModelConfig, AiProvider
from app.models.ai_costing import AiModelPricing

MODELS = [("OPENAI_GPT_5_4_MINI", "gpt-5.4-mini", "GPT-5.4 Mini"), ("OPENAI_GPT_5_4", "gpt-5.4", "GPT-5.4"), ("OPENAI_GPT_5_MINI", "gpt-5-mini", "GPT-5 Mini"), ("OPENAI_GPT_5", "gpt-5", "GPT-5")]


def seed() -> None:
    manager = DatabaseManager(get_settings()); manager.initialize(); assert manager.session_factory
    with manager.session_factory() as db:
        provider = db.scalar(select(AiProvider).where(AiProvider.provider_code == "OPENAI_RESPONSES"))
        if provider is None:
            raise RuntimeError("Run seed_ai_config before seed_ai_model_pricing.")
        for code, external, display in MODELS:
            model = db.scalar(select(AiModelConfig).where(AiModelConfig.model_code == code))
            if model is None:
                model = AiModelConfig(model_code=code, provider_id=provider.id, display_name=f"{display} (Governed, Disabled)", model_name=external, model_family="OPENAI_RESPONSES", purpose="AGENT_STAGE_1_CHAT", enabled=False, is_default=False, temperature=0, top_p=1, max_output_tokens=1200, context_window_tokens=128000, cost_per_1k_input_tokens=0, cost_per_1k_output_tokens=0)
                db.add(model); db.flush()
            pricing = db.scalar(select(AiModelPricing).where(AiModelPricing.provider_code == "OPENAI_RESPONSES", AiModelPricing.model_code == code, AiModelPricing.is_active.is_(True)))
            if pricing is None:
                db.add(AiModelPricing(pricing_id=f"PRICE-{code}-INITIAL", provider_code="OPENAI_RESPONSES", model_code=code, external_model_name=external, currency="USD", input_cost_per_million_tokens=0, completion_cost_per_million_tokens=0, pricing_source_note="User-editable placeholder. Verify against current OpenAI pricing before real use.", pricing_effective_from=date.today(), is_active=True))
        db.commit(); print(f"AI model pricing seed complete: {db.query(AiModelPricing).count()} active/history rows")
    manager.dispose()


if __name__ == "__main__": seed()
