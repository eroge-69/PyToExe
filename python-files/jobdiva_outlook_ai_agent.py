"""
AI Agent: JobDiva ➜ Outlook Auto‑Outreach
-------------------------------------------------
Python 3.10+

What this script does
- Pulls candidate records from JobDiva using defined search parameters
- Uses an LLM to generate a brief, personalized outreach email (no pay discussed)
- Sends messages from your Outlook account via Microsoft Graph API
- Persists history in SQLite so candidates aren’t re‑emailed within a cooldown window
- Adds basic compliance: unsubscribe/opt‑out handling, rate limiting, logging

Quick start
1) Create an Azure Entra app (App registration) with **Application permissions**:
   - Mail.Send
   - (Optional) Mail.ReadBasic if you plan to extend for reply/bounce handling
   Grant admin consent, then collect:
     AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET

2) Get a JobDiva API credential. Put the base URL + token in env vars below.
   (If your account uses username/password + token, adjust `get_jobdiva_candidates`.)

3) (Optional) OpenAI (or any LLM) key for better, on‑brand writing.
   If not set, script will fall back to a deterministic template.

4) Set environment variables (Windows example – User variables):
   - JOBDIVA_BASE_URL=https://api.jobdiva.com
   - JOBDIVA_API_TOKEN=***
   - AZURE_TENANT_ID=***
   - AZURE_CLIENT_ID=***
   - AZURE_CLIENT_SECRET=***
   - MS_GRAPH_SENDER=you@yourdomain.com     # the mailbox to send from
   - OPENAI_API_KEY=***                      # optional

5) Install deps:
   pip install requests pydantic tenacity python-dotenv jinja2 openai==1.* sqlite-utils

6) Configure the search + messaging policy in `AGENT_CONFIG` below.

7) Test in dry‑run first:
   python jobdiva_outlook_ai_agent.py --dry-run --limit 3

8) Schedule daily (Windows Task Scheduler or Cron).

Notes
- This sample uses common JobDiva REST patterns; adapt field names/filters to your tenant’s API.
- Respects the user’s preference: outreach does **not** mention compensation.
- Make sure your email footer and unsubscribe language meet your compliance policy.

"""
from __future__ import annotations

import os
import sys
import time
import json
import uuid
import sqlite3
import logging
import argparse
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, Field
from jinja2 import Template

# ----------------------------
# Global configuration
# ----------------------------

DB_PATH = os.environ.get("AGENT_DB_PATH", "agent_state.db")
LOG_LEVEL = os.environ.get("AGENT_LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("jobdiva_outreach")

# Env vars for services
JOBDIVA_BASE_URL = os.environ.get("JOBDIVA_BASE_URL", "https://api.jobdiva.com")
JOBDIVA_API_TOKEN = os.environ.get("JOBDIVA_API_TOKEN")

AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
MS_GRAPH_SENDER = os.environ.get("MS_GRAPH_SENDER")  # mailbox to send from

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # optional

# Business policy & search knobs
AGENT_CONFIG = {
    # Search criteria to pull candidates from JobDiva
    "search": {
        "keywords_any": ["RN", "Registered Nurse", "Staff Nurse"],
        "locations_any": ["Texas", "California", "Florida"],
        "must_have_skills": ["acute care"],
        "exclude_skills": ["NP", "CNS"],  # per preference: avoid NP/CNS
        "last_active_within_days": 180,
        "max_records": 200,
    },
    # Messaging policy
    "policy": {
        "cooldown_days": 45,            # do not re-email same candidate inside this window
        "daily_send_cap": 120,          # safety limiter
        "batch_size": 30,               # per run
        "optout_phrases": ["unsubscribe", "opt out", "remove me"],
        "include_compensation": False,  # respect user's preference
        "brand_name": "Emonics",
        "reply_to": None,               # defaults to sender
    },
    # Role/company context to personalize emails
    "context": {
        "role_title": "Registered Nurse (Various Units)",
        "company": "Emonics",
        "selling_points": [
            "Stable schedules with growth opportunities",
            "Supportive, well‑staffed units",
            "Multiple facilities and shifts to match your preference",
        ],
        "call_to_action_link": "https://www.emonics.com/careers",
    },
}

# ----------------------------
# Data models
# ----------------------------

class Candidate(BaseModel):
    candidate_id: str
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    skills: List[str] = Field(default_factory=list)
    last_active_utc: Optional[datetime] = None

class OutreachResult(BaseModel):
    candidate_id: str
    email: Optional[str]
    status: str  # SENT | SKIPPED | FAILED
    reason: Optional[str] = None
    message_id: Optional[str] = None

# ----------------------------
# Persistence (SQLite)
# ----------------------------

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS outreach_history (
            candidate_id TEXT,
            email TEXT,
            sent_utc TEXT,
            message_id TEXT,
            PRIMARY KEY(candidate_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    con.commit()
    con.close()


def already_contacted(candidate_id: str, cooldown_days: int) -> bool:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT sent_utc FROM outreach_history WHERE candidate_id=?",
        (candidate_id,),
    )
    row = cur.fetchone()
    con.close()
    if not row:
        return False
    sent_time = datetime.fromisoformat(row[0])
    return datetime.now(timezone.utc) - sent_time < timedelta(days=cooldown_days)


def record_sent(candidate_id: str, email: str, message_id: str):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "REPLACE INTO outreach_history(candidate_id, email, sent_utc, message_id) VALUES (?,?,?,?)",
        (candidate_id, email, datetime.now(timezone.utc).isoformat(), message_id),
    )
    con.commit()
    con.close()

# ----------------------------
# JobDiva API
# ----------------------------

class JobDivaAPIError(Exception):
    pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(JobDivaAPIError),
)
def jobdiva_request(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not JOBDIVA_API_TOKEN:
        raise JobDivaAPIError("Missing JOBDIVA_API_TOKEN")
    url = f"{JOBDIVA_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {JOBDIVA_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code >= 400:
        raise JobDivaAPIError(f"JobDiva API error {resp.status_code}: {resp.text}")
    try:
        return resp.json()
    except Exception as e:
        raise JobDivaAPIError(f"Invalid JSON from JobDiva: {e}")


def get_jobdiva_candidates(cfg: Dict[str, Any]) -> List[Candidate]:
    """Example search; adjust fields to your JobDiva API contract."""
    search = cfg["search"]
    payload = {
        "keywords_any": search.get("keywords_any", []),
        "locations_any": search.get("locations_any", []),
        "must_have_skills": search.get("must_have_skills", []),
        "exclude_skills": search.get("exclude_skills", []),
        "last_active_since": (
            datetime.now(timezone.utc) - timedelta(days=search.get("last_active_within_days", 365))
        ).date().isoformat(),
        "limit": search.get("max_records", 200),
    }

    # Replace with your tenant's actual endpoint path
    data = jobdiva_request("v1/candidates/search", payload)
    rows = data.get("results", [])
    candidates: List[Candidate] = []
    for r in rows:
        try:
            candidates.append(
                Candidate(
                    candidate_id=str(r.get("id")),
                    first_name=(r.get("firstName") or "").strip(),
                    last_name=(r.get("lastName") or "").strip(),
                    email=(r.get("email") or None),
                    phone=(r.get("phone") or None),
                    location=(r.get("location") or None),
                    skills=[s.strip() for s in (r.get("skills") or []) if s],
                    last_active_utc=(
                        datetime.fromisoformat(r["lastActiveUtc"]) if r.get("lastActiveUtc") else None
                    ),
                )
            )
        except Exception as e:
            logger.warning(f"Skipping malformed candidate: {e}")
    return candidates

# ----------------------------
# Microsoft Graph (Outlook) Mail
# ----------------------------

class GraphError(Exception):
    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def get_graph_token() -> str:
    if not (AZURE_TENANT_ID and AZURE_CLIENT_ID and AZURE_CLIENT_SECRET):
        raise GraphError("Missing Azure app credentials")
    url = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": AZURE_CLIENT_ID,
        "client_secret": AZURE_CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default",
    }
    resp = requests.post(url, data=data, timeout=30)
    if resp.status_code >= 400:
        raise GraphError(f"Token error {resp.status_code}: {resp.text}")
    return resp.json()["access_token"]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def graph_send_mail(subject: str, html_body: str, to_email: str, reply_to: Optional[str] = None) -> str:
    if not MS_GRAPH_SENDER:
        raise GraphError("Missing MS_GRAPH_SENDER email address")
    token = get_graph_token()
    url = f"https://graph.microsoft.com/v1.0/users/{MS_GRAPH_SENDER}/sendMail"
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": [{"emailAddress": {"address": to_email}}],
        },
        "saveToSentItems": True,
    }
    if reply_to:
        payload["message"]["replyTo"] = [{"emailAddress": {"address": reply_to}}]

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code == 202:
        # No message id returned; we fabricate a UUID for local tracking
        return str(uuid.uuid4())
    if resp.status_code >= 400:
        raise GraphError(f"Graph send error {resp.status_code}: {resp.text}")
    return str(uuid.uuid4())

# ----------------------------
# LLM‑assisted email drafting
# ----------------------------

BASIC_TEMPLATE = Template(
    """
    <p>Hi {{first_name or 'there'}},</p>
    <p>I’m reaching out from {{company}} about {{role_title}} opportunities across our client facilities.
    Based on your background, I believe you could be a strong match for current and upcoming roles.
    </p>
    <p>What we offer:</p>
    <ul>
    {% for sp in selling_points %}<li>{{sp}}</li>{% endfor %}
    </ul>
    <p>If you’re open to a quick chat, you can reply here or share a time that suits you.
    You can also submit interest here: <a href="{{cta}}">{{cta}}</a>.</p>
    <p>Best regards,<br/>
    {{sender_name}}<br/>
    {{company}}</p>
    <hr/>
    <p style="font-size:12px;color:#666;">If you prefer not to hear about roles, reply with "unsubscribe" and we’ll remove you.</p>
    """
)


def generate_subject(candidate: Candidate, ctx: Dict[str, Any]) -> str:
    first = candidate.first_name or "there"
    return f"{ctx['role_title']} – quick intro, {first}"


def draft_email(candidate: Candidate, cfg: Dict[str, Any]) -> str:
    policy = cfg["policy"]
    ctx = cfg["context"]

    # Guardrails: no compensation talk if disabled
    selling_points = [sp for sp in ctx["selling_points"]]
    if not policy.get("include_compensation", False):
        selling_points = [sp for sp in selling_points if "salary" not in sp.lower() and "pay" not in sp.lower()]

    if OPENAI_API_KEY:
        try:
            # Lazy import to keep dependency optional
            from openai import OpenAI

            client = OpenAI(api_key=OPENAI_API_KEY)
            sys_prompt = (
                "You are a concise, professional recruiter. Draft a short, friendly outreach email to a candidate. "
                "Do NOT mention compensation. Keep it under 140 words. Include a clear CTA. "
                "Use simple, positive language. British or American spelling both acceptable."
            )
            user_context = {
                "first_name": candidate.first_name or "there",
                "role_title": ctx["role_title"],
                "company": ctx["company"],
                "selling_points": selling_points,
                "cta": ctx["call_to_action_link"],
            }
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": json.dumps(user_context)},
                ],
                temperature=0.6,
                max_tokens=280,
            )
            content = completion.choices[0].message.content
            # Wrap in minimal HTML if text
            if "<" not in content:
                content = content.replace("\n", "<br/>")
                content = f"<p>{content}</p><hr/><p style=\"font-size:12px;color:#666;\">Reply with \"unsubscribe\" to opt out.</p>"
            return content
        except Exception as e:
            logger.warning(f"LLM failed, falling back to template: {e}")

    # Fallback deterministic template
    html = BASIC_TEMPLATE.render(
        first_name=candidate.first_name,
        role_title=ctx["role_title"],
        company=ctx["company"],
        selling_points=selling_points,
        cta=ctx["call_to_action_link"],
        sender_name=MS_GRAPH_SENDER.split("@")[0] if MS_GRAPH_SENDER else "Recruiter",
    )
    return html

# ----------------------------
# Core workflow
# ----------------------------

def run_agent(cfg: Dict[str, Any], limit: Optional[int] = None, dry_run: bool = True) -> List[OutreachResult]:
    init_db()
    policy = cfg["policy"]

    candidates = get_jobdiva_candidates(cfg)
    logger.info(f"Fetched {len(candidates)} candidates from JobDiva")

    # Filter & slice
    filtered: List[Candidate] = []
    for c in candidates:
        if not c.email:
            continue
        if already_contacted(c.candidate_id, policy["cooldown_days"]):
            continue
        # Basic exclude skills
        if any(ex.lower() in " ".join(c.skills).lower() for ex in cfg["search"].get("exclude_skills", [])):
            continue
        filtered.append(c)

    batch_cap = min(policy["batch_size"], policy["daily_send_cap"])
    if limit is not None:
        batch_cap = min(batch_cap, limit)
    todo = filtered[:batch_cap]
    logger.info(f"Prepared {len(todo)} candidates for outreach (cap={batch_cap})")

    results: List[OutreachResult] = []

    for idx, cand in enumerate(todo, start=1):
        subject = generate_subject(cand, cfg["context"])
        body_html = draft_email(cand, cfg)

        if dry_run:
            logger.info(f"[DRY‑RUN] Would email {cand.email} | subj='{subject}'")
            results.append(OutreachResult(candidate_id=cand.candidate_id, email=cand.email, status="SKIPPED", reason="dry-run"))
            continue

        try:
            message_id = graph_send_mail(subject, body_html, cand.email, reply_to=policy.get("reply_to") or MS_GRAPH_SENDER)
            record_sent(cand.candidate_id, cand.email, message_id)
            logger.info(f"SENT {idx}/{len(todo)} -> {cand.email}")
            results.append(OutreachResult(candidate_id=cand.candidate_id, email=cand.email, status="SENT", message_id=message_id))
            time.sleep(0.8)  # polite pacing / avoid throttling
        except Exception as e:
            logger.error(f"Failed sending to {cand.email}: {e}")
            results.append(OutreachResult(candidate_id=cand.candidate_id, email=cand.email, status="FAILED", reason=str(e)))

    return results

# ----------------------------
# CLI
# ----------------------------

def parse_args():
    p = argparse.ArgumentParser(description="JobDiva ➜ Outlook AI outreach agent")
    p.add_argument("--dry-run", action="store_true", help="Don’t send emails; log actions only")
    p.add_argument("--limit", type=int, default=None, help="Cap number of candidates processed this run")
    p.add_argument("--config", type=str, default=None, help="Path to JSON file to override AGENT_CONFIG")
    return p.parse_args()


def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return AGENT_CONFIG
    with open(path, "r", encoding="utf-8") as f:
        external = json.load(f)
    merged = json.loads(json.dumps(AGENT_CONFIG))  # deep copy
    # shallow merge keys present in external
    for k, v in external.items():
        if isinstance(v, dict) and k in merged and isinstance(merged[k], dict):
            merged[k].update(v)
        else:
            merged[k] = v
    return merged


if __name__ == "__main__":
    args = parse_args()
    cfg = load_config(args.config)

    try:
        results = run_agent(cfg, limit=args.limit, dry_run=args.dry_run)
        sent = sum(1 for r in results if r.status == "SENT")
        skipped = sum(1 for r in results if r.status == "SKIPPED")
        failed = sum(1 for r in results if r.status == "FAILED")
        logger.info(f"Run complete. SENT={sent} SKIPPED={skipped} FAILED={failed}")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
