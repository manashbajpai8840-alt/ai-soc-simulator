"""
Orchestrator. Run this in one terminal; run `streamlit run dashboard.py`
in another to watch it live.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python main.py                 # simulated responses (safe default)
    python main.py --live          # actually run iptables / SIGSTOP
                                    # (needs root for iptables; use with care)
    python main.py --events 100    # stop after N generated events
    python main.py --fast          # shorter interval between events
"""
import argparse
import sys
import time

import config
import db
import log_generator
from ai_analyzer import AIAnalyzer
from detector import is_suspicious
from responder import block_ip, generate_forensic_report, isolate_process


def run(max_events=None, live=False, interval=None):
    db.init_db()
    try:
        analyzer = AIAnalyzer()
    except RuntimeError as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        sys.exit(1)

    interval = interval if interval is not None else config.GENERATOR_INTERVAL_SECONDS
    sticky_ips = {}
    count = 0

    mode_label = "LIVE (real iptables/process actions)" if live else "SIMULATED (safe, no system changes)"
    print(f"=== AI SOC Simulator starting — response mode: {mode_label} ===")
    print(f"DB: {config.DB_PATH}")
    print(f"Model: {config.AI_MODEL}\n")

    try:
        while max_events is None or count < max_events:
            event = log_generator.next_event(sticky_ips)
            flagged = is_suspicious(event)
            event_id = db.insert_event(
                event["source_ip"], event["category"], event["raw_log"], flagged
            )

            tag = "[FLAGGED]" if flagged else "[benign]"
            print(f"{tag} {event['category']:14s} {event['source_ip']:15s} {event['raw_log'][:90]}")

            if flagged and not db.is_ip_blocked(event["source_ip"]):
                ai_result = analyzer.analyze(event)
                db.update_ai_verdict(
                    event_id,
                    ai_result.get("verdict"),
                    ai_result.get("confidence"),
                    ai_result.get("reasoning"),
                )

                is_threat = (
                    ai_result.get("verdict") == "real_threat"
                    and ai_result.get("confidence", 0) >= config.AI_CONFIDENCE_THRESHOLD
                )

                if is_threat:
                    action = ai_result.get("recommended_action", "monitor")
                    print(
                        f"    -> AI: REAL THREAT ({ai_result.get('threat_type')}, "
                        f"conf={ai_result.get('confidence'):.2f}) -> action={action}"
                    )

                    response_result = {"mode": "simulated", "detail": "no action taken"}
                    if action == "block_ip":
                        response_result = block_ip(event["source_ip"], live=live)
                        db.add_blocked_ip(event["source_ip"], response_result["mode"])
                    elif action == "isolate_process":
                        response_result = isolate_process(
                            None, event["category"], live=live
                        )

                    report_path = generate_forensic_report(event, ai_result, response_result)
                    db.update_response(
                        event_id,
                        action=action,
                        mode=response_result["mode"],
                        forensic_report_path=report_path,
                    )
                    print(f"    -> response: {response_result['detail']}")
                    print(f"    -> forensic report: {report_path}")
                else:
                    print(
                        f"    -> AI: false positive / low confidence "
                        f"(conf={ai_result.get('confidence', 0):.2f}) — no action"
                    )

            count += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-driven SOC simulator")
    parser.add_argument("--live", action="store_true", help="Actually run iptables/process actions")
    parser.add_argument("--events", type=int, default=None, help="Stop after N events")
    parser.add_argument("--fast", action="store_true", help="Use a 0.3s interval instead of the default")
    args = parser.parse_args()

    run(
        max_events=args.events,
        live=args.live or config.LIVE_RESPONSE,
        interval=0.3 if args.fast else None,
    )
