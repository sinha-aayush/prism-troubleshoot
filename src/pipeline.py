import json
from typing import Optional
import anthropic
import time

client = anthropic.Anthropic()

# Simple in-memory cache
query_cache = {}

# STAGE 0: Query Enrichment
def enrich_query(raw_complaint: str) -> dict:
    """Convert vague complaint → technical query"""
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"""Convert this Samsung device complaint into a technical query and category.
Complaint: "{raw_complaint}"

Respond ONLY with JSON (no markdown, no backticks):
{{"technical_query": "...", "issue_category": "..."}}"""
            }]
        )
        result = json.loads(response.content[0].text)
        return result
    except Exception as e:
        print(f"Enrichment error: {e}")
        return {
            "technical_query": raw_complaint,
            "issue_category": "general"
        }

# STAGE 1: Structure Extraction
def extract_steps(technical_query: str, issue_category: str) -> dict:
    """Extract Goal, Actions, Steps using Claude"""
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            messages=[{
                "role": "user",
                "content": f"""Generate troubleshooting steps for this Samsung device issue.
Issue: {technical_query}
Category: {issue_category}

RESPOND ONLY WITH VALID JSON (no markdown, no extra text):
{{
  "goal": "Follow these steps to fix [issue]",
  "title": "Troubleshooting [issue name]",
  "score": 0.85,
  "actions": [
    {{
      "actionName": "Step 1 Action",
      "description": "Navigate to settings",
      "category": "auto",
      "stepGroups": [{{
        "steps": [
          "Open Settings app",
          "Tap on Display",
          "Find and enable option"
        ],
        "validationDeeplink": "bixby://dummy_positive",
        "actionableDeeplink": "bixby://dummy_positive"
      }}]
    }},
    {{
      "actionName": "Step 2 Action",
      "description": "Restart device",
      "category": "manual",
      "stepGroups": [{{
        "steps": [
          "Power off device",
          "Wait 30 seconds",
          "Power on again"
        ],
        "validationDeeplink": "bixby://dummy_positive",
        "actionableDeeplink": "bixby://dummy_positive"
      }}]
    }}
  ]
}}"""
            }]
        )
        result = json.loads(response.content[0].text)
        return result
    except Exception as e:
        print(f"Extraction error: {e}")
        return {
            "goal": f"Fix {technical_query}",
            "title": "Troubleshooting Steps",
            "score": 0.5,
            "actions": []
        }

# STAGE 2 & 3: Deeplink Mapping + Cache
def map_deeplinks(actions: list) -> list:
    """Attach deeplinks to actions (dummy for prototype)"""
    deeplink_map = {
        "display": "bixby://dummy_positive",
        "battery": "bixby://dummy_positive",
        "performance": "bixby://dummy_positive",
        "navigation": "bixby://dummy_positive",
    }
    
    for action in actions:
        action_name_lower = action.get("actionName", "").lower()
        for key in deeplink_map:
            if key in action_name_lower:
                for sg in action.get("stepGroups", []):
                    sg["validationDeeplink"] = deeplink_map[key]
                    sg["actionableDeeplink"] = deeplink_map[key]
                break
    
    return actions

# MAIN PIPELINE
def get_troubleshooting_plan(complaint: str, siis_text: Optional[str] = None) -> dict:
    """Full 4-stage pipeline"""
    start_time = time.time()
    
    # Check cache
    if complaint in query_cache:
        cached = query_cache[complaint].copy()
        cached["meta"]["cache_hit"] = True
        cached["meta"]["latency_ms"] = int((time.time() - start_time) * 1000)
        return cached
    
    # Stage 0: Enrich
    enriched = enrich_query(complaint)
    technical_query = enriched["technical_query"]
    issue_category = enriched["issue_category"]
    
    # Stage 1: Extract
    plan = extract_steps(technical_query, issue_category)
    
    # Stage 2: Map deeplinks
    plan["actions"] = map_deeplinks(plan.get("actions", []))
    
    # Build response
    response = {
        "contexts": [plan],
        "meta": {
            "cache_hit": False,
            "latency_ms": int((time.time() - start_time) * 1000),
            "model": "claude-3-5-sonnet-20241022",
            "cost_usd": 0.015
        }
    }
    
    # Cache it
    query_cache[complaint] = response
    
    return response