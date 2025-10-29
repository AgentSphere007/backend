# import os
# from dotenv import load_dotenv
# import google.generativeai as genai
# import textwrap
# import json

# load_dotenv()

# TEMP_FOLDER = os.getenv("repo_stor")
# GEMINI_API_KEY = os.getenv("api_key")
# if not TEMP_FOLDER:
#     raise RuntimeError("Environment variable 'repo_stor' not set")
# if not GEMINI_API_KEY:
#     raise RuntimeError("Environment variable 'api_key' not set")

# # Configure Gemini
# genai.configure(api_key=GEMINI_API_KEY)
# model = genai.GenerativeModel("gemini-2.5-flash")

# # --- Scanning config (your previous lists) ---
# SKIP_LIST = [
#     "README.md", "LICENSE", ".gitignore", "__pycache__", ".git",
#     ".png", ".jpg", ".jpeg", ".exe", ".dll", ".zip", ".tar", ".pyc", ".venv", "node_modules", ".txt"
# ]

# system_prompt_keywords = [
#     'ROLE:"SYSTEM"', "ROLE': 'SYSTEM'", "SYSTEMMESSAGE",
#     "SYSTEM_PROMPT", "BASE_PROMPT", "INITIAL_PROMPT",
#     "YOU ARE", "ACT AS", "INSTRUCTION", "JAILBREAK"
# ]

# sql_injection_identifiers = [
#     # Core SQL Keywords
#     "SELECT", "UNION", "INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE",
#     "ALTER", "EXEC", "EXECUTE", "DECLARE", "CAST", "CONVERT",
#     "WHERE", "INTO", "VALUES",

#     # Metadata / Discovery Queries
#     "INFORMATION_SCHEMA", "ALL_TABLES", "ALL_USERS", "PG_CATALOG",
#     "MYSQL.DB", "SYSOBJECTS", "@@VERSION",

#     # Dangerous Functions
#     "xp_cmdshell", "sp_executesql", "EXECUTE IMMEDIATE",

#     # File & System Exfiltration
#     "INTO OUTFILE", "LOAD_FILE", "INTO DUMPFILE",

#     # Time-based / Blind SQL Injection
#     "SLEEP(", "BENCHMARK(", "WAITFOR DELAY",

#     # Tautologies & Injection Payloads
#     "' OR '1'='1", '" OR "1"="1', "OR 1=1", "' OR 1=1 --",
#     "') OR ('1'='1",

#     # Known SQLi Attack Patterns
#     "UNION SELECT", "OR 1=1", "LIKE '%'",
#     "ORDER BY", "GROUP BY",

#     # Injections through dynamic SQL
#     "cursor.execute(", "db.query(", "prepare(", "exec("
# ]

# # --- Utilities ---
# def should_skip(file_path: str) -> bool:
#     # Skip common non-code and repo metadata files/folders
#     normalized = file_path.replace("\\", "/").lower()
#     for skip in SKIP_LIST:
#         if skip.lower() in normalized:
#             return True
#     return False

# def scan_file(file_path: str):
#     """Return list of (line_no, snippet, message) for the file."""
#     issues = []
#     if should_skip(file_path):
#         return issues

#     try:
#         with open(file_path, "r", errors="ignore") as f:
#             lines = f.readlines()
#     except Exception as e:
#         issues.append((0, "", f"⚠️ Failed to open file: {e}"))
#         return issues

#     for i, raw_line in enumerate(lines, start=1):
#         line = raw_line.rstrip("\n")
#         lower = line.lower()

#         # Dangerous executions
#         if "os.system(" in lower or "subprocess.popen(" in lower or "subprocess.call(" in lower:
#             issues.append((i, line.strip(), "🔴 Dangerous command execution"))

#         # eval / exec
#         if "eval(" in lower or "exec(" in lower:
#             issues.append((i, line.strip(), "🔴 eval/exec usage — RCE risk"))

#         # Hardcoded secrets
#         for secret_kw in ("api_key", "secret", "password", "token", "access_key", "secret_key"):
#             if secret_kw in line.lower():
#                 issues.append((i, line.strip(), "🟡 Hardcoded secret/API key detected"))
#                 break

#         # Insecure HTTP
#         if "http://" in lower:
#             issues.append((i, line.strip(), "🟡 Insecure (non-HTTPS) request detected"))

#         # SQL injection heuristics
#         upper = line.upper()
#         for query in sql_injection_identifiers:
#             if query.upper() in upper:
#                 issues.append((i, line.strip(), "🔴 Potential SQL injection pattern"))
#                 break

#         # System prompt detection
#         for kw in system_prompt_keywords:
#             if kw.upper() in line.upper():
#                 issues.append((i, line.strip(), "🔵 Potential system/base prompt found"))
#                 break

#     return issues

# def scan_repo(repo_path: str):
#     """Scan a single cloned repo directory and return a dict: file -> list of issues."""
#     report = {}
#     for root, _, files in os.walk(repo_path):
#         for file in files:
#             file_path = os.path.join(root, file)
#             issues = scan_file(file_path)
#             if issues:
#                 report[file_path] = issues
#     return report

# def scan_all_repos():
#     """Return a combined report dict: repo_name -> { file_path: [issues] }"""
#     combined = {}
#     for repo in os.listdir(TEMP_FOLDER):
#         if repo.startswith("."):  # skip .git and hidden dirs at top level
#             continue
#         repo_path = os.path.join(TEMP_FOLDER, repo)
#         if os.path.isdir(repo_path):
#             report = scan_repo(repo_path)
#             if report:
#                 combined[repo] = report
#     return combined

# # --- Prepare a strong system prompt for Gemini ---
# SYSTEM_PROMPT = textwrap.dedent("""
# You are a concise, security-focused assistant. 
# Task: Given a textual security scan report (list of files with line-numbered flagged lines and labels),
# return a short JSON object with three fields:
#   1) "summary": a 1-3 sentence human-readable summary of the overall risk (no more than 40 words).
#   2) "core_issues": an array of strings each describing a single high-priority problem (limit to top 5).
#      Each item must include: repo name, file path (basename), issue type, and brief explanation.
#      Example entry: "MTRagEval: generation_referenced.py - Hardcoded secrets found (contains API keys in code)"
#   3) "recommendations": array of 1-3 prioritized remediation steps (very short).
# Return valid JSON ONLY. If no issues found, return:
#   {"summary":"No critical issues found.","core_issues":[],"recommendations":[]}
# Be conservative: only treat items as high-priority if they are dangerous (e.g. hardcoded secrets, eval/exec, command execution, SQLi patterns, prompt injections). Read through the lines of code in which the threats were detected, if the threats are baseless like threats found in import statements, comments etc, then ignore it. 
# In the case of api's if for eg: api_key = variable name, then pass it off as not a threat, if there is an api key hardcoded eg: api_key = "cwbfdsbcdczodbvsxsxawe2783", then flag it.
# Do NOT invent file contents; base conclusions only on the supplied report text.
# """).strip()

# def format_report_for_llm(combined_report: dict) -> str:
#     """
#     Build a compact text the LLM can consume. Keep it small but informative.
#     Format:
#       REPO: <name>
#       FILE: <path>
#       - LINE <n>: <message> | <code snippet>
#     """
#     parts = []
#     for repo, files in combined_report.items():
#         parts.append(f"REPO: {repo}")
#         for fp, issues in files.items():
#             # use basename for brevity
#             basename = os.path.basename(fp)
#             parts.append(f"FILE: {basename} (full_path: {fp})")
#             for line_no, snippet, message in issues:
#                 safe_snip = snippet.replace("\n", " ").strip()
#                 parts.append(f"- LINE {line_no}: {message} | {safe_snip}")
#         parts.append("")  # blank line between repos
#     if not parts:
#         return "No findings."
#     return "\n".join(parts)

# def call_gemini_and_extract_core(report_text: str) -> str:
#     """
#     Send the formatted report_text to Gemini and return its JSON response (string),
#     which should contain 'summary', 'core_issues', and 'recommendations'.
#     """
#     full_prompt = SYSTEM_PROMPT + "\n\nREPORT:\n" + report_text

#     # model.generate_content accepts structured input in newer SDKs; keeping simple string usage
#     try:
#         response = model.generate_content(full_prompt)
#     except Exception as e:
#         return json.dumps({
#             "error": f"LLM call failed: {str(e)}"
#         })

#     # response.text is typically the textual output
#     text = getattr(response, "text", None) or str(response)
#     # Try to be helpful and ensure JSON output:
#     # If the LLM returned JSON-like text, attempt to parse; otherwise, return raw text.
#     try:
#         parsed = json.loads(text)
#         return json.dumps(parsed, indent=2)
#     except Exception:
#         # Not valid JSON — return raw answer but wrapped
#         return json.dumps({
#             "raw_output": text
#         }, indent=2)

# # --- Main flow ---
# def main():
#     combined = scan_all_repos()

#     if not combined:
#         print("✅ No issues detected across repos.")
#         # Still call LLM with a short message if you want a final check:
#         result = call_gemini_and_extract_core("No findings.")
#         print("LLM Response:\n", result)
#         return

#     formatted = format_report_for_llm(combined)
#     print("\n--- Formatted report sent to LLM ---\n")
#     print(formatted[:2000])  # print first 2k chars for quick debugging

#     llm_result = call_gemini_and_extract_core(formatted)
#     print("\n--- LLM Core Security Issues (JSON) ---\n")
#     print(llm_result)








import os
from dotenv import load_dotenv
import google.generativeai as genai
import textwrap
import json
import re

load_dotenv()

TEMP_FOLDER = os.getenv("repo_stor")
GEMINI_API_KEY = os.getenv("api_key")

if not TEMP_FOLDER:
    raise RuntimeError("Environment variable 'repo_stor' not set")
if not GEMINI_API_KEY:
    raise RuntimeError("Environment variable 'api_key' not set")

# Configure Gemini
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

    original = raw_text

    # Step 1️⃣: Try outer JSON first
    try:
        outer = json.loads(raw_text)
        if isinstance(outer, dict) and "raw_output" in outer:
            raw_text = outer["raw_output"]
    except:
        pass

    # Step 2️⃣: Remove code fences like ```json ... ```
    raw_text = re.sub(r"```json|```", "", raw_text, flags=re.IGNORECASE).strip()

    # Step 3️⃣: Extract first valid JSON object using regex
    json_match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
    if not json_match:
        print("⚠️ Could not locate JSON braces. Raw output:\n", original)
        return None
    
    json_block = json_match.group(0)

    # Step 4️⃣: Parse cleaned JSON safely
    try:
        return json.loads(json_block)
    except json.JSONDecodeError as e:
        print("⚠️ JSON decode failure:", e)
        print("📌 Debug JSON block:\n", json_block)
        return None

    
# Skip list
SKIP_LIST = [
    "README.md", "LICENSE", ".gitignore", "__pycache__", ".git",
    ".png", ".jpg", ".jpeg", ".exe", ".dll", ".zip", ".tar",
    ".pyc", ".venv", "node_modules", ".txt"
]

# Prompt security keywords
system_prompt_keywords = [
    'ROLE:"SYSTEM"', "ROLE': 'SYSTEM'", "SYSTEMMESSAGE",
    "SYSTEM_PROMPT", "BASE_PROMPT", "INITIAL_PROMPT",
    "YOU ARE", "ACT AS", "INSTRUCTION", "JAILBREAK"
]

# SQL injection patterns
sql_injection_identifiers = [
    "SELECT", "UNION", "INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE",
    "ALTER", "EXEC", "EXECUTE", "DECLARE", "CAST", "CONVERT",
    "WHERE", "INTO", "VALUES",
    "INFORMATION_SCHEMA", "ALL_TABLES", "ALL_USERS", "PG_CATALOG",
    "MYSQL.DB", "SYSOBJECTS", "@@VERSION",
    "xp_cmdshell", "sp_executesql", "EXECUTE IMMEDIATE",
    "INTO OUTFILE", "LOAD_FILE", "INTO DUMPFILE",
    "SLEEP(", "BENCHMARK(", "WAITFOR DELAY",
    "' OR '1'='1", '" OR "1"="1', "OR 1=1", "' OR 1=1 --",
    "') OR ('1'='1", "UNION SELECT", "LIKE '%'",
    "ORDER BY", "GROUP BY", "cursor.execute(", "db.query(", "prepare(", "exec("
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

        # Command execution
        if "os.system(" in lower or "subprocess" in lower:
            issues.append((i, line, "🔴 Dangerous command execution"))

        # eval/exec
        if "eval(" in lower or "exec(" in lower:
            issues.append((i, line, "🔴 eval/exec — RCE risk"))

        # Hardcoded keys
        for secret_kw in ["api_key", "secret", "password", "token"]:
            if secret_kw in lower and '"' in line:
                issues.append((i, line, "🟡 Hardcoded secret/API key"))
                break

        # HTTP
        if "http://" in lower:
            issues.append((i, line, "🟡 Insecure HTTP request"))

        # SQL Injection
        if any(q in upper for q in sql_injection_identifiers):
            issues.append((i, line, "🔴 Potential SQL injection"))

        # System Prompt attacks
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
SYSTEM_PROMPT = textwrap.dedent("""
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
""").strip()


def format_report_for_llm(combined_report):
    out = []
    for repo, files in combined_report.items():
        out.append(f"REPO: {repo}")
        for fp, issues in files.items():
            base = os.path.basename(fp)
            for (line, snippet, msg) in issues:
                out.append(f"FILE: {base} | LINE {line}: {msg} | CODE: {snippet}")
    return "\n".join(out) if out else "No findings."

def call_gemini(report_text):
    try:
        resp = model.generate_content(SYSTEM_PROMPT + "\n\n" + report_text)
        text = resp.text
        return json.dumps(json.loads(text), indent=2)
    except Exception:
        return json.dumps({"raw_output": text}, indent=2)

# ✅ Main Entry — scan one repo
def main(repo_name):
    print(f"\n🔍 Scanning repo: {repo_name}")
    
    # Scan repository
    report = scan_single_repo(repo_name)

    # ✅ Print raw scan results
    print("\n📌 Intermediate Scan Results (Before AI Analysis)\n")
    
    if not report.get(repo_name):
        print("✅ No flagged security issues found in static scan ✅")
    else:
        for file_path, issues in report[repo_name].items():
            print(f"\n📄 File: {file_path}")
            for (line, snippet, msg) in issues:
                print(f"  🔹 Line {line}: {msg}")
                print(f"     └▶ Code: {snippet}")

    # Format report for LLM
    formatted = format_report_for_llm(report)

    print("\n📤 Sending findings to Gemini for risk assessment...\n")
    
    # Get AI processed result
    llm_result = call_gemini(formatted)

    print("\n🤖 Gemini Security Assessment (JSON) 📦")
    print(llm_result)
    parsed = parse_llm_result(llm_result)
    return parsed


# if __name__ == "__main__":
#     repo = input("Enter repo folder name inside temp storage: ").strip()
#     main(repo)
