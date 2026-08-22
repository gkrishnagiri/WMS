"""Idempotently seed the governed copilot safe-action catalog."""

from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import DatabaseManager
from app.models.copilot import CopilotSafeAction


SAFE_ACTIONS = [
    ("ACKNOWLEDGE_TICKET", "Acknowledge ticket", "Recommend acknowledgement of a support ticket; never execute it automatically.", "AMS", "RECOMMEND", "LOW"),
    ("START_TICKET_WORK", "Start ticket work", "Recommend moving an AMS ticket into active investigation.", "AMS", "RECOMMEND", "LOW"),
    ("CREATE_TICKET_WORK_NOTE_DRAFT", "Create ticket work note draft", "Generate an internal work-note draft for human review.", "AMS", "DRAFT", "LOW"),
    ("ACKNOWLEDGE_ALERT", "Acknowledge monitoring alert", "Recommend acknowledgement of an alert; support engineer must perform the action.", "MONITORING", "RECOMMEND", "LOW"),
    ("CREATE_DIAGNOSTIC_FROM_ALERT", "Create diagnostic from alert", "Recommend creating a deterministic diagnostic from an existing alert.", "OBSERVABILITY", "RECOMMEND", "MEDIUM"),
    ("CREATE_DIAGNOSTIC_FROM_BATCH_RUN", "Create diagnostic from batch run", "Recommend creating a diagnostic from failed batch evidence.", "OBSERVABILITY", "RECOMMEND", "MEDIUM"),
    ("CREATE_TICKET_FROM_EXCEPTION", "Create ticket from exception", "Recommend creating an AMS ticket from an operational exception.", "AMS", "RECOMMEND", "MEDIUM"),
    ("CREATE_TICKET_FROM_BATCH_RUN", "Create ticket from batch run", "Recommend creating an AMS ticket from a failed batch run.", "AMS", "RECOMMEND", "MEDIUM"),
    ("CREATE_TICKET_FROM_DIAGNOSTIC", "Create ticket from diagnostic", "Recommend linking or creating a ticket from a diagnostic case.", "AMS", "RECOMMEND", "MEDIUM"),
    ("GENERATE_CUSTOMER_UPDATE", "Generate customer update", "Draft a plain-language customer update without sending it.", "AMS", "DRAFT", "LOW"),
    ("GENERATE_INVESTIGATION_CHECKLIST", "Generate investigation checklist", "Draft a reviewable investigation checklist from assembled context.", "COPILOT", "DRAFT", "LOW"),
]


def seed() -> None:
    manager = DatabaseManager(get_settings())
    manager.initialize()
    assert manager.session_factory is not None
    with manager.session_factory() as db:
        for code, name, description, module, action_type, risk in SAFE_ACTIONS:
            row = db.scalar(select(CopilotSafeAction).where(CopilotSafeAction.action_code == code))
            if row is None:
                db.add(CopilotSafeAction(action_code=code, name=name, description=description, target_module=module, action_type=action_type, risk_level=risk, requires_human_approval=True, enabled=True))
            else:
                row.name, row.description, row.target_module, row.action_type, row.risk_level = name, description, module, action_type, risk
                row.requires_human_approval, row.enabled = True, True
        db.commit()
        print(f"Copilot seed complete: safe_actions={db.query(CopilotSafeAction).count()}")
    manager.dispose()


if __name__ == "__main__":
    seed()
