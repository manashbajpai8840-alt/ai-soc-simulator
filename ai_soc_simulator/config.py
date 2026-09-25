"""
Central configuration for the AI SOC Simulator.
Everything is overridable via environment variables so you never
have to hardcode secrets into the source.
"""
import os

# --- Anthropic API -----------------------------------------------------
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
# Check https://docs.claude.com for the current list of model names —
# model availability/naming changes over time, so don't assume this
# string is still valid when you read this.
AI_MODEL = os.environ.get("SOC_AI_MODEL", "claude-sonnet-4-6")

# --- Response behaviour --------------------------------------------------
# SAFETY: by default nothing on your real system is touched. All
# "blocking"/"isolation" actions are simulated (printed + logged) unless
# you explicitly pass --live on the command line AND set this env var.
LIVE_RESPONSE = os.environ.get("SOC_LIVE_RESPONSE", "false").lower() == "true"

# How long a simulated/real IP block lasts, in seconds, before the
# dashboard marks it as "expired" (cosmetic only in simulate mode).
BLOCK_DURATION_SECONDS = int(os.environ.get("SOC_BLOCK_DURATION", "3600"))

# --- Detection tuning ------------------------------------------------
# Minimum number of failed logins from one IP within the window below
# before the prefilter flags it as brute-force-suspicious.
BRUTE_FORCE_THRESHOLD = int(os.environ.get("SOC_BRUTE_FORCE_THRESHOLD", "5"))
BRUTE_FORCE_WINDOW_SECONDS = int(os.environ.get("SOC_BRUTE_FORCE_WINDOW", "60"))

# Confidence (0-1) the AI must return before we treat something as a
# confirmed threat and trigger a response action.
AI_CONFIDENCE_THRESHOLD = float(os.environ.get("SOC_AI_CONFIDENCE_THRESHOLD", "0.7"))

# --- Storage -----------------------------------------------------------
DB_PATH = os.environ.get("SOC_DB_PATH", os.path.join(os.path.dirname(__file__), "soc.db"))
FORENSICS_DIR = os.environ.get(
    "SOC_FORENSICS_DIR", os.path.join(os.path.dirname(__file__), "forensic_reports")
)

# --- Log generation ------------------------------------------------------
# Seconds between each synthetic log event the generator emits.
GENERATOR_INTERVAL_SECONDS = float(os.environ.get("SOC_GEN_INTERVAL", "1.5"))
