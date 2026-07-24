import os
import subprocess
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


with open(os.path.join(ROOT, "deployment.yml"), encoding="utf-8") as file:
    config = yaml.safe_load(file)

for name, repo in config["repositories"].items():
    folder = os.path.join(ROOT, "repos", repo["folder"])
    if not os.path.exists(folder):
        continue

    print(f"Actualizando {name}")
    subprocess.run(["git", "-C", folder, "pull"], check=True)
