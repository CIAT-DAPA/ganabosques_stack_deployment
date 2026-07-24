import yaml
from pathlib import Path

from deployment_utils import (
    build_env_variables,
    read_env,
)

ROOT = Path(__file__).resolve().parent.parent

CONFIG = ROOT / "deployment.yml"

REPOS = ROOT / "repos"

GLOBAL_ENV = ROOT / ".env"


def write_env(path, data):

    with open(path, "w", encoding="utf-8") as file:

        for key, value in data.items():

            file.write(f"{key}={value}\n")


def main():

    if not GLOBAL_ENV.exists():

        print("Error: No se encontró el archivo .env global.")

        return

    global_env_data = read_env(GLOBAL_ENV)

    with open(CONFIG, encoding="utf-8") as file:

        config = yaml.safe_load(file)

    docker_values = build_env_variables(global_env_data)

    for name, repo in config["repositories"].items():

        project = REPOS / repo["folder"]

        example = project / repo["env_file"]

        target = project / ".env"

        if not example.exists():

            print(f"No existe {example}")

            continue

        print(f"Configurando {name}")

        env = read_env(example)

        #
        # 1. Variables iguales entre .env global y .env del proyecto
        #

        for key in env:

            if key in global_env_data:

                env[key] = global_env_data[key]

        #
        # 2. Variables calculadas por el instalador
        #

        for key, value in docker_values.items():

            if key in env:

                env[key] = value

        #
        # 3. Variables mapeadas
        #

        mapping = repo.get("env_map", {})

        for target_key, source_key in mapping.items():

            if target_key not in env:
                continue

            if source_key not in global_env_data:
                continue

            env[target_key] = global_env_data[source_key]

        write_env(target, env)


if __name__ == "__main__":

    main()