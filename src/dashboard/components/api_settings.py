import streamlit as st
import os

def render_api_settings():
    """Render API settings section in sidebar"""
    with st.sidebar.expander("API Settings", expanded=False, icon=":material/vpn_key:"):
        st.write("Configure your API keys for enhanced functionality")

        # OpenAI API Key
        openai_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.get('OPENAI_API_KEY', ''),
            type="password",
            help="Get your key from https://platform.openai.com/"
        )
        if openai_key:
            st.session_state['OPENAI_API_KEY'] = openai_key
            os.environ['OPENAI_API_KEY'] = openai_key

        # Financial Datasets API Key
        financial_key = st.text_input(
            "Financial Datasets API Key",
            value=st.session_state.get('FINANCIAL_DATASETS_API_KEY', ''),
            type="password",
            help="Get your key from https://financialdatasets.ai/"
        )
        if financial_key:
            st.session_state['FINANCIAL_DATASETS_API_KEY'] = financial_key
            os.environ['FINANCIAL_DATASETS_API_KEY'] = financial_key

        # Show status indicators
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.get('OPENAI_API_KEY'):
                st.success("OpenAI: Connected")
            else:
                st.warning("OpenAI: Not Set")

        with col2:
            if st.session_state.get('FINANCIAL_DATASETS_API_KEY'):
                st.success("Financial Data: Connected")
            else:
                st.warning("Financial Data: Not Set")
