from git_repo_cloner.repo_cloner import cloner
from secure_checker.security_agent import main
import sys
import os
from dotenv import load_dotenv
from modelReplace.replaceAgent import replaceWithCustomModel

load_dotenv()

repo_name = cloner()
llm_result = main(repo_name)

repo_path = os.path.join("temp", repo_name)


if not llm_result:
    print("❌ Could not interpret security result.")
    sys.exit(1)

core_issues = llm_result.get("core_issues", [])

if not core_issues:
    print("\n✅ Repo is secure — continue process ✅")
    replaceWithCustomModel(repo_path)

else:
    print("\n🚨 Repo flagged! Security issues:")
    for issue in core_issues:
        print(" -", issue)

    print("\n❌ STOP — Cannot proceed with insecure repo.")
    sys.exit(1)
