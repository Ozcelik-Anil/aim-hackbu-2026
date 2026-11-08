"""Named entry points for research and the security demonstration."""
import streamlit as st

st.set_page_config(page_title="AgentGuard | Research", layout="wide")
page = st.navigation([
    st.Page("research_ui.py", title="Research", default=True),
    st.Page("pages/1_Source_Inspector.py", title="Security demo", url_path="Source_Inspector"),
])
page.run()