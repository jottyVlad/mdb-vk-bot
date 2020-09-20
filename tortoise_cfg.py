TORTOISE_ORM = {
    "connections": {"default": "sqlite://mdbbot_database.sqlite3"},
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
