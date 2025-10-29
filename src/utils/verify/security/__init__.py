import os
import google.generativeai as genai
import textwrap
import json
import re

from src.config import config


TEMP_FOLDER = os.path.join("temp")
GEMINI_API_KEY = config.app.gemini_api_key

if not TEMP_FOLDER:
    raise RuntimeError("Environment variable 'repo_stor' not set")
if not GEMINI_API_KEY:
    raise RuntimeError("Environment variable 'api_key' not set")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

import json
import re


def parse_llm_result(raw_text: str):
    """
    Extract proper JSON from Gemini output even when wrapped in raw_output strings
    and markdown code fences.
    """
    if not raw_text:
        return None
    try:
        outer = json.loads(raw_text)
        if isinstance(outer, dict) and "raw_output" in outer:
            raw_text = outer["raw_output"]
    except:
        pass
    raw_text = re.sub(r"```json|```", "", raw_text, flags=re.IGNORECASE).strip()
    json_match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
    if not json_match:
        # print("⚠️ Could not locate JSON braces. Raw output:\n", original)
        return None
    json_block = json_match.group(0)
    try:
        return json.loads(json_block)
    except json.JSONDecodeError as e:
        # print("⚠️ JSON decode failure:", e)
        # print("📌 Debug JSON block:\n", json_block)
        return None


SKIP_LIST = [
    "README.md",
    "LICENSE",
    ".gitignore",
    "__pycache__",
    ".git",
    ".png",
    ".jpg",
    ".jpeg",
    ".exe",
    ".dll",
    ".zip",
    ".tar",
    ".pyc",
    ".venv",
    "node_modules",
    ".txt",
]

# Prompt security keywords
system_prompt_keywords = [
    'ROLE:"SYSTEM"',
    "ROLE': 'SYSTEM'",
    "SYSTEMMESSAGE",
    "SYSTEM_PROMPT",
    "BASE_PROMPT",
    "INITIAL_PROMPT",
    "YOU ARE",
    "ACT AS",
    "INSTRUCTION",
    "JAILBREAK",
]

# SQL injection patterns
sql_injection_identifiers = [
    "SELECT",
    "UNION",
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "TRUNCATE",
    "ALTER",
    "EXEC",
    "EXECUTE",
    "DECLARE",
    "CAST",
    "CONVERT",
    "WHERE",
    "INTO",
    "VALUES",
    "INFORMATION_SCHEMA",
    "ALL_TABLES",
    "ALL_USERS",
    "PG_CATALOG",
    "MYSQL.DB",
    "SYSOBJECTS",
    "@@VERSION",
    "xp_cmdshell",
    "sp_executesql",
    "EXECUTE IMMEDIATE",
    "INTO OUTFILE",
    "LOAD_FILE",
    "INTO DUMPFILE",
    "SLEEP(",
    "BENCHMARK(",
    "WAITFOR DELAY",
    "' OR '1'='1",
    '" OR "1"="1',
    "OR 1=1",
    "' OR 1=1 --",
    "') OR ('1'='1",
    "UNION SELECT",
    "LIKE '%'",
    "ORDER BY",
    "GROUP BY",
    "cursor.execute(",
    "db.query(",
    "prepare(",
    "exec(",
]


def should_skip(file_path):
    normalized = file_path.replace("\\", "/").lower()
    return any(skip.lower() in normalized for skip in SKIP_LIST)


def scan_file(file_path):
    issues = []
    if should_skip(file_path):
        return issues
    try:
        with open(file_path, "r", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        return [(0, "", f"⚠️ Failed to open file: {e}")]
    for i, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")
        lower = line.lower()
        upper = line.upper()
        if "os.system(" in lower or "subprocess" in lower:
            issues.append((i, line, "🔴 Dangerous command execution"))
        if "eval(" in lower or "exec(" in lower:
            issues.append((i, line, "🔴 eval/exec — RCE risk"))
        for secret_kw in ["api_key", "secret", "password", "token"]:
            if secret_kw in lower and '"' in line:
                issues.append((i, line, "🟡 Hardcoded secret/API key"))
                break
        if "http://" in lower:
            issues.append((i, line, "🟡 Insecure HTTP request"))
        if any(q in upper for q in sql_injection_identifiers):
            issues.append((i, line, "🔴 Potential SQL injection"))
        if any(k in upper for k in system_prompt_keywords):
            issues.append((i, line, "🔵 Potential system prompt"))

    return issues


def scan_repo(repo_path):
    report = {}
    for root, _, files in os.walk(repo_path):
        for f in files:
            path = os.path.join(root, f)
            issues = scan_file(path)
            if issues:
                report[path] = issues
    return report


def scan_single_repo(repo_name):
    repo_path = os.path.join(TEMP_FOLDER, repo_name)
    if not os.path.isdir(repo_path):
        raise RuntimeError(f"Repository '{repo_name}' not found in {TEMP_FOLDER}")
    return {repo_name: scan_repo(repo_path)}


# Strong system prompt for Gemini
SYSTEM_PROMPT = textwrap.dedent(
    """
You are a concise, security-focused assistant. 
Task: Given a textual security scan report (list of files with line-numbered flagged lines and labels),
return a short JSON object with three fields:
  1) "summary": a 1-3 sentence human-readable summary of the overall risk (no more than 40 words).
  2) "core_issues": an array of strings each describing a single high-priority problem (limit to top 5).
     Each item must include: repo name, file path (basename), issue type, and brief explanation.
     Example entry: "MTRagEval: generation_referenced.py - Hardcoded secrets found (contains API keys in code)"
  3) "recommendations": array of 1-3 prioritized remediation steps (very short).
Return valid JSON ONLY. If no issues found, return:
  {"summary":"No critical issues found.","core_issues":[],"recommendations":[]}
Be conservative: only treat items as high-priority if they are dangerous (e.g. hardcoded secrets, eval/exec, command execution, SQLi patterns, prompt injections). Read through the lines of code in which the threats were detected, if the threats are baseless like threats found in import statements, comments etc, then ignore it. 
In the case of api's or secret keys if for eg: api_key = variable name, then pass it off as not a threat, if there is an api key hardcoded eg: api_key = "cwbfdsbcdczodbvsxsxawe2783", then flag it.
Do NOT invent file contents; base conclusions only on the supplied report text.
"""
).strip()


def format_report_for_llm(combined_report):
    out = []
    for repo, files in combined_report.items():
        out.append(f"REPO: {repo}")
        for fp, issues in files.items():
            base = os.path.basename(fp)
            for line, snippet, msg in issues:
                out.append(f"FILE: {base} | LINE {line}: {msg} | CODE: {snippet}")
    return "\n".join(out) if out else "No findings."


def call_gemini(report_text) -> dict:
    try:
        resp = model.generate_content(SYSTEM_PROMPT + "\n\n" + report_text)
        text = resp.text
        return json.loads(text)
    except Exception:
        return {"raw_output": report_text}


def check_secure(repo_name: str) -> dict:
    report = scan_single_repo(repo_name)
    formatted = format_report_for_llm(report)
    llm_result = call_gemini(formatted)
    return llm_result
