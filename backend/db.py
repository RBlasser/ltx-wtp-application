"""PostgreSQL persistence layer using psycopg3 connection pool."""

import json
import uuid
from typing import Any
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from config import settings

pool: ConnectionPool | None = None


def init_pool() -> None:
    """Initialize PostgreSQL connection pool."""
    global pool
    if pool is None:
        pool = ConnectionPool(
            conninfo=settings.database_url,
            min_size=1,
            max_size=10,
            open=True,
        )


def close_pool() -> None:
    """Close PostgreSQL connection pool cleanly."""
    global pool
    if pool is not None:
        pool.close()
        pool = None


def _get_pool() -> ConnectionPool:
    if pool is None:
        raise RuntimeError("Database pool is not initialized.")
    return pool


def check_db_health() -> bool:
    """Verify database connectivity."""
    with _get_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            row = cur.fetchone()
            return bool(row and row[0] == 1)


def insert_survey_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Insert a session and validated WTP response atomically."""
    session_id = f"ses_{uuid.uuid4().hex[:16]}"
    response_id = f"res_{uuid.uuid4().hex[:16]}"
    invitation_token = f"tok_{uuid.uuid4().hex}"

    selected_ids = payload.get("selectedServiceIds") or []
    priority_datasets = payload.get("priorityDatasets") or []
    role_category = payload.get("roleCategory") or ""
    services_json = json.dumps(
        {
            "s3": bool(payload["s3"]) or ("srv_aws_s3_hechos_relevantes" in selected_ids),
            "tablero": bool(payload["tablero"]) or ("srv_whitelabel_terminal" in selected_ids),
            "sdk": bool(payload["sdk"])
            or ("srv_api_client_sdk" in selected_ids)
            or ("srv_quickstart_integration" in selected_ids),
            "selected_ids": selected_ids,
            "priority_datasets": priority_datasets,
            "role_category": role_category,
        }
    )

    with _get_pool().connection() as conn:
        with conn.transaction():
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    INSERT INTO wtp_survey_sessions (
                        session_id,
                        institution_alias,
                        market_segment,
                        invitation_token,
                        respondent_role_category,
                        is_completed,
                        completed_at
                    )
                    VALUES (%s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
                    """,
                    (
                        session_id,
                        payload["alias"],
                        payload["segment"],
                        invitation_token,
                        payload["contact"],
                    ),
                )

                cur.execute(
                    """
                    INSERT INTO wtp_survey_responses (
                        response_id,
                        session_id,
                        institution_alias,
                        market_segment,
                        respondent_role_category,
                        package_code_evaluated,
                        manual_hours_per_month,
                        evaluated_intrinsic_value_usd,
                        price_too_cheap,
                        price_cheap,
                        price_expensive,
                        price_too_expensive,
                        nms_score_cheap,
                        nms_score_expensive,
                        selected_complementary_services,
                        qualitative_notes
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s::jsonb, %s
                    )
                    RETURNING response_id, submitted_at
                    """,
                    (
                        response_id,
                        session_id,
                        payload["alias"],
                        payload["segment"],
                        payload["contact"],
                        "DATAHUB-CORE",
                        payload["manualHours"],
                        payload["intrinsicValueUsd"],
                        payload["tooCheap"],
                        payload["cheap"],
                        payload["expensive"],
                        payload["tooExpensive"],
                        payload["nmsCheap"],
                        payload["nmsExpensive"],
                        services_json,
                        payload.get("qualitativeNotes") or "",
                    ),
                )
                row = cur.fetchone()
                return {
                    "response_id": row["response_id"],
                    "session_id": session_id,
                    "submitted_at": row["submitted_at"].isoformat(),
                }


def list_survey_responses() -> list[dict[str, Any]]:
    """Fetch all persisted WTP responses ordered by newest first."""
    with _get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    response_id,
                    institution_alias,
                    respondent_role_category,
                    market_segment,
                    manual_hours_per_month,
                    evaluated_intrinsic_value_usd,
                    price_too_cheap,
                    price_cheap,
                    price_expensive,
                    price_too_expensive,
                    nms_score_cheap,
                    nms_score_expensive,
                    selected_complementary_services,
                    qualitative_notes,
                    submitted_at
                FROM wtp_survey_responses
                ORDER BY submitted_at DESC
                """
            )
            rows = cur.fetchall()

    result: list[dict[str, Any]] = []
    for r in rows:
        services = r["selected_complementary_services"] or {}
        result.append(
            {
                "id": r["response_id"],
                "alias": r["institution_alias"],
                "contact": r["respondent_role_category"],
                "segment": r["market_segment"],
                "manualHours": float(r["manual_hours_per_month"]),
                "intrinsicValueUsd": float(r["evaluated_intrinsic_value_usd"]),
                "tooCheap": float(r["price_too_cheap"]),
                "cheap": float(r["price_cheap"]),
                "expensive": float(r["price_expensive"]),
                "tooExpensive": float(r["price_too_expensive"]),
                "nmsCheap": int(r["nms_score_cheap"]),
                "nmsExpensive": int(r["nms_score_expensive"]),
                "s3": bool(services.get("s3", False)),
                "tablero": bool(services.get("tablero", False)),
                "sdk": bool(services.get("sdk", False)),
                "selectedServiceIds": services.get("selected_ids", []),
                "priorityDatasets": services.get("priority_datasets", []),
                "roleCategory": services.get("role_category", ""),
                "qualitativeNotes": r["qualitative_notes"] or "",
                "submittedAt": r["submitted_at"].isoformat() if r["submitted_at"] else "",
            }
        )
    return result


def list_complementary_services(active_only: bool = True) -> list[dict[str, Any]]:
    """List complementary services from wtp_complementary_services_catalog."""
    sql = """
        SELECT
            service_id,
            service_code,
            service_name,
            setup_fee_usd,
            monthly_fee_usd,
            is_active,
            description,
            created_at
        FROM wtp_complementary_services_catalog
    """
    if active_only:
        sql += " WHERE is_active = TRUE"
    sql += " ORDER BY created_at ASC, service_code ASC"

    with _get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

    return [
        {
            "id": r["service_id"],
            "code": r["service_code"],
            "name": r["service_name"],
            "setupFeeUsd": float(r["setup_fee_usd"]),
            "monthlyFeeUsd": float(r["monthly_fee_usd"]),
            "isActive": bool(r["is_active"]),
            "description": r["description"] or "",
        }
        for r in rows
    ]


def create_complementary_service(payload: dict[str, Any]) -> dict[str, Any]:
    """Insert a new complementary service into the catalog."""
    service_id = f"srv_{uuid.uuid4().hex[:12]}"
    with _get_pool().connection() as conn:
        with conn.transaction():
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    INSERT INTO wtp_complementary_services_catalog (
                        service_id,
                        service_code,
                        service_name,
                        setup_fee_usd,
                        monthly_fee_usd,
                        is_active,
                        description
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING
                        service_id, service_code, service_name,
                        setup_fee_usd, monthly_fee_usd, is_active, description
                    """,
                    (
                        service_id,
                        payload["code"],
                        payload["name"],
                        payload["setupFeeUsd"],
                        payload["monthlyFeeUsd"],
                        payload["isActive"],
                        payload.get("description") or "",
                    ),
                )
                r = cur.fetchone()
    return {
        "id": r["service_id"],
        "code": r["service_code"],
        "name": r["service_name"],
        "setupFeeUsd": float(r["setup_fee_usd"]),
        "monthlyFeeUsd": float(r["monthly_fee_usd"]),
        "isActive": bool(r["is_active"]),
        "description": r["description"] or "",
    }


def update_complementary_service(service_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Update an existing complementary service."""
    with _get_pool().connection() as conn:
        with conn.transaction():
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    UPDATE wtp_complementary_services_catalog
                    SET
                        service_code = %s,
                        service_name = %s,
                        setup_fee_usd = %s,
                        monthly_fee_usd = %s,
                        is_active = %s,
                        description = %s
                    WHERE service_id = %s
                    RETURNING
                        service_id, service_code, service_name,
                        setup_fee_usd, monthly_fee_usd, is_active, description
                    """,
                    (
                        payload["code"],
                        payload["name"],
                        payload["setupFeeUsd"],
                        payload["monthlyFeeUsd"],
                        payload["isActive"],
                        payload.get("description") or "",
                        service_id,
                    ),
                )
                r = cur.fetchone()
    if not r:
        return None
    return {
        "id": r["service_id"],
        "code": r["service_code"],
        "name": r["service_name"],
        "setupFeeUsd": float(r["setup_fee_usd"]),
        "monthlyFeeUsd": float(r["monthly_fee_usd"]),
        "isActive": bool(r["is_active"]),
        "description": r["description"] or "",
    }


def delete_complementary_service(service_id: str) -> bool:
    """Delete a complementary service from the catalog."""
    with _get_pool().connection() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM wtp_complementary_services_catalog WHERE service_id = %s",
                    (service_id,),
                )
                return cur.rowcount > 0
