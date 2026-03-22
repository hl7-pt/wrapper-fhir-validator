#!/usr/bin/env bash
# setup.sh – Bootstrap the wrapper-fhir-validator environment and start the app.
#
# Usage:
#   chmod +x setup.sh
#   ./setup.sh
#
# What this script does:
#   1. Checks that Python 3 and Java are available.
#   2. Creates a Python virtual environment in ./venv (if it does not exist).
#   3. Installs Python dependencies from requirements.txt.
#   4. Creates the tmp/ and logs/ runtime directories.
#   5. Reminds you to download validator_cli.jar if it is missing.
#   6. Starts the Flask development server (http://0.0.0.0:5005).
#
# For production use, run Gunicorn directly or install the systemd service
# (see fhir-validator.service and the README).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
JAR_FILE="${SCRIPT_DIR}/validator_cli.jar"
JAR_DOWNLOAD_URL="https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar"

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

log()  { echo "[setup] $*"; }
warn() { echo "[setup] WARNING: $*" >&2; }
die()  { echo "[setup] ERROR: $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# 1. Verify prerequisites
# ---------------------------------------------------------------------------

log "Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
    die "Python 3 is not installed or not on PATH. Please install Python 3.9 or later."
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
log "Found Python ${PYTHON_VERSION}"

if ! command -v java &>/dev/null; then
    warn "Java is not installed or not on PATH."
    warn "Java 11 or later is required to run validator_cli.jar."
    warn "Please install a JDK before validating FHIR resources."
fi

# ---------------------------------------------------------------------------
# 2. Create virtual environment
# ---------------------------------------------------------------------------

if [ ! -d "${VENV_DIR}" ]; then
    log "Creating virtual environment at ${VENV_DIR} ..."
    python3 -m venv "${VENV_DIR}"
else
    log "Virtual environment already exists at ${VENV_DIR}, skipping creation."
fi

# Activate the virtual environment
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
log "Virtual environment activated."

# ---------------------------------------------------------------------------
# 3. Install dependencies
# ---------------------------------------------------------------------------

log "Installing Python dependencies from requirements.txt ..."
pip install --upgrade pip --quiet
pip install -r "${SCRIPT_DIR}/requirements.txt" --quiet
log "Dependencies installed."

# ---------------------------------------------------------------------------
# 4. Create runtime directories
# ---------------------------------------------------------------------------

for dir in tmp logs; do
    if [ ! -d "${SCRIPT_DIR}/${dir}" ]; then
        mkdir -p "${SCRIPT_DIR}/${dir}"
        log "Created directory: ${dir}/"
    fi
done

# ---------------------------------------------------------------------------
# 5. Check for validator_cli.jar
# ---------------------------------------------------------------------------

if [ ! -f "${JAR_FILE}" ]; then
    warn "validator_cli.jar not found at ${JAR_FILE}"
    warn "Download it with:"
    warn "  curl -L -o '${JAR_FILE}' '${JAR_DOWNLOAD_URL}'"
    warn "The application will start but resource validation will not work until the JAR is present."
fi

# ---------------------------------------------------------------------------
# 6. Start the Flask development server
# ---------------------------------------------------------------------------

log "Starting Flask development server on http://0.0.0.0:5005 ..."
log "Press Ctrl+C to stop."
log ""

cd "${SCRIPT_DIR}"
python run.py
