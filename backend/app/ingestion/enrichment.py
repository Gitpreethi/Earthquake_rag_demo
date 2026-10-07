"""Lightweight metadata enrichment: location and topic tags.

Uses a generic gazetteer of Indian states/UTs (plus a few neighbouring
countries and well-known seismic districts) and keyword-based topic rules.
These are reference lists, not document content: tags are only attached
when the term actually occurs in the chunk text.
"""
from __future__ import annotations

import re
from collections import Counter

# canonical name -> aliases (lower case)
INDIA_REGIONS: dict[str, list[str]] = {
    "Andhra Pradesh": ["andhra pradesh"], "Arunachal Pradesh": ["arunachal"],
    "Assam": ["assam", "guwahati"], "Bihar": ["bihar", "patna"],
    "Chhattisgarh": ["chhattisgarh"], "Goa": ["goa"],
    "Gujarat": ["gujarat", "kutch", "kachchh", "bhuj", "ahmedabad", "anjar", "bhachau"],
    "Haryana": ["haryana"], "Himachal Pradesh": ["himachal", "shimla", "kangra", "chamba"],
    "Jharkhand": ["jharkhand"], "Karnataka": ["karnataka"], "Kerala": ["kerala"],
    "Madhya Pradesh": ["madhya pradesh", "jabalpur"],
    "Maharashtra": ["maharashtra", "latur", "koyna", "killari", "mumbai"],
    "Manipur": ["manipur", "imphal"], "Meghalaya": ["meghalaya", "shillong"],
    "Mizoram": ["mizoram", "aizawl"], "Nagaland": ["nagaland", "kohima"],
    "Odisha": ["odisha", "orissa"], "Punjab": ["punjab"], "Rajasthan": ["rajasthan"],
    "Sikkim": ["sikkim", "gangtok", "mangan", "chungthang", "lachung"],
    "Tamil Nadu": ["tamil nadu", "chennai"], "Telangana": ["telangana", "hyderabad"],
    "Tripura": ["tripura", "agartala"],
    "Uttar Pradesh": ["uttar pradesh"],
    "Uttarakhand": ["uttarakhand", "uttaranchal", "uttarkashi", "chamoli", "pithoragarh", "dehradun"],
    "West Bengal": ["west bengal", "darjeeling", "kolkata"],
    "Andaman and Nicobar Islands": ["andaman", "nicobar", "campbell bay", "port blair"],
    "Delhi": ["delhi"], "Jammu and Kashmir": ["jammu", "kashmir", "srinagar"],
    "Ladakh": ["ladakh", "laddakh", "leh", "kargil"],
}
NEIGHBOURS = {
    "Nepal": ["nepal", "kathmandu"], "Bhutan": ["bhutan"], "Myanmar": ["myanmar"],
    "Bangladesh": ["bangladesh"], "Pakistan": ["pakistan"], "Afghanistan": ["afghanistan"],
    "China (Tibet)": ["tibet", "xizang"], "Sri Lanka": ["sri lanka"],
}
HIMALAYA = ["himalaya", "himalayan"]

TOPIC_RULES: dict[str, list[str]] = {
    "legislation_governance": ["act,", "section", "authority", "chapter", "notification", "parliament", "regulation"],
    "response_rescue": ["rescue", "usar", "search and", "ndrf", "response", "deployment", "mobilis", "mobiliz", "evacuat"],
    "relief_logistics": ["relief", "logistic", "shelter", "food", "water", "tent", "supplies", "equipment", "stores"],
    "medical": ["medical", "hospital", "injur", "casualt", "first aid", "triage", "psychosocial"],
    "reconstruction": ["reconstruction", "rehabilitation", "retrofit", "rebuild", "housing", "building code"],
    "damage_assessment": ["damage", "collapse", "crack", "landslide", "loss", "survey"],
    "seismology_hazard": ["magnitude", "epicentre", "epicenter", "seismic", "richter", "tectonic", "aftershock", "zone"],
    "finance": ["fund", "finance", "budget", "compensation", "expenditure", "rs."],
    "preparedness_planning": ["plan", "preparedness", "mitigation", "training", "awareness", "drill", "capacity"],
    "communication": ["communication", "sitrep", "media", "warning", "information"],
}


def _contains(text_l: str, alias: str) -> bool:
    return re.search(rf"(?<![a-z]){re.escape(alias)}(?![a-z])", text_l) is not None


def tag_locations(text: str) -> list[str]:
    tl = text.lower()
    found = [name for name, aliases in {**INDIA_REGIONS, **NEIGHBOURS}.items() if any(_contains(tl, a) for a in aliases)]
    if any(_contains(tl, a) for a in HIMALAYA):
        found.append("Himalayan region")
    return found


def tag_topics(text: str, max_topics: int = 3) -> list[str]:
    tl = text.lower()
    scores = {t: sum(tl.count(k) for k in kws) for t, kws in TOPIC_RULES.items()}
    ranked = [t for t, s in sorted(scores.items(), key=lambda x: -x[1]) if s >= 2]
    return ranked[:max_topics]


def dominant_locations(texts: list[str], top: int = 3) -> list[str]:
    c: Counter[str] = Counter()
    for t in texts:
        c.update(tag_locations(t))
    return [n for n, _ in c.most_common(top)]


def canonical_region(name: str) -> str | None:
    """Map a free-text place (e.g. 'Laddakh') to a canonical region name."""
    nl = name.lower().strip()
    for canon, aliases in {**INDIA_REGIONS, **NEIGHBOURS}.items():
        if nl == canon.lower() or any(_contains(nl, a) for a in aliases):
            return canon
    return None
