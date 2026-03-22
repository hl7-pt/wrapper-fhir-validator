# wrapper-fhir-validator

A Flask-based web application that wraps the [HL7 FHIR Validator](https://confluence.hl7.org/display/FHIR/Using+the+FHIR+Validator) (`validator_cli.jar`). It provides a web UI and a REST API to validate FHIR resources against Implementation Guides (IGs).

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Systemd Service (Production)](#systemd-service-production)

---

## Overview

The wrapper provides two main features:

1. **FHIR Resource Validation** – Submit a FHIR resource (JSON) together with an Implementation Guide (`.tgz` package or URL) through the web UI or the API. The application invokes the FHIR Validator JAR and returns the validation results (errors, warnings, and informational messages) colour-coded by severity.

2. **IG Upload** – Push the resources from an Implementation Guide into a FHIR server via REST.

---

## Project Structure

```
wrapper-fhir-validator/
├── validator_app/               # Main Flask application package
│   ├── __init__.py              # App factory, Swagger/Flasgger configuration
│   ├── views.py                 # Route handlers and validation logic
│   ├── templates/
│   │   └── index.html           # Web UI
│   ├── static/
│   │   └── css/
│   │       └── main.css         # Application stylesheet
│   └── docs/
│       └── upload-ig.yml        # OpenAPI/Swagger spec for the upload-ig endpoint
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── setup.sh                     # Helper script: create venv, install deps, start app
├── fhir-validator.service       # Systemd unit file for production deployment
├── LICENSE
└── README.md
```

### Key files

| File | Purpose |
|------|---------|
| `run.py` | Configures rotating-file logging and starts the Flask development server on port **5005**. |
| `validator_app/__init__.py` | Creates the Flask application instance and registers Flasgger (Swagger UI). |
| `validator_app/views.py` | Defines two routes (`/fhir-validator/` and `/fhir-validator/upload-ig`) and calls the FHIR Validator JAR via `subprocess`. |
| `fhir-validator.service` | Systemd unit that runs the app under Gunicorn in production (port **5006**). |
| `setup.sh` | One-shot script to bootstrap a virtual environment, install dependencies, and launch the application. |

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.9 or later |
| Java | 11 or later (required to run `validator_cli.jar`) |
| `validator_cli.jar` | Download from [https://github.com/hapifhir/org.hl7.fhir.core/releases/latest](https://github.com/hapifhir/org.hl7.fhir.core/releases/latest) |

---

## Installation

The `setup.sh` script automates the setup process:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/hl7-pt/wrapper-fhir-validator.git
cd wrapper-fhir-validator

# Make the script executable and run it
chmod +x setup.sh
./setup.sh
```

The script will:

1. Create a Python virtual environment (`venv/`) inside the project directory.
2. Install all Python dependencies from `requirements.txt`.
3. Create the `tmp/` and `logs/` directories used at runtime.
4. Print instructions for downloading `validator_cli.jar`.
5. Start the Flask development server (port **5005**).

---

## Configuration

The following paths are currently **hardcoded** in `validator_app/views.py` and must be updated before running the application:

| Variable | Default value | Description |
|----------|---------------|-------------|
| `jar_path` | `<APP_DIR>/validator_cli.jar` | Absolute path to the FHIR Validator JAR |
| `temp_dir` | `<APP_DIR>/tmp` | Directory used to store temporary files during validation |

Replace `<APP_DIR>` with the absolute path to your project directory and update both values in `validator_app/views.py` before running the application.

---

## Running the Application

### Development

```bash
# Activate the virtual environment
source venv/bin/activate

# Start the development server
python run.py
```

The application will be available at `http://localhost:5005/fhir-validator/`.

### Production (Gunicorn)

```bash
source venv/bin/activate
gunicorn --workers 2 --bind 0.0.0.0:5006 run:app
```

The application will be available at `http://<server>:5006/fhir-validator/`.

---

## API Endpoints

### Web UI

| Method | Path | Description |
|--------|------|-------------|
| `GET` / `POST` | `/fhir-validator/` | Validation form – submit a FHIR resource and an IG package |

### REST API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/fhir-validator/upload-ig` | Upload an Implementation Guide to a FHIR server |

#### `POST /fhir-validator/upload-ig` – request body (JSON)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `serverBase` | string | ✅ | Base URL of the target FHIR server |
| `packageId` | string | ☐ | FHIR package identifier (e.g. `hl7.fhir.r4.core#4.0.1`) |
| `packagebase64` | string | ☐ | Base64-encoded `.tgz` package |
| `packageURL` | string | ☐ | URL of the `.tgz` package |
| `usePUT` | boolean | ☐ | Use `PUT` instead of `POST` when uploading resources (default: `true`) |
| `loadRecursively` | boolean | ☐ | Also load dependent IGs (default: `false`) |

> Only **one** of `packageId`, `packagebase64`, or `packageURL` may be provided at a time.

### Swagger / OpenAPI

Interactive API documentation is available at `/apidocs/` after starting the application.

---

## Systemd Service (Production)

A ready-to-use systemd unit file is provided at `fhir-validator.service`. Follow the steps below to install it:

```bash
# 1. Edit the service file and replace the placeholder values
#    APP_USER  – the OS user that will run the service
#    APP_GROUP – the OS group (e.g. www-data)
#    APP_DIR   – absolute path to the project directory (e.g. /opt/wrapper-fhir-validator)

# 2. Copy the unit file to the systemd directory
sudo cp fhir-validator.service /etc/systemd/system/

# 3. Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable fhir-validator

# 4. Start the service
sudo systemctl start fhir-validator

# 5. Check its status
sudo systemctl status fhir-validator
```

Logs from the application are written to `logs/ig-uploader.log` (rotating, max 10 MB per file, 10 backups).
