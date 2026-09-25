"""
Sends a prefilter-flagged log entry to the Anthropic API and asks it to
decide, in structured JSON, whether it's a real threat or a false
positive — this is the piece that replaces brittle regex-only rules
with judgment that can weigh context (e.g. "5 failed logins from an
internal IP during a known migration" vs "5 failed logins from a
Tor exit node against the admin account").

Requires ANTHROPIC_API_KEY to be set in the environment. Get a key at
https://console.anthropic.com/ and see https://docs.claude.com for the
current model list / SDK docs.

MOCK MODE: If ANTHROPIC_API_KEY is not set, this will use fake verdicts
for demonstration purposes.
"""
import json
import os

try:
    import anthropic # type: ignore
except ImportError:
    anthropic = None

import config

SYSTEM_PROMPT = """You are a SOC (Security Operations Center) triage analyst.
You will be given ONE flagged log line plus some brief context. Decide whether
it represents a REAL security threat or a FALSE POSITIVE (benign activity that
merely matched a heuristic pattern).

Respond with ONLY a JSON object, no other text, no markdown fences:
{
  "verdict": "real_threat" | "false_positive",
  "confidence": <float 0.0-1.0>,
  "threat_type": "brute_force" | "sql_injection" | "malware_c2" | "other" | "none",
  "reasoning": "<one or two sentence explanation, plain text>",
  "recommended_action": "block_ip" | "isolate_process" | "monitor" | "none"
}"""


class AIAnalyzer:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or config.ANTHROPIC_API_KEY
        self.model = model or config.AI_MODEL
        self.use_mock = not self.api_key
        
        if not self.use_mock:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            print("[INFO] Running in MOCK mode (no API key) — using simulated threat verdicts")

    def analyze(self, event: dict) -> dict:
        """
        event: dict with keys category, source_ip, raw_log (as stored in db.py)
        Returns a dict matching the JSON schema in SYSTEM_PROMPT, with
        safe fallback values if parsing fails.
        """
        if self.use_mock:
            return self._analyze_mock(event)
        
        user_prompt = (
            f"Category flagged by prefilter: {event['category']}\n"
            f"Source IP: {event['source_ip']}\n"
            f"Raw log line: {event['raw_log']}\n\n"
            "Classify this."
        )
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = "".join(
                block.text for block in resp.content if getattr(block, "type", None) == "text"
            ).strip()
            text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            data = json.loads(text)
            data.setdefault("confidence", 0.5)
            data.setdefault("threat_type", "other")
            data.setdefault("recommended_action", "monitor")
            data.setdefault("reasoning", "")
            return data
        except Exception as e:  # noqa: BLE001 — we want ANY failure to degrade safely
            return {
                "verdict": "false_positive",
                "confidence": 0.0,
                "threat_type": "none",
                "reasoning": f"Analyzer error, defaulting to no action: {e}",
                "recommended_action": "none",
            }

    def _analyze_mock(self, event: dict) -> dict:
        """Mock analyzer for running without an API key."""
        import random
        
        category = event.get("category", "")
        
        # Simulate realistic threat analysis based on category
        if "brute_force" in category:
            verdict = random.choice(["real_threat", "real_threat", "false_positive"])
            confidence = random.uniform(0.75, 0.95) if verdict == "real_threat" else random.uniform(0.4, 0.6)
            threat_type = "brute_force"
            action = "block_ip" if verdict == "real_threat" else "monitor"
            reasoning = "Multiple failed login attempts detected from same source IP in short time window."
        elif "sql_injection" in category:
            verdict = random.choice(["real_threat", "real_threat", "real_threat", "false_positive"])
            confidence = random.uniform(0.8, 0.98) if verdict == "real_threat" else random.uniform(0.3, 0.5)
            threat_type = "sql_injection"
            action = "block_ip" if verdict == "real_threat" else "monitor"
            reasoning = "SQL injection pattern detected in HTTP request parameter."
        elif "malware_c2" in category:
            verdict = random.choice(["real_threat", "real_threat", "real_threat", "false_positive"])
            confidence = random.uniform(0.85, 0.99) if verdict == "real_threat" else random.uniform(0.2, 0.4)
            threat_type = "malware_c2"
            action = "isolate_process" if verdict == "real_threat" else "monitor"
            reasoning = "Suspicious outbound connection pattern consistent with C2 beacon activity."
        else:
            verdict = random.choice(["real_threat", "false_positive", "false_positive"])
            confidence = random.uniform(0.5, 0.75) if verdict == "real_threat" else random.uniform(0.3, 0.6)
            threat_type = "other"
            action = "monitor"
            reasoning = "Event matched prefilter rules but requires investigation."
        
        return {
            "verdict": verdict,
            "confidence": round(confidence, 2),
            "threat_type": threat_type,
            "reasoning": reasoning,
            "recommended_action": action,
        }
