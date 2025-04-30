SERVICES = {
    "php": {
        "8.2": {
            "image": "php:8.2-fpm",
            "template": "templates/services/php/8.2/Dockerfile.j2",
            "extensions": ["pdo", "pdo_mysql", "bcmath"],
            "apt": ["libzip-dev"],
            "compose": {
                "build": ".",
                "restart": "always",
                "volumes": ["./app:/var/www/html"],
                "networks": ["docknet"],
                "depends_on": ["mysql"],
                "working_dir": "/var/www/html"
            }
        }
    },
    "mysql": {
        "8.0": {
            "image": "mysql:8.0",
            "template": "templates/services/mysql/docker-compose-snippet.j2",
            "compose": {
                "restart": "always",
                "volumes": ["mysql_data:/var/lib/mysql"],
                "ports": ["3306:3306"],
                "environment": [
                    "MYSQL_ROOT_PASSWORD=root",
                    "MYSQL_DATABASE=app_db",
                    "MYSQL_USER=app_user",
                    "MYSQL_PASSWORD=app_pass"
                ],
                "networks": ["docknet"]
            }
        }
    },
    "redis": {
        "default": {
            "image": "redis:latest",
            "template": "templates/services/redis/docker-compose-snippet.j2",
            "compose": {
                "restart": "always",
                "ports": ["6379:6379"],
                "volumes": ["redis_data:/data"],
                "networks": ["docknet"]
            }
        }
    },
    "postgres": {
        "14": {
            "image": "postgres:14",
            "template": "templates/services/postgres/docker-compose-snippet.j2",
            "compose": {
                "restart": "always",
                "volumes": ["postgres_data:/var/lib/postgresql/data"],
                "ports": ["5432:5432"],
                "environment": [
                    "POSTGRES_USER=postgres",
                    "POSTGRES_PASSWORD=secret",
                    "POSTGRES_DB=app_db"
                ],
                "networks": ["docknet"]
            }
        }
    },
    "nginx": {
        "latest": {
            "image": "nginx:latest",
            "template": "templates/services/nginx/docker-compose-snippet.j2",
            "compose": {
                "restart": "always",
                "ports": ["80:80"],
                "volumes": [
                    "./nginx/default.conf:/etc/nginx/conf.d/default.conf",
                    "./app:/var/www/html"
                ],
                "depends_on": ["php"],
                "networks": ["docknet"]
            }
        }
    }
}
