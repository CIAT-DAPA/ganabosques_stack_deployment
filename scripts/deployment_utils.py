from pathlib import Path
import copy
import json

SERVICE_TARGETS = {

    "app": {

        "container": "app",

        "port": 3000,

        "subdomain_env": "SUBDOMAIN_APP",

        "nginx": {
            "websocket": True
        }

    },

    "web_admin": {

        "container": "web-admin",

        "port": 5000,

        "subdomain_env": "SUBDOMAIN_WEB_ADMIN",

        "nginx": {
            "proxy_read_timeout": 300
        }

    },

    "api": {

        "container": "api",

        "port": 8000,

        "subdomain_env": "SUBDOMAIN_API",

        "nginx": {
            "proxy_read_timeout": 300
        }

    },

    "keycloak": {

        "container": "keycloak",

        "port": 8080,

        "subdomain_env": "SUBDOMAIN_KEYCLOAK",

        "nginx": {

            "forward_headers": True,

            "proxy_read_timeout": 300

        }

    },

    "geoserver": {

        "container": "geoserver",

        "port": 8080,

        "subdomain_env": "SUBDOMAIN_GEOSERVER",

        "nginx": {

            "client_max_body_size": "100M",

            "proxy_read_timeout": 300

        }

    }

}


def build_services(global_env):

    use_proxy = global_env.get(
        "USE_PROXY",
        "false"
    ).lower() == "true"


    domain = global_env.get(
        "DOMAIN",
        "localhost"
    )


    services = {}


    for name, info in SERVICE_TARGETS.items():


        if use_proxy:

            subdomain = global_env.get(
                info["subdomain_env"],
                name
            )

            host = f"{subdomain}.{domain}"


        else:

            subdomain = global_env.get(
                info["subdomain_env"],
                name
            )

            host = f"{subdomain}.localhost"



        services[name] = {

            "host": host,

            "container": info["container"],

            "port": info["port"],

            "nginx": info.get("nginx", {})

        }

    return services

def build_env_variables(global_env):

    services = build_services(global_env)

    return {

        "MONGO_URI":
            "mongodb://mongo:27017",

        "API_BASE_URL":
            f"http://{services['api']['host']}",

        "NEXT_PUBLIC_API_URL":
            f"http://{services['api']['host']}/",

        "KEYCLOAK_URL":
            f"http://{services['keycloak']['host']}",

        "KEYCLOAK_SERVER_URL":
            f"http://{services['keycloak']['host']}",

        "NEXT_PUBLIC_KEYCLOAK_URL":
            f"http://{services['keycloak']['host']}",

        "GEOSERVER_URL":
            f"http://{services['geoserver']['host']}/geoserver/rest/",

        "URL_GEO":
            f"http://{services['geoserver']['host']}/geoserver",

        "NEXT_PUBLIC_APP_URL":
            f"http://{services['app']['host']}",

        "WEB_ADMIN_URL":
            f"http://{services['web_admin']['host']}"

    }


def build_admin_user(env, config):

    admin = config["keycloak"]["admin_user"]

    return {

        "username": env[admin["username"]],

        "enabled": True,

        "emailVerified": True,

        "firstName": env[admin["first_name"]],

        "lastName": env[admin["last_name"]],

        "email": env[admin["email"]],

        "credentials": [

            {

                "type": "password",

                "value": env[admin["password"]],

                "temporary": False

            }

        ]

    }

def replace_placeholders(obj, values):
    """
    Reemplaza recursivamente los placeholders dentro del template.
    """

    if isinstance(obj, dict):
        return {
            k: replace_placeholders(v, values)
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [
            replace_placeholders(v, values)
            for v in obj
        ]

    if isinstance(obj, str):

        for placeholder, value in values.items():

            obj = obj.replace(
                placeholder,
                str(value)
            )

        return obj

    return obj

def build_keycloak_configuration(env, config, template_path):

    with open(template_path, encoding="utf8") as f:
        realm = json.load(f)

    urls = build_env_variables(env)

    values = {
        "__KEYCLOAK_REALM__": env["KEYCLOAK_REALM"],
        "__KEYCLOAK_CLIENT_ID__": env["KEYCLOAK_CLIENT_ID"],
        "__KEYCLOAK_WEB_CLIENT_ID__": env["KEYCLOAK_WEB_CLIENT_ID"],
        "__KEYCLOAK_CLIENT_SECRET__": env["KEYCLOAK_CLIENT_SECRET"],

        "__APP_URL__": urls["NEXT_PUBLIC_APP_URL"],
        "__WEB_ADMIN_URL__": urls["WEB_ADMIN_URL"],
        "__KEYCLOAK_URL__": urls["KEYCLOAK_URL"],
    }

    realm = replace_placeholders(
        realm,
        values
    )


    realm.setdefault(
        "users",
        []
    ).append(
        build_admin_user(env, config)
    )

    return realm

def read_env(path):
    """Lee cualquier archivo .env y lo transforma en diccionario."""
    data = {}
    if not path.exists():
        return data
    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                data[key] = value
    return data


