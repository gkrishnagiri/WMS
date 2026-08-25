"""Seed the deterministic guided demo scenario catalog (idempotent)."""

from app.core.config import get_settings
from app.db.session import DatabaseManager
from app.models.demo_scenario import DemoScenario
from app.services.demo_scenario_service import SCENARIO_DEFINITIONS


def main() -> None:
    manager = DatabaseManager(get_settings())
    manager.initialize()
    with manager.session_factory() as db:
        for code, definition in SCENARIO_DEFINITIONS.items():
            row = db.query(DemoScenario).filter(DemoScenario.scenario_code == code).one_or_none()
            if row is None:
                row = DemoScenario(scenario_code=code)
                db.add(row)
            row.title = definition["title"]
            row.description = definition["description"]
            row.business_value = definition["business_value"]
            row.default_experience = definition["default_experience"]
            row.sort_order = definition["sort_order"]
            row.is_enabled = True
        db.commit()
    print(f"Seeded {len(SCENARIO_DEFINITIONS)} demo scenarios.")


if __name__ == "__main__":
    main()
