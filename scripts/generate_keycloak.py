import json
from pathlib import Path

import yaml

from deployment_utils import (build_keycloak_configuration, read_env)

ROOT = Path(__file__).resolve().parent.parent

CONFIG = ROOT / "deployment.yml"

GLOBAL_ENV = ROOT / ".env"


def main():

    env = read_env(GLOBAL_ENV)

    template_path = ROOT / "realm-template.json"

    with open(CONFIG, encoding="utf8") as file:

        config = yaml.safe_load(file)

    realm = build_keycloak_configuration(env, config, template_path)

    ganabosques_data_str = env.get("GANABOSQUES_DATA", "./volumes")
    
    base_data_path = Path(ganabosques_data_str)
    
    if not base_data_path.is_absolute():
        base_data_path = ROOT / base_data_path
    
    keycloak_import_dir = base_data_path / "keycloak" / "import"
    realm_file = keycloak_import_dir / "realm.json"

    keycloak_import_dir.mkdir(parents=True, exist_ok=True)

    with open(realm_file, "w", encoding="utf8") as file:

        json.dump(realm, file, indent=4)

    print("realm.json generado correctamente.")


if __name__ == "__main__":

    main()