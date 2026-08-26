"""Print the deterministic Stage 3 profile catalog.

Profiles are code-governed rather than database data, so this seed is
intentionally idempotent and performs no writes.
"""

from app.services.stage3_autonomous_service import PROFILE_DEFINITIONS


def main() -> None:
    for code, profile in PROFILE_DEFINITIONS.items():
        print(f"{code}: {profile['title']} ({len(profile['allowed_actions'])} allowed actions)")


if __name__ == "__main__":
    main()
