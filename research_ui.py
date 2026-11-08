"""Question-first entry point for the guarded research agent."""
from html import escape
from pathlib import Path

import streamlit as st
from google.genai.errors import APIError
from pydantic import ValidationError

from research_agent import investigate
from team_config import team_key


css = Path(__file__).with_name("workspace.css").read_text(encoding="utf-8")
st.html(f"<style>{css}</style>")
st.html('<section class="cover"><div><h1>AgentGuard Research</h1><p>Ask a question. The assistant searches public sources, checks each excerpt and returns cited findings.</p></div></section>')
key = team_key("GEMINI_API_KEY")
backup_key = team_key("GEMINI_BACKUP_API_KEY")
st.caption("Searches Wikipedia and scholarly abstracts. Your question and source excerpts are processed by Gemini.")
with st.form("research"):
    question = st.text_input("Research question", max_chars=600, placeholder="How do passkeys protect users against phishing?")
    submitted = st.form_submit_button("Start research", type="primary")

if submitted:
    st.session_state.pop("research_result", None)
    if not key:
        st.warning("The team's research service is currently unavailable.")
    elif not question.strip():
        st.warning("Enter a research question.")
    else:
        with st.status("Research in progress", expanded=False) as status:
            try:
                sources, findings, warnings = investigate(question.strip(), key, status.write, backup_key)
                st.session_state["research_result"] = question, sources, findings, warnings
                label = "Research complete" if findings else "No supported answer found"
                if findings and any("quota reached" in w for w in warnings):
                    label = "Partial research"
                status.update(label=label, state="complete" if findings else "error")
            except APIError as error:
                status.update(label="Gemini request failed", state="error", expanded=True)
                st.error(f"Gemini returned HTTP {error.code}. " + ("The model quota or rate limit was reached." if error.code == 429 else "Check model availability and account access."))
            except ValidationError:
                status.update(label="Incomplete model response", state="error", expanded=True)
                st.error("Gemini did not return a valid research plan or answer. Try again.")
            except Exception:
                status.update(label="Research unavailable", state="error", expanded=True)
                st.error("The research service could not complete this request. Check model access and try again.")

if "research_result" in st.session_state:
    topic, sources, findings, warnings = st.session_state["research_result"]
    st.html(f"<h2>{escape(topic)}</h2>")
    if findings and any("quota reached" in w for w in warnings):
        st.warning("Partial research: Gemini quota was reached. Only previously checked source excerpts are shown.")
    if not findings:
        for warning in dict.fromkeys(warnings):
            st.warning(warning)
        st.info("There was insufficient checked evidence for a cited answer.")
    by_number = {source["number"]: source for source in sources}
    for finding in findings:
        if heading := getattr(finding, "heading", ""):
            st.html(f"<h3>{escape(heading)}</h3>")
        links = [
            f'<a href="{escape(by_number[n]["url"], quote=True)}" target="_blank" rel="noopener noreferrer"'
            f' aria-label="Source {n}">[{n}]</a>' for n in dict.fromkeys(finding.source_numbers)
        ]
        st.html(f"<p>{escape(finding.text)} {' '.join(links)}</p>")
    with st.expander(f"Sources and guard decisions ({len(sources)})"):
        for warning in dict.fromkeys(warnings):
            st.warning(warning)
        for source in sources:
            st.text(f"[{source['number']}] {source['title']} | {source['status']}")
            st.link_button(f"Open source {source['number']}", source["url"])
