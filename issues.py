import json
import os
import requests
from datetime import datetime

def create_github_issue():
    with open("papers_latest.json") as f:
        data = json.load(f)

    papers = data["papers"][:15]
    date = data["date"]

    # Separar por tipo
    tier1 = [p for p in papers if p["source_tier"] == 3]
    resto = [p for p in papers if p["source_tier"] < 3]
    nonweird = [p for p in papers if any(k in ["sesgo","gender bias","latin america","non-weird","intersectional","spanish","decolonial"] for k in p.get("keywords_matched", []))]

    body = f"## 📚 Papers de la semana — {date}\n\n"
    body += f"**{data['total_found']} papers encontrados** · {len(papers)} en este digest\n\n"

    if nonweird:
        body += "### 🌍 No-WEIRD / Sesgo / Género\n\n"
        for p in nonweird[:5]:
            resumen = p.get("resumen_es", "")
            body += f"**[{p['title']}]({p['url']})**\n"
            body += f"*Fuente: {p['source']} · Score: {p['score']}*\n\n"
            if resumen:
                body += f"> {resumen}\n\n"
            else:
                body += f"{p['abstract'][:200]}...\n\n"
            body += f"`{'` `'.join(p['keywords_matched'][:4])}`\n\n---\n\n"

    if tier1:
        body += "### ⭐ Fuentes tier 1 (Anthropic, OpenAI, Alignment Forum...)\n\n"
        for p in tier1[:5]:
            resumen = p.get("resumen_es", "")
            body += f"**[{p['title']}]({p['url']})**\n"
            body += f"*Fuente: {p['source']}*\n\n"
            if resumen:
                body += f"> {resumen}\n\n"
            else:
                body += f"{p['abstract'][:200]}...\n\n"
            body += f"`{'` `'.join(p['keywords_matched'][:4])}`\n\n---\n\n"

    body += "### 📋 Resto de papers relevantes\n\n"
    for p in resto[:8]:
        body += f"- **[{p['title']}]({p['url']})** · `{p['source']}` · score {p['score']}\n"
        if p.get("keywords_matched"):
            body += f"  `{'` `'.join(p['keywords_matched'][:3])}`\n"

    body += f"\n\n---\n*Generado automáticamente por el scraper · [Ver JSON completo](papers_latest.json)*\n"
    body += "\n**👇 Elige 3-5 papers y escribe aquí tu resumen editorial para la semana**"

    # Labels automáticos
    labels = ["digest"]
    if nonweird:
        labels.append("no-WEIRD")
    if tier1:
        labels.append("tier-1")

    resp = requests.post(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues",
        headers={
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github+json",
        },
        json={
            "title": f"📚 Papers semana {date}",
            "body": body,
            "labels": labels,
        },
    )

    if resp.status_code == 201:
        print(f"✅ Issue creado: {resp.json()['html_url']}")
    else:
        print(f"⚠️  Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    create_github_issue()
