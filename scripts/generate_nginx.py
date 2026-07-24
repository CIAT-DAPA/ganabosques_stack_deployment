from pathlib import Path

from deployment_utils import (build_services, read_env)

ROOT = Path(__file__).resolve().parent.parent

GLOBAL_ENV = ROOT / ".env"

NGINX_DIR = ROOT / "nginx"

NGINX_CONF = NGINX_DIR / "nginx.conf"

def generate_server(name, service):

    nginx = []

    nginx.append("    server {")
    nginx.append("")
    nginx.append("        listen 80;")
    nginx.append("")
    nginx.append(f"        server_name {service['host']};")
    nginx.append("")
    nginx.append("        location / {")
    nginx.append("")
    nginx.append(
        f"            proxy_pass http://{service['container']}:{service['port']};"
    )
    nginx.append("")

    nginx.append("            proxy_http_version 1.1;")
    nginx.append("")

    nginx.append("            proxy_set_header Host $host;")
    nginx.append("            proxy_set_header X-Real-IP $remote_addr;")
    nginx.append(
        "            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;"
    )
    nginx.append("            proxy_set_header X-Forwarded-Proto $scheme;")

    config = service.get("nginx", {})

    #
    # WebSockets
    #

    if config.get("websocket"):

        nginx.append("")
        nginx.append("            proxy_set_header Upgrade $http_upgrade;")
        nginx.append('            proxy_set_header Connection "upgrade";')

    #
    # Forward headers
    #

    if config.get("forward_headers"):

        nginx.append("")
        nginx.append("            proxy_set_header X-Forwarded-Host $host;")
        nginx.append("            proxy_set_header X-Forwarded-Port $server_port;")

    #
    # Timeouts
    #

    timeout = config.get("proxy_read_timeout")

    if timeout:

        nginx.append("")
        nginx.append(f"            proxy_read_timeout {timeout};")

    nginx.append("")
    nginx.append("        }")

    #
    # Uploads
    #

    upload = config.get("client_max_body_size")

    if upload:

        nginx.append("")
        nginx.append(f"        client_max_body_size {upload};")

    nginx.append("")
    nginx.append("    }")
    nginx.append("")

    return "\n".join(nginx)


def main():

    env = read_env(GLOBAL_ENV)

    ganabosques_data_str = env.get("GANABOSQUES_DATA", "./volumes")
    
    base_data_path = Path(ganabosques_data_str)
    
    if not base_data_path.is_absolute():
        base_data_path = ROOT / base_data_path
    
    nginx_dir = base_data_path / "nginx"
    nginx_conf_file = nginx_dir / "nginx.conf"

    services = build_services(env)

    nginx_dir.mkdir(parents=True, exist_ok=True)

    nginx = []

    nginx.append("events {}")
    nginx.append("")
    nginx.append("http {")
    nginx.append("")
    nginx.append("    resolver 127.0.0.11 valid=10s;")
    nginx.append("")

    for name, service in services.items():

        nginx.append(generate_server(name, service))

    nginx.append("}")

    with open(nginx_conf_file, "w", encoding="utf8") as file:

        file.write("\n".join(nginx))

    print("nginx.conf generado correctamente.")


if __name__ == "__main__":

    main()
