"""Study Guard UI. Untrusted content is displayed as plain text only."""

import os

import streamlit as st
from google.genai.errors import APIError

from guard import GuardResult, MAX_PAGE_CHARS, analyze_page, run_action
from study_site import SAMPLE_PAGE, SAMPLE_RESULT, read_sample_site

STUDENT_TASK = "Collect lesson notes about binary search from a third-party study page."

st.set_page_config(page_title="AIM | AgentGuard", page_icon="🛡️", layout="wide")
st.markdown("### TEAM AIM / HACKBU 2026")
st.title("AgentGuard")
st.write("Keep the lesson. Block the trap.")
st.caption("A read-only student assistant inspecting untrusted third-party content.")

left, right = st.columns([1, 1.2], gap="large")
with left:
    st.subheader("1. Student request")
    st.text(STUDENT_TASK)
    st.caption("Authorized: read lesson text and display notes. No credentials or form submissions.")

    st.subheader("2. Third-party study page")
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    mode = st.radio("Guard mode", ["Live Gemini", "Offline example"], index=0 if has_key else 1)
    if mode == "Offline example":
        st.info("OFFLINE PLAYBACK - prerecorded sample verdict. No model or API call.")
        st.caption("Custom pages require Live Gemini. Playback does not perform detection.")
    else:
        st.info("LIVE GEMINI - inspect the page with the model.")
        st.caption("Page text is sent to Gemini only when you click an inspection button. Use fictional data.")
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
        height=280,
        max_chars=MAX_PAGE_CHARS,
        placeholder="Paste fictional lesson text here, or load the sample above.",
        help="This is untrusted source text. It is never rendered as HTML or executed.",
    )
    inspect = st.button("Inspect page", type="primary", width="stretch")
    st.caption("Sample: a fictional binary-search lesson containing a student-password trap.")

with right:
    st.subheader("3. Guard decision")
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
        st.caption("A failed inspection is not a clean verdict. External actions remain unavailable.")
    elif saved and saved[:2] == (page, mode):
        result = saved[2]
        st.caption("OFFLINE PLAYBACK / prerecorded fixture / no API call" if mode == "Offline example" else "LIVE GEMINI / model-generated verdict")
        if result.has_malicious_instruction:
            st.error("THREAT DETECTED - Malicious instruction identified.")
        else:
            st.success("CLEAN VERDICT - No malicious instruction detected.")
            st.caption("This is a model verdict, not a guarantee that the page is safe.")

        st.markdown("**What the site tried to do**")
        st.text(result.blocked_action or "No malicious action identified.")
        st.markdown("**Why this decision was made**")
        st.text(result.reason)

        st.subheader("Lesson notes the student received")
        st.caption("Extracted content / plain text / never executed")
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
        st.info("READY - Load the sample to inspect it in one click, or inspect your own page.")
        st.write("You will see the attempted action, the guard's reason and the lesson notes that remain.")
        if saved or failed:
            st.caption("Page or mode changed. Inspect again for a result matching these inputs.")

st.divider()
st.caption("Demo boundary: model-based content inspection + code-enforced read-only permissions. Not a general security guarantee.")
