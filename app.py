import streamlit as st
from src.pipelines.pipeline import run_research_pipeline

# Run on cuda 
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

print(device)

# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide",
)


# ==========================================
# Custom CSS
# ==========================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 30px;
    }

    .step-box {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #ddd;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# Header
# ==========================================

st.markdown(
    '<div class="main-title">🔎 AI Research Agent</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Multi-agent research system powered by LangChain and Groq'
    '</div>',
    unsafe_allow_html=True,
)


# ==========================================
# Sidebar
# ==========================================

with st.sidebar:

    st.header("⚙️ Research Settings")

    st.write(
        """
        This application uses multiple AI components:

        **1. Search Agent**
        - Searches the web
        - Finds recent information

        **2. Reader Agent**
        - Selects relevant URLs
        - Scrapes detailed content

        **3. Writer**
        - Combines research
        - Generates a structured report

        **4. Critic**
        - Reviews the report
        - Provides a score and feedback
        """
    )

    st.divider()

    st.info(
        "💡 Enter a research topic and let the agents "
        "research, write and critique the result."
    )


# ==========================================
# Topic Input
# ==========================================

st.subheader("📝 Research Topic")

topic = st.text_input(
    "What would you like to research?",
    placeholder="e.g. Impact of Artificial Intelligence on healthcare",
)


# ==========================================
# Run Research
# ==========================================

if st.button("🚀 Start Research", type="primary", use_container_width=True):

    if not topic.strip():

        st.warning("Please enter a research topic.")

    else:

        # Progress indicator
        progress = st.progress(0)

        # Status message
        status = st.empty()

        try:

            # ==================================
            # Step 1
            # ==================================

            status.info("🔎 Step 1/4 — Search Agent is searching the web...")
            progress.progress(10)

            state = run_research_pipeline(topic)

            progress.progress(100)

            status.success("✅ Research completed!")

            # ==================================
            # Results
            # ==================================

            st.divider()

            st.header("📊 Research Results")

            # ==================================
            # Search Results
            # ==================================

            with st.expander(
                "🔎 Step 1 — Web Search Results",
                expanded=False,
            ):

                st.markdown(
                    state.get(
                        "search_results",
                        "No search results available.",
                    )
                )

            # ==================================
            # Scraped Content
            # ==================================

            with st.expander(
                "📖 Step 2 — Scraped Content",
                expanded=False,
            ):

                st.markdown(
                    state.get(
                        "scraped_content",
                        "No scraped content available.",
                    )
                )

            # ==================================
            # Final Report
            # ==================================

            st.subheader("📄 Final Research Report")

            report = state.get(
                "report",
                "No report generated.",
            )

            st.markdown(report)

            # Download report
            st.download_button(
                label="⬇️ Download Report",
                data=report,
                file_name="research_report.txt",
                mime="text/plain",
            )

            # ==================================
            # Critic
            # ==================================

            st.divider()

            st.subheader("🧐 Critic Review")

            feedback = state.get(
                "feedback",
                "No critic feedback available.",
            )

            st.markdown(feedback)

        except Exception as e:

            progress.empty()

            status.error("❌ An error occurred.")

            st.exception(e)


# ==========================================
# Footer
# ==========================================

st.divider()

st.caption(
    "AI Research Agent • LangChain + Groq + Tavily"
)

