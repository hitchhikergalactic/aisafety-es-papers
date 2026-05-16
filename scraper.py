import feedparser
import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

ARXIV_FEEDS = [
    "https://rss.arxiv.org/rss/cs.AI",
    "https://rss.arxiv.org/rss/cs.LG",
    "https://rss.arxiv.org/rss/cs.CY",
    "https://rss.arxiv.org/rss/cs.CL",
]

RSS_FEEDS = [
    ("https://www.alignmentforum.org/feed.xml", "alignment_forum", 3),
    ("https://www.lesswrong.com/feed.xml?view=top-questions", "lesswrong", 2),
    ("https://www.anthropic.com/rss.xml", "anthropic", 3),
    ("https://openai.com/blog/rss.xml", "openai", 3),
    ("https://deepmind.google/blog/rss/feed/", "deepmind", 3),
    ("https://www.safe.ai/blog/rss", "cais", 2),
]

GITHUB_REPOS = [
    ("anthropics", "evals", 3),
    ("openai", "evals", 3),
    ("METR", "task-standard", 3),
    ("google-deepmind", "safety-research", 2),
    ("EleutherAI", "lm-evaluation-harness", 2),
    ("deepseek-ai", "DeepSeek-R1", 2),
    ("alignmentresearch", "alignment-research-dataset", 2),
]

WATCH_PAGES = [
    ("https://metr.org/research", "metr", 3),
    ("https://apolloresearch.ai/research", "apollo_research", 3),
    ("https://www.gov.uk/search/research-and-statistics?keywords=AI+safety", "uk_dsit", 3),
    ("https://incidentdatabase.ai/blog/", "ai_incident_db", 2),
]

KEYWORDS_SAFETY = [
    "alignment", "ai safety", "interpretability", "mechanistic",
    "scalable oversight", "rlhf", "rlaif", "reward hacking",
    "corrigibility", "deceptive alignment", "mesa-optimization",
    "goal misgeneralization", "emergent capabilities", "ai governance",
    "existential risk", "jailbreak", "red teaming", "robustness",
    "superalignment", "constitutional ai", "corrigible",
    "capability evaluation", "dangerous capabilities", "evals",
    "frontier model", "agentic", "multi-agent safety", "autonomous",
]

KEYWORDS_NONWEIRD = [
    "non-weird", "global south", "latin america", "spanish language",
    "multilingual bias", "cultural bias", "indigenous", "decolonial",
    "feminist ai", "gender bias", "intersectional", "colonial bias",
    "low-resource language", "spanish evaluation", "sesgo",
    "habla hispana", "castellano", "língua portuguesa",
    "racismo", "discriminación", "equidad", "inclusión",
]

KEYWORDS_ALL = KEYWORDS_SAFETY + KEYWORDS_NONWEIRD


def score_paper(title, abstract):
    text = (title + " " + abstract).lower()
    hits = [kw for kw in KEYWORDS_ALL if kw in text]
    return len(hits), hits


def fetch_arxiv():
    papers = []
    seen = set()
    for feed_url in ARXIV_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                arxiv_id = entry.get("id", "")
                if arxiv_id in seen:
                    continue
                seen.add(arxiv_id)
                title = entry.get("title", "").replace("\n", " ")
                abstract = entry.get("summary", "").replace("\n", " ")
                score, matched = score_paper(title, abstract)
                if score > 0:
                    papers.append({
                        "title": title,
                        "abstract": abstract[:500],
                        "url": arxiv_id,
                        "source": "arxiv",
                        "source_tier": 2,
                        "score": score,
                        "keywords_matched": matched,
                    })
        except Exception as e:
            print(f"  ⚠️  arXiv error {feed_url}: {e}")
    return papers


def fetch_rss_feeds():
    papers = []
    for url, source_name, tier in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:
                title = entry.get("title", "").replace("\n", " ")
                abstract = entry.get("summary", "").replace("\n", " ")
                score, matched = score_paper(title, abstract)
                if score > 0 or tier == 3:
                    papers.append({
                        "title": title,
                        "abstract": abstract[:500],
                        "url": entry.get("link", ""),
                        "source": source_name,
                        "source_tier": tier,
                        "score": score + tier,
                        "keywords_matched": matched,
                    })
        except Exception as e:
            print(f"  ⚠️  RSS error {source_name}: {e}")
    return papers


def fetch_github():
    papers = []
    for owner, repo, tier in GITHUB_REPOS:
        for feed_type in ["releases", "tags"]:
            url = f"https://github.com/{owner}/{repo}/{feed_type}.atom"
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:
                    title = f"[{owner}/{repo}] {entry.get('title', f'New {feed_type[:-1]}')}"
                    abstract = entry.get("summary", "")
                    score, matched = score_paper(title, abstract)
                    papers.append({
                        "title": title,
                        "abstract": abstract[:300],
                        "url": entry.get("link", f"https://github.com/{owner}/{repo}"),
                        "source": f"github_{owner}",
                        "source_tier": tier,
                        "score": score + tier,
                        "keywords_matched": matched,
                        "type": f"github_{feed_type[:-1]}",
                    })
            except Exception as e:
                print(f"  ⚠️  GitHub {feed_type} error {owner}/{repo}: {e}")
    return papers


def fetch_watch_pages():
    papers = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; aisafety-bot/1.0)"}
    for url, source_name, tier in WATCH_PAGES:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup.find_all(["h2", "h3", "h4", "a"])[:30]:
                text = tag.get_text(strip=True)
                href = tag.get("href", "")
                if len(text) < 20:
                    continue
                score, matched = score_paper(text, "")
                if score > 0 or tier == 3:
                    full_url = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
                    papers.append({
                        "title": text,
                        "abstract": "",
                        "url": full_url,
                        "source": source_name,
                        "source_tier": tier,
                        "score": score + tier,
                        "keywords_matched": matched,
                        "type": "web_page",
                    })
        except Exception as e:
            print(f"  ⚠️  Watch page error {source_name}: {e}")
    return papers


def fetch_semantic_scholar():
    papers = []
    queries = [
        "AI safety alignment 2025",
        "LLM bias spanish non-WEIRD 2025",
        "interpretability mechanistic 2025",
        "AI governance global south 2025",
    ]
    for query in queries:
        try:
            r = requests.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params={
                    "query": query,
                    "limit": 10,
                    "fields": "title,abstract,authors,year,url,externalIds",
                    "publicationDateOrYear": "2025",
                },
                timeout=10,
            )
            for p in r.json().get("data", []):
                abstract = p.get("abstract") or ""
                score, matched = score_paper(p.get("title", ""), abstract)
                if score > 0:
                    papers.append({
                        "title": p.get("title", ""),
                        "abstract": abstract[:500],
                        "url": p.get("url", ""),
                        "source": "semantic_scholar",
                        "source_tier": 2,
                        "score": score,
                        "keywords_matched": matched,
                    })
        except Exception as e:
            print(f"  ⚠️  Semantic Scholar error: {e}")
    return papers


def fetch_acl_anthology():
    papers = []
    queries = ["bias spanish", "multilingual safety", "gender bias LLM", "latin america NLP"]
    for q in queries:
        try:
            r = requests.get("https://aclanthology.org/search/", params={"q": q}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for item in soup.select(".list-pl-responsive")[:5]:
                title_el = item.select_one("strong a")
                if not title_el:
                    continue
                title = title_el.text.strip()
                href = "https://aclanthology.org" + title_el["href"]
                score, matched = score_paper(title, "")
                papers.append({
                    "title": title,
                    "abstract": "",
                    "url": href,
                    "source": "acl_anthology",
                    "source_tier": 2,
                    "score": max(score, 1),
                    "keywords_matched": matched,
                })
        except Exception as e:
            print(f"  ⚠️  ACL Anthology error: {e}")
    return papers


def generate_summary_es(paper, api_key):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    "Eres editor de aisafety.es. En 3 líneas en castellano explica por qué "
                    "este paper importa para una audiencia hispanohablante interesada en seguridad "
                    "de IA. Sé concreto y directo, nada de frases genéricas.\n\n"
                    f"Título: {paper['title']}\n"
                    f"Abstract: {paper['abstract']}"
                ),
            }],
        )
        return msg.content[0].text
    except Exception as e:
        print(f"  ⚠️  Resumen error '{paper['title'][:50]}': {e}")
        return ""


def main():
    all_papers = []

    print("📡 arXiv...")
    r = fetch_arxiv()
    print(f"   {len(r)} papers")
    all_papers += r

    print("📡 RSS (Alignment Forum, Anthropic, OpenAI, DeepMind...)")
    r = fetch_rss_feeds()
    print(f"   {len(r)} items")
    all_papers += r

    print("📡 GitHub releases + tags...")
    r = fetch_github()
    print(f"   {len(r)} items")
    all_papers += r

    print("📡 Apollo, METR, DSIT...")
    r = fetch_watch_pages()
    print(f"   {len(r)} items")
    all_papers += r

    print("📡 Semantic Scholar...")
    r = fetch_semantic_scholar()
    print(f"   {len(r)} papers")
    all_papers += r

    print("📡 ACL Anthology...")
    r = fetch_acl_anthology()
    print(f"   {len(r)} papers")
    all_papers += r

    # Dedup por URL
    seen_urls = set()
    unique = []
    for p in all_papers:
        if p["url"] and p["url"] not in seen_urls:
            seen_urls.add(p["url"])
            unique.append(p)

    unique.sort(key=lambda x: (x["source_tier"], x["score"]), reverse=True)

    # Resúmenes en castellano si hay API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        print("🤖 Generando resúmenes en castellano (top 20)...")
        for p in unique[:20]:
            if p.get("abstract"):
                p["resumen_es"] = generate_summary_es(p, api_key)
                print(f"   ✓ {p['title'][:60]}")
    else:
        print("ℹ️  Sin ANTHROPIC_API_KEY — saltando resúmenes")

    output = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "total_found": len(unique),
        "by_source": {
            src: len([p for p in unique if p["source"] == src])
            for src in sorted(set(p["source"] for p in unique))
        },
        "papers": unique[:50],
    }

    with open("papers_latest.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(unique)} items únicos. Top 50 en papers_latest.json")
    print(f"   Por fuente: {json.dumps(output['by_source'], indent=2)}")


if __name__ == "__main__":
    main()
