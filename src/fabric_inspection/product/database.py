from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ProductDatabase:
    """Small SQLite repository for fabrics, inspections, and human review."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                PRAGMA journal_mode = WAL;
                CREATE TABLE IF NOT EXISTS fabrics (
                    fabric_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    default_engine TEXT NOT NULL DEFAULT 'classical_solution1',
                    commissioning_status TEXT NOT NULL DEFAULT 'DRAFT',
                    classical_model_path TEXT,
                    profile TEXT,
                    pass_threshold REAL,
                    review_threshold REAL,
                    fail_threshold REAL,
                    fail_enabled INTEGER NOT NULL DEFAULT 0,
                    commissioning_samples INTEGER NOT NULL DEFAULT 0,
                    commissioning_summary TEXT
                );
                CREATE TABLE IF NOT EXISTS commissioning_samples (
                    sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fabric_id TEXT NOT NULL REFERENCES fabrics(fabric_id) ON DELETE CASCADE,
                    path TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'upload',
                    created_at TEXT NOT NULL,
                    UNIQUE(fabric_id, path)
                );
                CREATE TABLE IF NOT EXISTS inspections (
                    inspection_id TEXT PRIMARY KEY,
                    comparison_group TEXT,
                    timestamp TEXT NOT NULL,
                    fabric_id TEXT NOT NULL REFERENCES fabrics(fabric_id),
                    engine TEXT NOT NULL,
                    anomaly_score REAL NOT NULL,
                    decision TEXT NOT NULL,
                    defect_count INTEGER NOT NULL,
                    latency_ms REAL NOT NULL,
                    image_path TEXT NOT NULL,
                    original_path TEXT NOT NULL,
                    anomaly_map_path TEXT NOT NULL,
                    anomaly_map_image_path TEXT NOT NULL,
                    overlay_path TEXT NOT NULL,
                    thresholds_json TEXT NOT NULL,
                    defects_json TEXT NOT NULL,
                    ground_truth_label INTEGER
                );
                CREATE TABLE IF NOT EXISTS operator_reviews (
                    inspection_id TEXT PRIMARY KEY REFERENCES inspections(inspection_id) ON DELETE CASCADE,
                    decision TEXT NOT NULL,
                    notes TEXT NOT NULL DEFAULT '',
                    reviewed_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_inspections_fabric_time
                    ON inspections(fabric_id, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_inspections_decision_time
                    ON inspections(decision, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_inspections_engine_time
                    ON inspections(engine, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_inspections_timestamp
                    ON inspections(timestamp DESC);
                PRAGMA optimize;
                """
            )

        with self.connect() as db:
            columns = {r[1] for r in db.execute("PRAGMA table_info(fabrics)")}
            if "profile" not in columns:
                db.execute("ALTER TABLE fabrics ADD COLUMN profile TEXT")
            db.execute("UPDATE fabrics SET commissioning_status = 'RECOMMISSION_REQUIRED' WHERE default_engine != 'classical_solution1' AND commissioning_status = 'READY'")

    @staticmethod
    def _decode_fabric(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        value = dict(row)
        value["fail_enabled"] = bool(value["fail_enabled"])
        value["commissioning_summary"] = (
            json.loads(value["commissioning_summary"])
            if value["commissioning_summary"] else None
        )
        return value

    def create_fabric(self, values: dict[str, Any]) -> dict[str, Any]:
        with self.connect() as db:
            db.execute(
                """INSERT INTO fabrics
                   (fabric_id, name, description, created_at, default_engine, profile)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    values["fabric_id"], values["name"], values.get("description", ""),
                    utc_now(), "classical_solution1",
                    values["profile"],
                ),
            )
        return self.get_fabric(values["fabric_id"]) or {}

    def list_fabrics(self) -> list[dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM fabrics ORDER BY created_at DESC").fetchall()
        return [self._decode_fabric(row) or {} for row in rows]

    def get_fabric(self, fabric_id: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM fabrics WHERE fabric_id = ?", (fabric_id,)).fetchone()
        return self._decode_fabric(row)

    def add_samples(self, fabric_id: str, paths: list[str], source: str = "upload") -> int:
        with self.connect() as db:
            db.executemany(
                """INSERT OR IGNORE INTO commissioning_samples
                   (fabric_id, path, source, created_at) VALUES (?, ?, ?, ?)""",
                [(fabric_id, path, source, utc_now()) for path in paths],
            )
            count = db.execute(
                "SELECT COUNT(*) FROM commissioning_samples WHERE fabric_id = ?", (fabric_id,)
            ).fetchone()[0]
            db.execute(
                "UPDATE fabrics SET commissioning_samples = ?, commissioning_status = 'SAMPLES_ADDED' WHERE fabric_id = ?",
                (count, fabric_id),
            )
        return int(count)

    def list_samples(self, fabric_id: str) -> list[dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT * FROM commissioning_samples WHERE fabric_id = ? ORDER BY sample_id",
                (fabric_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def mark_commissioning(self, fabric_id: str, status: str) -> None:
        with self.connect() as db:
            db.execute(
                "UPDATE fabrics SET commissioning_status = ? WHERE fabric_id = ?",
                (status, fabric_id),
            )

    def complete_commissioning(self, fabric_id: str, summary: dict[str, Any]) -> dict[str, Any]:
        with self.connect() as db:
            db.execute(
                """UPDATE fabrics SET commissioning_status = ?, default_engine = 'classical_solution1', classical_model_path = ?,
                   pass_threshold = ?, review_threshold = ?, fail_threshold = ?, fail_enabled = ?,
                   commissioning_samples = ?, commissioning_summary = ? WHERE fabric_id = ?""",
                (
                    "READY" if summary["validation_passed"] else "VALIDATION_FAILED",
                    summary["model_artifact_path"] if summary["validation_passed"] else None, summary["thresholds"]["pass"],
                    summary["thresholds"]["review"], summary["thresholds"].get("fail"),
                    int(summary["fail_enabled"]), summary["number_of_samples"],
                    json.dumps(summary), fabric_id,
                ),
            )
        return self.get_fabric(fabric_id) or {}

    @staticmethod
    def _decode_inspection(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        value = dict(row)
        value["thresholds"] = json.loads(value.pop("thresholds_json"))
        value["defects"] = json.loads(value.pop("defects_json"))
        if value.get("operator_decision") is not None:
            value["review"] = {
                "decision": value.pop("operator_decision"),
                "notes": value.pop("review_notes"),
                "reviewed_at": value.pop("reviewed_at"),
            }
        else:
            value.pop("operator_decision", None)
            value.pop("review_notes", None)
            value.pop("reviewed_at", None)
            value["review"] = None
        return value

    def save_inspection(self, value: dict[str, Any]) -> dict[str, Any]:
        with self.connect() as db:
            db.execute(
                """INSERT INTO inspections VALUES
                   (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    value["inspection_id"], value.get("comparison_group"), value["timestamp"],
                    value["fabric_id"], value["engine"], value["anomaly_score"],
                    value["decision"], value["defect_count"], value["latency_ms"],
                    value["image_path"], value["original_path"], value["anomaly_map_path"],
                    value["anomaly_map_image_path"], value["overlay_path"],
                    json.dumps(value["thresholds"]), json.dumps(value["defects"]),
                    value.get("ground_truth_label"),
                ),
            )
        return self.get_inspection(value["inspection_id"]) or {}

    def get_inspection(self, inspection_id: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute(
                """SELECT i.*, r.decision AS operator_decision, r.notes AS review_notes,
                          r.reviewed_at
                   FROM inspections i LEFT JOIN operator_reviews r USING (inspection_id)
                   WHERE i.inspection_id = ?""",
                (inspection_id,),
            ).fetchone()
        return self._decode_inspection(row)

    def list_inspections(
        self, fabric_id: str | None = None, decision: str | None = None,
        engine: str | None = None, date_from: str | None = None, date_to: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        predicates: list[str] = []
        parameters: list[Any] = []
        for column, value in (("i.fabric_id", fabric_id), ("i.decision", decision), ("i.engine", engine)):
            if value:
                predicates.append(f"{column} = ?")
                parameters.append(value)
        if date_from:
            predicates.append("i.timestamp >= ?")
            parameters.append(date_from)
        if date_to:
            predicates.append("i.timestamp <= ?")
            parameters.append(date_to)
        where = f"WHERE {' AND '.join(predicates)}" if predicates else ""
        parameters.append(min(max(limit, 1), 500))
        with self.connect() as db:
            rows = db.execute(
                f"""SELECT i.*, r.decision AS operator_decision, r.notes AS review_notes,
                           r.reviewed_at FROM inspections i
                    LEFT JOIN operator_reviews r USING (inspection_id)
                    {where} ORDER BY i.timestamp DESC LIMIT ?""",
                parameters,
            ).fetchall()
        return [self._decode_inspection(row) or {} for row in rows]

    def save_review(self, inspection_id: str, decision: str, notes: str) -> dict[str, Any]:
        with self.connect() as db:
            db.execute(
                """INSERT INTO operator_reviews (inspection_id, decision, notes, reviewed_at)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(inspection_id) DO UPDATE SET
                   decision = excluded.decision, notes = excluded.notes,
                   reviewed_at = excluded.reviewed_at""",
                (inspection_id, decision, notes, utc_now()),
            )
        return self.get_inspection(inspection_id) or {}

