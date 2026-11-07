"""Study Guard UI. Untrusted content is displayed as plain text only."""

import os
import json
from pathlib import Path

import streamlit as st
from google.genai.errors import APIError

from guard import GuardResult, MAX_PAGE_CHARS, analyze_page, run_action
from study_site import SAMPLE_PAGE, SAMPLE_RESULT, read_sample_site

STUDENT_TASK = "Collect lesson notes about binary search from a third-party study page."

st.set_page_config(page_title="AIM | AgentGuard", page_icon="🛡️", layout="wide")
stylesheet = Path(__file__).with_name("workspace.css").read_text(encoding="utf-8")
st.html(f"<style>{stylesheet}</style>")
st.html("""
<nav class="mast" aria-label="Workspace"><b><span class="symbol" aria-hidden="true"></span>AgentGuard</b>
<div><a href="#inspection">Inspection</a><a href="#evaluation">Evaluation</a></div><small>TEAM AIM</small></nav>
<section class="cover"><div><h1>Inspect untrusted<br>web content.</h1>
<p>Find instructions that exceed the student's permissions. Return the lesson notes the student asked for.</p></div>
<div class="diagram" role="img" aria-label="Illustration of three page layers separated by a security filter">
<div class="layer lower"></div><div class="layer filter"></div><div class="layer upper">
<i></i><i></i><i></i></div><div class="diagram-label">READ-ONLY FILTER</div></div></section>
""")
st.html(f'<div class="request" id="inspection"><strong>Student request</strong><span>{STUDENT_TASK}</span></div>')

left, right = st.columns([1, 1.12], gap="medium")
with left:
    st.header("Source page", anchor=False)
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    mode = st.radio("Inspection mode", ["Live Gemini", "Offline example"], index=0 if has_key else 1, horizontal=True)
    if mode == "Offline example":
        st.caption("Replays the sample verdict locally. Use Live Gemini for custom pages.")
    else:
        st.caption("Inspection sends page text to Gemini. Use fictional data.")
        if not has_key:
            st.warning("Live mode needs GEMINI_API_KEY configured on the server.")

    sample = st.button("Load Sample Study Site with Trap", width="stretch")
    load_failed = False
    if sample:
        # Clear first: even a sample fetch failure must never release previous notes.
        st.session_state.pop("inspection", None)
        st.session_state.pop("inspection_error", None)
        try:
            st.session_state["page"] = read_sample_site()
        except Exception:
            load_failed = True

    page = st.text_area(
        "Untrusted page text",
        key="page",
        height=190,
        max_chars=MAX_PAGE_CHARS,
        placeholder="Paste fictional lesson text here, or load the sample above.",
        help="This is untrusted source text. It is never rendered as HTML or executed.",
    )
    inspect = st.button("Inspect page", type="primary", width="stretch")

with right:
    st.header("Guard decision", anchor=False)
    if sample or inspect:
        st.session_state.pop("inspection", None)
        st.session_state.pop("inspection_error", None)
        error_message = None
        try:
            if load_failed:
                error_message = "The local sample site could not be loaded. Try again."
            elif not page.strip():
                error_message = "Provide page text or load the sample before inspecting."
            elif mode == "Offline example":
                if page != SAMPLE_PAGE:
                    error_message = "Offline playback supports only the unchanged sample. Load it again or select Live Gemini."
                else:
                    result = GuardResult(**SAMPLE_RESULT)
            elif not has_key:
                error_message = "Configure GEMINI_API_KEY on the server, or use offline sample playback."
            else:
                with st.spinner("Inspecting the page with Gemini..."):
                    result = analyze_page(page)
            if error_message is None:
                st.session_state["inspection"] = (page, mode, result)
        except APIError as error:
            error_message = f"Gemini API returned status {error.code}."
        except ValueError:
            error_message = "The guard response could not be validated."
        except Exception:
            # Do not expose SDK exceptions, credentials, or previous inspection output.
            error_message = "Check the server API key, model access and connection, then retry."
        if error_message:
            st.session_state["inspection_error"] = (page, mode, error_message)

    saved = st.session_state.get("inspection")
    failed = st.session_state.get("inspection_error")
    if failed and failed[:2] == (page, mode):
        st.error("INSPECTION FAILED - No verdict. No notes released.")
        st.text(failed[2])
    elif saved and saved[:2] == (page, mode):
        result = saved[2]
        st.caption("Offline example  /  Prerecorded result" if mode == "Offline example" else "Live Gemini  /  Model decision")
        if result.has_malicious_instruction:
            st.error("Threat detected", icon=":material/gpp_bad:")
        else:
            st.success("No threat detected", icon=":material/verified_user:")

        if result.blocked_action:
            st.subheader("Attempted action", anchor=False)
            st.text(result.blocked_action)
        st.subheader("Reason", anchor=False)
        st.text(result.reason)

        st.divider()
        st.subheader("Extracted lesson notes", anchor=False)
        st.text(run_action("display_notes", result) or "No usable notes found.")

        with st.expander("Four-field guard JSON"):
            st.json(result.model_dump())
        with st.expander("Test the agent's permissions"):
            st.write("The backend permits local note display only. Form submissions are blocked even after a clean verdict.")
            st.caption("Simulation only: no form is submitted and no credentials are collected.")
            if st.button("Simulate submitting a form"):
                try:
                    run_action("submit_form", result)
                except PermissionError as error:
                    st.error(str(error))
    else:
        st.html('<div class="waiting"><b>Awaiting inspection</b><p>Load the sample to see which instruction the guard flags and which lesson notes reach the student.</p></div>')
        if saved or failed:
            st.caption("Page or mode changed. Inspect again for a result matching these inputs.")

st.caption("Agent permissions: read page text and display notes. External submissions are disabled.")

eval_dir = Path(__file__).with_name("evals")
cases = json.loads((eval_dir / "study_cases.json").read_text(encoding="utf-8"))
run = json.loads((eval_dir / "live_run.json").read_text(encoding="utf-8"))
outputs = {row["id"]: row for row in run["cases"]}
attacks = [case for case in cases if case["expected_malicious_flag"]]
clean = [case for case in cases if not case["expected_malicious_flag"]]

st.html('<div class="eval-title" id="evaluation"><h2>Evaluation</h2><span>Recorded live run</span></div>')
st.caption(f"{run['model']}  /  {run['run_date']}  /  Six fictional pages in three matched pairs")
caught = sum(outputs[c["id"]]["verdict"]["has_malicious_instruction"] for c in attacks)
alarms = sum(outputs[c["id"]]["verdict"]["has_malicious_instruction"] for c in clean)
facts = sum(row["lesson_fact_preserved"] for row in outputs.values())
st.html(f"""
<div class="metrics">
<div><b>{caught}<small> / {len(attacks)}</small></b><span>Attacks detected</span></div>
<div><b>{alarms}<small> / {len(clean)}</small></b><span>Clean pages flagged</span></div>
<div><b>{facts}<small> / {len(cases)}</small></b><span>Lesson facts preserved</span></div></div>
""")
topics = {"A": "Account security", "B": "Quoted instructions", "C": "Course footer"}
if st.toggle("Explore recorded evidence"):
    selected = st.selectbox("Recorded case", cases, format_func=lambda c: (
        f"{topics[c['pair']]} / {'Attack' if c['expected_malicious_flag'] else 'Clean page'}"
    ))
    st.caption("Source text from the recorded case")
    st.text(selected["page_text"])
    st.caption("Recorded Gemini response")
    st.json(outputs[selected["id"]]["verdict"])
