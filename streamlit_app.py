import streamlit as st
import requests
from typing import List, Dict
import time

st.set_page_config(
    page_title="Academic Research Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Academic Research Assistant")
st.markdown("Search across multiple open-access academic databases")

# Configuration
SOURCES = {
    "Semantic Scholar": {
        "url": "https://api.semanticscholar.org/graph/v1/paper/search",
        "enabled": True
    },
    "OpenAlex": {
        "url": "https://api.openalex.org/works",
        "enabled": True
    }
}

def search_semantic_scholar(query: str, limit: int = 10) -> List[Dict]:
    """Search Semantic Scholar API"""
    try:
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,year,abstract,openAccessPdf,externalIds"
        }
        response = requests.get(SOURCES["Semantic Scholar"]["url"], params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = []
            for paper in data.get("data", []):
                results.append({
                    "title": paper.get("title", "No title"),
                    "authors": ", ".join([a.get("name", "") for a in paper.get("authors", [])[:3]]),
                    "year": paper.get("year", "N/A"),
                    "abstract": paper.get("abstract", "No abstract available")[:300] + "...",
                    "pdf_url": paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None,
                    "doi": paper.get("externalIds", {}).get("DOI"),
                    "source": "Semantic Scholar"
                })
            return results
    except Exception as e:
        st.warning(f"Semantic Scholar error: {str(e)}")
    return []

def search_openalex(query: str, limit: int = 10) -> List[Dict]:
    """Search OpenAlex API"""
    try:
        params = {
            "search": query,
            "per-page": limit,
            "mailto": "research-tool@example.com"  # Polite API usage
        }
        response = requests.get(SOURCES["OpenAlex"]["url"], params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = []
            for work in data.get("results", []):
                authors = work.get("authorships", [])
                author_names = ", ".join([a.get("author", {}).get("display_name", "") for a in authors[:3]])
                
                results.append({
                    "title": work.get("title", "No title"),
                    "authors": author_names if author_names else "Unknown",
                    "year": work.get("publication_year", "N/A"),
                    "abstract": (work.get("abstract_inverted_index", {}) and "Abstract available") or "No abstract",
                    "pdf_url": work.get("open_access", {}).get("oa_url"),
                    "doi": work.get("doi", "").replace("https://doi.org/", ""),
                    "source": "OpenAlex"
                })
            return results
    except Exception as e:
        st.warning(f"OpenAlex error: {str(e)}")
    return []

# Search interface
query = st.text_input("🔍 Enter your research topic:", placeholder="e.g., machine learning in healthcare")

col1, col2 = st.columns([1, 4])
with col1:
    max_results = st.selectbox("Results per source:", [5, 10, 15, 20], index=1)
with col2:
    search_button = st.button("Search", type="primary", use_container_width=True)

if search_button and query:
    with st.spinner("Searching academic databases..."):
        all_results = []
        
        if SOURCES["Semantic Scholar"]["enabled"]:
            all_results.extend(search_semantic_scholar(query, max_results))
            time.sleep(0.5)  # Rate limiting
        
        if SOURCES["OpenAlex"]["enabled"]:
            all_results.extend(search_openalex(query, max_results))
        
        # Display results
        if all_results:
            st.success(f"Found {len(all_results)} papers")
            
            for idx, paper in enumerate(all_results, 1):
                with st.expander(f"**{idx}. {paper['title']}**"):
                    st.markdown(f"**Authors:** {paper['authors']}")
                    st.markdown(f"**Year:** {paper['year']} | **Source:** {paper['source']}")
                    st.markdown(f"**Abstract:** {paper['abstract']}")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if paper['pdf_url']:
                            st.link_button("📄 Open Access PDF", paper['pdf_url'])
                    with col_b:
                        if paper['doi']:
                            st.link_button("🔗 DOI Link", f"https://doi.org/{paper['doi']}")
                    with col_c:
                        if paper['doi']:
                            st.link_button("🔓 Find Free PDF", f"https://unpaywall.org/{paper['doi']}")
        else:
            st.warning("No results found. Try different keywords.")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This tool searches:
    - **Semantic Scholar** (AI-powered)
    - **OpenAlex** (Open catalog)
    
    More sources coming soon.
    """)
    
    st.header("Tips")
    st.markdown("""
    - Use specific keywords
    - Try synonyms if no results
    - Check Unpaywall for PDFs
    """)

