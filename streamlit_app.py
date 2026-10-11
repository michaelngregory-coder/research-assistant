import streamlit as st
import requests

# App Configuration
st.set_page_config(page_title="Academic & Gov Research Aggregator", layout="wide")

st.title("📚 Research Assistant")
st.markdown("Search academic databases and access key government archives.")

# --- API FUNCTIONS ---
def search_semantic_scholar(query):
    # Your existing Semantic Scholar API logic here
    # Example: response = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}")
    return "Semantic Scholar results for: " + query

def search_openalex(query):
    # Your existing OpenAlex API logic here
    return "OpenAlex results for: " + query

def search_pubmed(query):
    # Your existing PubMed logic
    return "PubMed results for: " + query

def search_arxiv(query):
    # Your existing ArXiv logic
    return "ArXiv results for: " + query

def search_core(query):
    # Your existing CORE logic
    return "CORE results for: " + query

# --- SIDEBAR: DATABASE SELECTION & RESOURCES ---
with st.sidebar:
    st.header("Search Settings")
    
    st.subheader("Active Databases")
    search_semantic = st.checkbox("Semantic Scholar", value=True)
    search_openalex = st.checkbox("OpenAlex", value=True)
    search_pubmed = st.checkbox("PubMed/PMC", value=True)
    search_arxiv = st.checkbox("ArXiv", value=True)
    search_core = st.checkbox("CORE", value=True)
    
    st.divider()
    
    with st.expander("🔗 Quick Access Resources"):
        st.markdown("[U.S. Supreme Court](https://www.supremecourt.gov/opinions/slipopinion/26)")
        st.markdown("[SCOTUS Blog](https://www.scotusblog.com/)")
        st.markdown("[U.S. Congress](https://www.congress.gov/)")
        st.markdown("[GovTrack](https://www.govtrack.us/)")
        st.markdown("[Library of Congress](https://www.loc.gov/)")
        st.markdown("[Office of the Historian](https://www.state.gov/bureaus-offices/under-secretary-for-management/foreign-service-institute/office-of-the-historian/)")
        st.markdown("[History.com](https://www.history.com/)")
        st.markdown("[CIA Factbook Archive](https://www.cia.gov/the-world-factbook/about/archives/)")

# --- MAIN DASHBOARD ---
query = st.text_input("Enter your research topic:", "")

if st.button("Search"):
    if not query:
        st.warning("Please enter a search query.")
    else:
        active_dbs = []
        if search_semantic: active_dbs.append("Semantic Scholar")
        if search_openalex: active_dbs.append("OpenAlex")
        if search_pubmed: active_dbs.append("PubMed/PMC")
        if search_arxiv: active_dbs.append("ArXiv")
        if search_core: active_dbs.append("CORE")
        
        st.success(f"Searching: {', '.join(active_dbs)}")
        
        if search_semantic:
            with st.expander("Semantic Scholar Results"):
                st.write(search_semantic_scholar(query))
        if search_openalex:
            with st.expander("OpenAlex Results"):
                st.write(search_openalex(query))
        if search_pubmed:
            with st.expander("PubMed/PMC Results"):
                st.write(search_pubmed(query))
        if search_arxiv:
            with st.expander("ArXiv Results"):
                st.write(search_arxiv(query))
        if search_core:
            with st.expander("CORE Results"):
                st.write(search_core(query))

# Manual Lookup
st.divider()
st.markdown(f"**Quick Manual Search:** [Google Scholar](https://scholar.google.com/scholar?q={query})")

