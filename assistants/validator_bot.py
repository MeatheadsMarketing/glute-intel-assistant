# assistants/validator_bot.py

import os
import pandas as pd
from datetime import datetime

DATA_DIR = "data"
UPLOADS_DIR = "uploads"
LOGS_DIR = os.path.join(DATA_DIR, "logs")
TAG_LOG = os.path.join(DATA_DIR, "tag_logs.csv")
PLAN_LOG = os.path.join(DATA_DIR, "plan_logs.csv")


def get_sessions():
    """Return all session folders and log file basenames"""
    session_ids = []
    if os.path.exists(UPLOADS_DIR):
        session_ids = [d for d in os.listdir(UPLOADS_DIR) if os.path.isdir(os.path.join(UPLOADS_DIR, d))]
    return sorted(session_ids)


def validate_session(session_id):
    """Check if a session has images, tag history, and plan history"""
    issues = []
    session_path = os.path.join(UPLOADS_DIR, session_id)
    log_path = os.path.join(LOGS_DIR, f"{session_id}_log.txt")

    # Check image uploads
    if not os.path.exists(session_path) or not any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(session_path)):
        issues.append("❌ Missing or invalid image folder")

    # Check tag logs
    if os.path.exists(TAG_LOG):
        tag_df = pd.read_csv(TAG_LOG)
        if session_id not in tag_df.session_id.values:
            issues.append("⚠️ No tags found in tag_logs.csv")
    else:
        issues.append("⚠️ tag_logs.csv not found")

    # Check plan logs
    if os.path.exists(PLAN_LOG):
        plan_df = pd.read_csv(PLAN_LOG)
        if session_id not in plan_df.session_id.values:
            issues.append("⚠️ No plan generated or archived")
    else:
        issues.append("⚠️ plan_logs.csv not found")

    # Check session log
    if not os.path.exists(log_path):
        issues.append("⚠️ No session log file found")

    return issues if issues else ["✅ Session is complete"]


def validate_all_sessions():
    """Validate every session currently stored"""
    session_ids = get_sessions()
    report = {}
    for sid in session_ids:
        report[sid] = validate_session(sid)
    return report

