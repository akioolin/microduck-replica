"""Read-only startup diagnostics. These observations never establish motion readiness."""
import math
import re

from .estop import STARTING_PHASES

OBSERVATION_MAX_AGE_MS = 3000
TELEMETRY = ("position_raw", "speed_raw", "load_raw", "current_raw", "volts", "temperature_c")
_CALIBRATION_ERROR = re.compile(r"calibrat|motion_enabled|IMU mounting", re.I)


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _age(value):
    return value if _number(value) and value >= 0 else None


def startup_wait(bus):
    """Describe the actual startup wait, keeping unknown bus failures generic."""
    if not isinstance(bus, dict) or bus.get("phase") not in STARTING_PHASES:
        return None
    error = str(bus.get("error") or "")
    if _CALIBRATION_ERROR.search(error):
        return None
    native = bus.get("native") if isinstance(bus.get("native"), dict) else {}
    if re.search(r"\bimu(?:\s*200)?\b", error, re.I):
        source = native.get("imu_source")
        source = source if isinstance(source, str) and source else None
        return {"kind": "imu", "text": "等待 IMU 数据" + (f"（来源：{source}）" if source else ""),
                "source": source}
    if bus.get("phase") == "waiting_for_bus":
        return {"kind": "bus", "text": "等待总线设备响应", "source": None}
    return None


def servo_observations(bus, *, present, bus_age_s, bus_error=None):
    """Normalize native startup evidence; add all three ages before trusting a row.

    Returning None outside startup preserves the existing motion/commissioning path.
    Within startup an empty/expired result is unknown, never zero responding servos.
    """
    if not isinstance(bus, dict) or bus.get("phase") not in STARTING_PHASES:
        return None
    native = bus.get("native") if isinstance(bus.get("native"), dict) else {}
    obs = native.get("servo_observations")
    obs = obs if isinstance(obs, dict) else {}
    receipt_ms = None if _age(bus_age_s) is None else bus_age_s * 1000
    snapshot_ms = _age(obs.get("age_ms"))
    usable = (present is True and bus_error is None and receipt_ms is not None
              and snapshot_ms is not None and obs.get("attempted") is True)
    base_age = receipt_ms + snapshot_ms if usable else None
    rows = []
    for row in obs.get("rows") if isinstance(obs.get("rows"), list) else []:
        if not isinstance(row, dict) or not isinstance(row.get("id"), int) or isinstance(row.get("id"), bool):
            continue
        ages = {key: None if base_age is None or _age(row.get(key)) is None else base_age + row[key]
                for key in ("check_age_ms", "reply_age_ms", "feedback_age_ms")}
        checked = ages["check_age_ms"] is not None and ages["check_age_ms"] < OBSERVATION_MAX_AGE_MS
        replied = ages["reply_age_ms"] is not None and ages["reply_age_ms"] < OBSERVATION_MAX_AGE_MS
        responding = row.get("responding") if checked and isinstance(row.get("responding"), bool) else None
        if responding is True and not replied:
            responding = None
        feedback = (responding is True and ages["feedback_age_ms"] is not None
                    and ages["feedback_age_ms"] < OBSERVATION_MAX_AGE_MS)
        rows.append({"id": row["id"], "name": row.get("name"), "responding": responding,
                     "feedback_fresh": feedback, **ages,
                     **{key: row.get(key) if feedback and _number(row.get(key)) else None for key in TELEMETRY}})
    known = any(row["responding"] is not None for row in rows)
    return {"rows": rows, "online": sum(row["responding"] is True for row in rows) if known else None}
