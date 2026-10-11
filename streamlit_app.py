import streamlit as st
import requests
import urllib.parse
from typing import List, Dict

st.set_page_config(page_title="Academic Research Assistant", page_icon="🔬", layout="wide")

st.title("🔬 Academic Research Assistant")
st.markdown("Search across multiple open academic databases")

# Search query input
query = st.text_input("Enter your research query:", placeholder="e.g., machine learning healthcare")
max_results = st.slider("Results per database:", min_value=5, max_value=20, value=10)

def search_semantic_scholar(query: str, limit: int = 10) -> List[Dict]:
    """Search Semantic Scholar API"""
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {"query": query, "limit": limit, "fields": "title,authors,year,abstract,openAccessPdf,externalIds"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        st.error(f"Semantic Scholar error: {e}")
        return []

def search_openalex(query: str, limit: int = 10) -> List[Dict]:
    """Search OpenAlex API"""
    try:
        url = "https://api.openalex.org/works"
        params = {"filter": f"display_name.search:{query}", "per-page": limit}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        st.error(f"OpenAlex error: {e}")
        return []

def search_pubmed(query: str, limit: int = 10) -> List[Dict]:
    """Search PubMed via NCBI E-utilities"""
    try:
        # Step 1: Search for PMIDs
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": limit,
            "retmode": "json"
        }
        search_response = requests.get(search_url, params=search_params, timeout=10)
        search_response.raise_for_status()
        pmids = search_response.json().get("esearchresult", {}).get("idlist", [])
        
        if not pmids:
            return []
        
        # Step 2: Fetch summaries for PMIDs
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json"
        }
        summary_response = requests.get(summary_url, params=summary_params, timeout=10)
        summary_response.raise_for_status()
        results = summary_response.json().get("result", {})
        
        papers = []
        for pmid in pmids:
            if pmid in results:
                paper = results[pmid]
                papers.append({
                    "pmid": pmid,
                    "title": paper.get("title", ""),
                    "authors": [author.get("name", "") for author in paper.get("authors", [])],
                    "pubdate": paper.get("pubdate", ""),
                    "source": paper.get("source", ""),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
        return papers
    except Exception as e:
        st.error(f"PubMed error: {e}")
        return []

def search_arxiv(query: str, limit: int = 10) -> List[Dict]:
    """Search ArXiv API"""
    try:
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse XML response (simple approach)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        
        papers = []
        for entry in root.findall("atom:entry", namespace):
            title = entry.find("atom:title", namespace)
            summary = entry.find("atom:summary", namespace)
            published = entry.find("atom:published", namespace)
            link = entry.find("atom:id", namespace)
            authors = entry.findall("atom:author/atom:name", namespace)
            
            papers.append({
                "title": title.text.strip() if title is not None else "",
                "authors": [author.text for author in authors],
                "published": published.text[:10] if published is not None else "",
                "abstract": summary.text.strip() if summary is not None else "",
                "url": link.text if link is not None else ""
            })
        return papers
    except Exception as e:
        st.error(f"ArXiv error: {e}")
        return []

def search_core(query: str, limit: int = 10) -> List[Dict]:
    """Search CORE API (without API key - limited results)"""
    try:
        url = "https://core.ac.uk:443/api-v2/search/" + urllib.parse.quote(query)
        params = {"page": 1, "pageSize": limit}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        st.warning(f"CORE error (may need API key for full access): {e}")
        return []

# Search button
if st.button("🔍 Search All Databases", type="primary"):
    if not query:
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Searching databases..."):
            # Semantic Scholar
            st.subheader("📚 Semantic Scholar")
            ss_results = search_semantic_scholar(query, max_results)
            if ss_results:
                for paper in ss_results:
                    with st.expander(f"**{paper.get('title', 'No title')}**"):
                        authors = ", ".join([a.get("name", "") for a in paper.get("authors", [])])
                        st.write(f"**Authors:** {authors}")
                        st.write(f"**Year:** {paper.get('year', 'N/A')}")
                        if paper.get("abstract"):
                            st.write(f"**Abstract:** {paper['abstract'][:300]}...")
                        pdf = paper.get("openAccessPdf")
                        if pdf and pdf.get("url"):
                            st.markdown(f"[📄 Open Access PDF]({pdf['url']})")
            else:
                st.info("No results from Semantic Scholar.")
            
            st.divider()
            
            # OpenAlex
            st.subheader("🌐 OpenAlex")
            oa_results = search_openalex(query, max_results)
            if oa_results:
                for work in oa_results:
                    with st.expander(f"**{work.get('display_name', 'No title')}**"):
                        st.write(f"**Year:** {work.get('publication_year', 'N/A')}")
                        st.write(f"**Cited by:** {work.get('cited_by_count', 0)}")
                        if work.get("doi"):
                            st.markdown(f"[🔗 DOI Link](https://doi.org/{work['doi']})")
            else:
                st.info("No results from OpenAlex.")
            
            st.divider()
            
            # PubMed
            st.subheader("🧬 PubMed")
            pm_results = search_pubmed(query, max_results)
            if pm_results:
                for paper in pm_results:
                    with st.expander(f"**{paper['title']}**"):
                        st.write(f"**Authors:** {', '.join(paper['authors'][:5])}")
                        st.write(f"**Published:** {paper['pubdate']}")
                        st.write(f"**Source:** {paper['source']}")
                        st.markdown(f"[🔗 PubMed Link]({paper['url']})")
            else:
                st.info("No results from PubMed.")
            
            st.divider()
            
            # ArXiv
            st.subheader("📑 ArXiv")
            arxiv_results = search_arxiv(query, max_results)
            if arxiv_results:
                for paper in arxiv_results:
                    with st.expander(f"**{paper['title']}**"):
                        st.write(f"**Authors:** {', '.join(paper['authors'][:5])}")
                        st.write(f"**Published:** {paper['published']}")
                        if paper.get("abstract"):
                            st.write(f"**Abstract:** {paper['abstract'][:300]}...")
                        st.markdown(f"[🔗 ArXiv Link]({paper['url']})")
            else:
                st.info("No results from ArXiv.")
            
            st.divider()
            
            # CORE
            st.subheader("🔓 CORE")
            core_results = search_core(query, max_results)
            if core_results:
                for paper in core_results:
                    title = paper.get("title", "No title")
                    with st.expander(f"**{title}**"):
                        st.write(f"**Authors:** {', '.join(paper.get('authors', []))}")
                        st.write(f"**Year:** {paper.get('year', 'N/A')}")
                        if paper.get("downloadUrl"):
                            st.markdown(f"[📄 Download PDF]({paper['downloadUrl']})")
            else:
                st.info("No results from CORE (may require API key).")
            
            st.divider()
            
            # Google Scholar Manual Link
            st.subheader("🎓 Google Scholar")
            encoded_query = urllib.parse.quote(query)
            scholar_url = f"https://scholar.google.com/scholar?q={encoded_query}"
            st.markdown(f"[🔗 Search on Google Scholar]({scholar_url})")
            st.caption("Google Scholar does not provide a public API. Click above to search manually.")

st.divider()
st.caption("Built with Streamlit | Searches open academic databases")
