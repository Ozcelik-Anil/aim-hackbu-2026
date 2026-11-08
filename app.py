"""Question-first entry point for the guarded research agent."""
import os
from pathlib import Path

import streamlit as st

from research_agent import investigate

st.set_page_config(page_title="AgentGuard | Research", layout="wide")
css = Path(__file__).with_name("workspace.css").read_text(encoding="utf-8")
st.html(f"<style>{css}</style>")
st.html('<section class="cover"><div><h1>AgentGuard Research</h1><p>Ask a question. The assistant searches public sources, checks each excerpt and returns cited findings.</p></div></section>')
key = os.getenv("GEMINI_API_KEY")
if not key:
    key = st.text_input("Gemini API key for this local session", type="password", key="research_api_key")
st.caption("Searches up to six Wikipedia introductions and Crossref scholarly abstracts. Your question and source excerpts are processed by Gemini.")
with st.form("research"):
    question = st.text_input("Research question", max_chars=600, placeholder="How do passkeys protect users against phishing?")
    submitted = st.form_submit_button("Start research", type="primary")

if submitted:
    st.session_state.pop("research_result", None)
    if not key or not question.strip():
        st.warning("Enter a question and configure a Gemini key to start research.")
    else:
        with st.status("Research in progress", expanded=True) as status:
            try:
                sources, findings, warnings = investigate(question.strip(), key, status.write)
                st.session_state["research_result"] = question, sources, findings, warnings
                status.update(label="Research complete" if findings else "No supported answer found", state="complete" if findings else "error")
            except Exception:
                status.update(label="Research unavailable", state="error")
                st.error("The research service could not complete this request. Check model access and try again.")

if "research_result" in st.session_state:
    topic, sources, findings, warnings = st.session_state["research_result"]
    st.header("Research report")
    st.text(topic)
    for warning in dict.fromkeys(warnings):
        st.warning(warning)
    if not findings:
        st.info("There was insufficient checked evidence for a cited answer.")
    for finding in findings:
        st.text(finding.text + " " + " ".join(f"[{n}]" for n in finding.source_numbers))
    st.subheader("Sources and guard decisions")
    for source in sources:
        st.text(f"[{source['number']}] {source['title']} | {source['status']}")
        st.link_button(f"Open source {source['number']}", source["url"])
