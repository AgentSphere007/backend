import os
import subprocess
import sys
import importlib.util

def ensure_pipreqs_installed():
    """Check if pipreqs is installed; if not, install it automatically."""
    if importlib.util.find_spec("pipreqs") is None:
        print("⚠️ pipreqs not found. Installing now...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pipreqs"], check=True)
        print("✅ pipreqs installed successfully.")

def generate_requirements(repo_path: str):
    """
    Looks for all .py files in repo_path and uses pipreqs
    to generate a requirements.txt inside that same directory.
    """
    if not os.path.exists(repo_path):
        print(f"❌ Directory does not exist: {repo_path}")
        return

    # Check for .py files (recursively)
    py_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))

    if not py_files:
        print("⚠️ No Python files found in this directory.")
        return

    print(f"✅ Found {len(py_files)} Python files.")
    print("📦 Generating requirements.txt using pipreqs...")

    # Ensure pipreqs exists before running
    ensure_pipreqs_installed()

    # Run pipreqs command
    try:
        subprocess.run(
            ["pipreqs", repo_path, "--force"],
            check=True
        )
        print(f"✅ requirements.txt created successfully at: {os.path.join(repo_path, 'requirements.txt')}")
    except subprocess.CalledProcessError as e:
        print(f"❌ pipreqs failed with error: {e}")


