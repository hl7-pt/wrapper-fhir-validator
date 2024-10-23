"""Flask app for starting server."""

from flask import Flask
from flasgger import Swagger


app = Flask(__name__)

app.config["SWAGGER"] = {
    "swagger": "2.0",
    "info": {
        "title": "IG validator",
        "description": "IG Validator API",
        "contact": {
            "responsibleOrganization": "IG Validator",
            "responsibleDeveloper": "Joao Almeida",
        },
        "termsOfService": "http://me.com/terms",
        "version": "0.0.1",
    },
    "url_prefix": "/ig-uploader-api",
    "basePath": "api",  # base bash for blueprint registration
    "schemes": ["http", "https"],
}

swagger = Swagger(app, template=app.config["SWAGGER"])


import validator_app.views
