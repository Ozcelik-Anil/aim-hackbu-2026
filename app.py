import os

import streamlit as st

from guard import GuardResult, MAX_PAGE_CHARS, analyze_page, run_action
from study_site import SAMPLE_PAGE, SAMPLE_RESULT, read_sample_site

st.set_page_config(page_title="AIM | Study Guard", layout="wide")
st.title("AIM · Study Guard")
st.write("Student task: collect lesson notes from a third-party study page.")

left, right = st.columns([1, 1])
with left:
    st.subheader("Study site")
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    mode = st.radio("Guard mode", ["Live Gemini", "Offline example"], index=0 if has_key else 1)
    sample = st.button("Load Sample Study Site with Trap")
    if sample:
        try:
            st.session_state["page"] = read_sample_site()
        except OSError:
            st.error("The local study site could not be reached.")
            st.stop()
    page = st.text_area("Untrusted page text", key="page", height=230, max_chars=MAX_PAGE_CHARS)
    inspect = st.button("Inspect page", type="primary")
    if mode == "Live Gemini":
        st.caption("Page text is sent to Gemini. Use fictional data.")

with right:
    st.subheader("Guard decision")
    if sample or inspect:
        st.session_state.pop("inspection", None)
        try:
            if mode == "Offline example":
                if page != SAMPLE_PAGE:
                    st.warning("Load the sample for offline playback, or select Live Gemini for custom text.")
                    st.stop()
                result = GuardResult(**SAMPLE_RESULT)
            else:
                if not has_key or not page.strip():
                    st.warning("Set GEMINI_API_KEY on the server and provide page text.")
                    st.stop()
                with st.spinner("Inspecting the page…"):
                    result = analyze_page(page)
            st.session_state["inspection"] = (page, mode, result)
        except Exception:
            st.error("Inspection failed. No notes were released. Check the API key, model access and connection.")
            st.stop()

    saved = st.session_state.get("inspection")
    if saved and saved[:2] == (page, mode):
        result = saved[2]
        st.caption("Offline fixture · no API call" if mode == "Offline example" else "Live Gemini verdict")
        if result.has_malicious_instruction:
            st.error("Malicious instruction detected")
            st.text(result.blocked_action)
        else:
            st.success("No malicious instruction detected")
        st.text(result.reason)
        st.subheader("Extracted study notes")
        st.text(run_action("display_notes", result) or "No usable notes found.")
        with st.expander("Guard JSON"):
            st.json(result.model_dump())
        with st.expander("Test the agent's permissions"):
            if st.button("Simulate submitting a form"):
                try:
                    run_action("submit_form", result)
                except PermissionError as error:
                    st.error(str(error))
    else:
        st.info("Load the sample or inspect the current page.")
