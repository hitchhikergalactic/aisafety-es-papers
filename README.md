# 📚 aisafety-es-papers

Scraper automático de papers sobre seguridad de IA para [aisafety.es](https://aisafety.es).

Cada semana seleccionamos 3-5 papers con criterio editorial y resumen en castellano 
sobre por qué importan para la re hispanohablante.

## Qué hace

- Rastrea arXiv (cs.AI, cs.LG, cs.CY, cs.CL), Alignment Forum, Anthropic, OpenAI, 
  DeepMind, METR, Apollo Research, ACL Anthology y Semantic Scholar
- Filtra por keywords de safety, alignment, interpretabilidad y sesgo/no-WEIRD
- Crea un issue semanal en GitHub con los papers organizados por categoría
- Guarda el resultado completo en `papers_latest.json`

## Cuándo corre

Automáticamente cada lunes y jueves a las 9:00 (Madrid) vía GitHub Actions.
También se puede lanzar manualmente desde la pestaña Actions.

## Estructura

```
├── scraper.py          # Fetching y scoring de papers
├── issues.py           # Creación del issue semanal en GitHub
├── requirements.txt    # Dependencias Python
├── papers_latest.json  # Último resultado del scraper
└── .github/workflows/
    └── scraper.yml     # Workflow de GitHub Actions
```

## Categorías

**⭐ Tier 1** — Fuentes primarias: Anthropic, OpenAI, DeepMind, Alignment Forum, METR, Apollo Research

**🌍 No-WEIRD** — Papers fuera del entorno Western/English-centric: América Latina, 
sesgo en español, perspectivas feministas, lenguas indígenas, Global South

**📋 Resto** — Papers relevantes de arXiv y otras fuentes académicas

## Flujo editorial

1. El scraper crea un issue cada lunes con ~15 papers relevantes
2. Se leen los candidatos y se eligen 3-5
3. Se escribe en castellano por qué importa cada uno
4. Se publica en aisafety.es

## Keywords monitorizadas

**Safety/Alignment:** alignment, interpretability, mechanistic, scalable oversight, 
RLHF, reward hacking, corrigibility, deceptive alignment, red teaming, evals...

**No-WEIRD:** latin america, global south, gender bias in ai, multilingual bias, 
decolonial, feminist ai, sesgo en ia, habla hispana...

## Contribuir

Si conoces fuentes relevantes que no estamos monitorizando, abre un issue.
Si quieres colaborar en la selección editorial, escríbenos a [hola@aisafety.es](mailto:hola@aisafety.es).

## Licencia

MIT
