ENV = "production"
SERVER_NAME = "pfarre-machstrasse.at"
PREFERRED_URL_SCHEME = "https"
FILE_STORE = "./files"
SECRET_KEY = b"\x8dk\x0fw\xee \x8c2\xdfi\x07\xeaj\xac1."
TINIFY_KEY = "PP5kKs2F5VPQp9sDxWX33SMv2kzjKN4M"

# Log - Config
LOG_LEVEL = "INFO"
LOG_FORMAT = "[{name}] {levelname} {message}"

# SQLAlchemy - Config
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = ""

# CORS - Config
CORS = {
    "/api/.*": {
        "origins": "*",
        "allow_headers": "*"
    }
}

# APISPEC - Config
APISPEC_SWAGGER_URL = "/swagger/"
APISPEC_SWAGGER_UI_URL = None,
APISPEC_TITLE = "Website Pfarre Machstrasse - API"
APISPEC_VERSION = "v1"
APISPEC_OAS_VERSION = "3.0.2",
APISPEC_SERVERS = [
    {
        "url": "https://pfarre-machstrasse.at",
        "description": "Production Server"
    }
]
APISPEC_AUTH = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
}
