import os
import subprocess
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG = os.path.join(ROOT, "deployment.yml")

REPOS_PATH = os.path.join(ROOT, "repos")

def main():

    with open(CONFIG, encoding="utf-8") as file:
        config = yaml.safe_load(file)

    os.makedirs(REPOS_PATH, exist_ok=True)

    for name, repo in config["repositories"].items():
        folder = os.path.join(REPOS_PATH, repo["folder"])

        if os.path.exists(folder):
            print(f"✓ {name} ya existe")
            continue

        print(f"Clonando {name}")

        subprocess.run(
            ["git", "clone", "--branch", repo["branch"], repo["url"], folder],
            check=True,
        )

if __name__ == "__main__":
    main()
