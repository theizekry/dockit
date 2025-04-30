SERVICES = {
    "php": {
        "7.4": {
            "base_image": "php:7.4-fpm",
            "extensions": ["pdo", "pdo_mysql"],
            "apt": ["libzip-dev", "libonig-dev"],
            "template": "templates/services/php/7.4/Dockerfile.j2"
        },
        "8.2": {
            "base_image": "php:8.2-fpm",
            "extensions": ["pdo", "pdo_mysql", "bcmath"],
            "apt": ["libzip-dev"],
            "template": "templates/services/php/8.2/Dockerfile.j2"
        }
    },
    "mysql": {
        "5.7": {
            "image": "mysql:5.7",
            "env": {"MYSQL_ROOT_PASSWORD": "root"},
            "template": "templates/services/mysql/docker-compose-snippet.j2"
        },
        "8.0": {
            "image": "mysql:8.0",
            "env": {"MYSQL_ROOT_PASSWORD": "root"},
            "template": "templates/services/mysql/docker-compose-snippet.j2"
        }
    },
    "redis": {
        "default": {
            "image": "redis:latest",
            "template": "templates/services/redis/docker-compose-snippet.j2"
        }
    }
}
