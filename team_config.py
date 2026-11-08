"""Resolve credentials from the team server, never from visitor input."""
import os

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


def team_key(name):
    if value := os.getenv(name):
        return value.strip()
    try:
        return st.secrets.get(name, "").strip()
    except StreamlitSecretNotFoundError:
        return ""
