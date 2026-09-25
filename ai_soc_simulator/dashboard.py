"""
Live dashboard. Run with:
    streamlit run dashboard.py

Reads from the same SQLite DB that main.py writes to, so run main.py
in another terminal first (or alongside).
"""
import time

import pandas as pd
import streamlit as st

import config
import db

st.set_page_config(page_title="AI SOC Simulator", layout="wide", page_icon="🛡️")
db.init_db()

st.title("🛡️ AI SOC Simulator — Live Dashboard")
mode = "🔴 LIVE responses" if config.LIVE_RESPONSE else "🟢 Simulated responses (safe)"
st.caption(f"Response mode: **{mode}**  ·  Model: `{config.AI_MODEL}`  ·  DB: `{config.DB_PATH}`")

placeholder = st.empty()
refresh_seconds = st.sidebar.slider("Auto-refresh interval (s)", 1, 10, 3)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "Run the generator/analyzer in another terminal:\n\n"
    "```\nexport ANTHROPIC_API_KEY=sk-ant-...\npython main.py\n```"
)

while True:
    with placeholder.container():
        stats = db.get_stats()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total events", stats["total_events"])
        c2.metric("Flagged by prefilter", stats["prefilter_flagged"])
        c3.metric("Confirmed threats", stats["confirmed_threats"])
        c4.metric("False positives", stats["false_positives"])
        c5.metric("Active IP blocks", stats["active_blocks"])

        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.subheader("Threats by category")
            if stats["threats_by_category"]:
                cat_df = pd.DataFrame(
                    list(stats["threats_by_category"].items()), columns=["category", "count"]
                ).set_index("category")
                st.bar_chart(cat_df)
            else:
                st.info("No confirmed threats yet.")

        with col_right:
            st.subheader("Active IP blocks")
            blocks = db.get_active_blocks()
            if blocks:
                st.dataframe(pd.DataFrame(blocks), hide_index=True, use_container_width=True)
            else:
                st.info("No IPs currently blocked.")

        st.subheader("Recent events")
        events = db.get_recent_events(limit=100)
        if events:
            df = pd.DataFrame(events)
            df["ts"] = pd.to_datetime(df["ts"], unit="s")
            df = df[
                [
                    "ts",
                    "category",
                    "source_ip",
                    "prefilter_flagged",
                    "ai_verdict",
                    "ai_confidence",
                    "response_action",
                    "response_mode",
                    "raw_log",
                ]
            ]

            def highlight(row):
                if row["ai_verdict"] == "real_threat":
                    return ["background-color: #ffe0e0"] * len(row)
                if row["ai_verdict"] == "false_positive":
                    return ["background-color: #fffbe0"] * len(row)
                return [""] * len(row)

            st.dataframe(
                df.style.apply(highlight, axis=1),
                hide_index=True,
                use_container_width=True,
                height=500,
            )
        else:
            st.info("No events yet — start `python main.py` in another terminal.")

    time.sleep(refresh_seconds)
    st.rerun()
