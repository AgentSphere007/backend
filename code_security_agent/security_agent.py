import os

TEMP_FOLDER = "C:\\Users\\Niall Dcunha\\backend\\temp_repo_storage"

# ✅ Ignore common non-code file types and metadata
SKIP_LIST = [
    "README.md", "LICENSE", ".gitignore", "__pycache__", ".git",
    ".png", ".jpg", ".jpeg", ".exe", ".dll", ".zip", ".tar", ".pyc"
]

def should_skip(file_path):
    return any(skip in file_path for skip in SKIP_LIST)


def scan_file(file_path):
    issues = []

    if should_skip(file_path):
        return issues

    try:
        with open(file_path, "r", errors="ignore") as f:
            lines = f.readlines()

            for i, line in enumerate(lines, start=1):

                check = line.lower()

                if "os.system(" in check or "subprocess" in check:
                    issues.append((i, line.strip(), "🔴 Dangerous command execution"))

                if "eval(" in check:
                    issues.append((i, line.strip(), "🔴 eval() — RCE risk"))

                if any(word in line.upper() for word in ["API_KEY", "SECRET", "PASSWORD", "TOKEN"]):
                    issues.append((i, line.strip(), "🟡 Hardcoded secret/API key"))

                if "http://" in check:
                    issues.append((i, line.strip(), "🟡 Insecure HTTP request"))

                if "DROP TABLE" in line.upper():
                    issues.append((i, line.strip(), "🔴 SQL injection pattern"))

    except Exception as e:
        issues.append((0, "", f"⚠️ Failed to scan file: {e}"))

    return issues


def scan_repo(repo_path):
    print(f"\n📂 Scanning: {repo_path}")
    report = {}

    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            issues = scan_file(file_path)

            if issues:
                report[file_path] = issues

    return report


def scan_all_repos():
    print("\n🔍 Starting repo scan...")

    for repo in os.listdir(TEMP_FOLDER):
        if repo.startswith("."):
            continue

        repo_path = os.path.join(TEMP_FOLDER, repo)
        if os.path.isdir(repo_path):

            report = scan_repo(repo_path)

            if report:
                print(f"\n🚨 Vulnerabilities found in: {repo}")
                for file_path, issues in report.items():
                    print(f"\n📄 {file_path}")
                    for line_no, snippet, message in issues:
                        print(f"  Line {line_no}: {message}")
                        print(f"     └▶ {snippet}")
            else:
                print(f"✅ {repo}: Clean ✅")


if __name__ == "__main__":
    scan_all_repos()
