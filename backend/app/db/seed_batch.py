"""Idempotent seed for deterministic batch jobs and ordered steps."""

from __future__ import annotations

from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import DatabaseManager
from app.models.batch import BatchJob, BatchJobStep


JOBS = [
    ("BATCH-INV-RECON", "Nightly Inventory Reconciliation", "Reconcile warehouse balances and publish variance results.", "INVENTORY_RECONCILIATION", "HIGH", 120, [
        ("EXTRACT_INVENTORY_BALANCES", "Extract Inventory Balances", "EXTRACT"), ("VALIDATE_BALANCES", "Validate Balances", "VALIDATE"), ("RECONCILE_ON_HAND", "Reconcile On Hand", "RECONCILE"), ("GENERATE_VARIANCE_REPORT", "Generate Variance Report", "EXPORT"), ("PUBLISH_RESULTS", "Publish Results", "EXPORT")]),
    ("BATCH-ORDER-RELEASE", "Wave Order Release", "Select eligible orders and release them to fulfillment.", "ORDER_RELEASE", "HIGH", 90, [
        ("SELECT_RELEASE_CANDIDATES", "Select Release Candidates", "EXTRACT"), ("VALIDATE_RELEASE_PREREQUISITES", "Validate Release Prerequisites", "VALIDATE"), ("RELEASE_ORDERS", "Release Orders", "PROCESS"), ("PUBLISH_RELEASE_SUMMARY", "Publish Release Summary", "EXPORT")]),
    ("BATCH-SHIP-SYNC", "Shipment Status Synchronization", "Synchronize shipment status with carrier systems.", "SHIPMENT_SYNC", "HIGH", 60, [
        ("EXTRACT_OPEN_SHIPMENTS", "Extract Open Shipments", "EXTRACT"), ("SYNC_CARRIER_STATUS", "Sync Carrier Status", "EXTERNAL_CALL"), ("VALIDATE_STATUS_CHANGES", "Validate Status Changes", "VALIDATE"), ("PUBLISH_SHIPMENT_RESULTS", "Publish Shipment Results", "EXPORT")]),
    ("BATCH-LOW-STOCK", "Low Stock Notification Batch", "Scan low stock balances and publish notifications.", "LOW_STOCK_NOTIFICATION", "MEDIUM", 45, [
        ("SCAN_LOW_STOCK", "Scan Low Stock", "EXTRACT"), ("BUILD_NOTIFICATION_PAYLOADS", "Build Notification Payloads", "TRANSFORM"), ("PUBLISH_NOTIFICATIONS", "Publish Notifications", "NOTIFY"), ("RECORD_NOTIFICATION_RESULTS", "Record Notification Results", "EXPORT")]),
    ("BATCH-INV-SNAPSHOT", "Inventory Snapshot Batch", "Create a point-in-time inventory snapshot for operations.", "INVENTORY_SNAPSHOT", "MEDIUM", 60, [
        ("EXTRACT_BALANCE_DATA", "Extract Balance Data", "EXTRACT"), ("VALIDATE_SNAPSHOT_DATA", "Validate Snapshot Data", "VALIDATE"), ("WRITE_SNAPSHOT", "Write Snapshot", "PROCESS"), ("PUBLISH_SNAPSHOT", "Publish Snapshot", "EXPORT")]),
]


def seed() -> None:
    manager = DatabaseManager(get_settings())
    manager.initialize()
    assert manager.session_factory is not None
    with manager.session_factory() as db:
        for code, name, description, job_type, severity, sla, steps in JOBS:
            job = db.scalar(select(BatchJob).where(BatchJob.job_code == code))
            if job is None:
                job = BatchJob(job_code=code, name=name, description=description, job_type=job_type, module="WAREHOUSE_FULFILLMENT", business_service="Warehouse & Fulfillment Operations", application_name="Enterprise Operations Suite", enabled=True, default_severity=severity, sla_minutes=sla)
                db.add(job)
                db.flush()
            else:
                job.name, job.description, job.job_type, job.default_severity, job.sla_minutes = name, description, job_type, severity, sla
            for order, (step_code, step_name, step_type) in enumerate(steps, 1):
                step = db.scalar(select(BatchJobStep).where(BatchJobStep.job_id == job.id, BatchJobStep.step_code == step_code))
                if step is None:
                    db.add(BatchJobStep(job_id=job.id, step_code=step_code, step_name=step_name, step_order=order, step_type=step_type, description=f"Deterministic {step_name.lower()} step.", enabled=True, expected_duration_ms=500 + order * 100))
                else:
                    step.step_name, step.step_order, step.step_type, step.enabled = step_name, order, step_type, True
        db.commit()
    manager.dispose()
    print(f"Batch seed complete: batch_jobs={len(JOBS)}, batch_job_steps={sum(len(job[-1]) for job in JOBS)}")


if __name__ == "__main__":
    seed()
