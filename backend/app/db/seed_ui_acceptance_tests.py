"""Seed the deterministic manual UI acceptance catalog (idempotent)."""

from app.core.config import get_settings
from app.db.session import DatabaseManager
from app.services.ui_acceptance_service import seed_catalog, UI_TEST_CATALOG


def main() -> None:
    manager = DatabaseManager(get_settings())
    manager.initialize()
    with manager.session_factory() as db:
        created = seed_catalog(db)
        db.commit()
    print(f"Seeded UI acceptance catalog: suites={len(UI_TEST_CATALOG)}, records_created={created}.")


if __name__ == "__main__":
    main()
