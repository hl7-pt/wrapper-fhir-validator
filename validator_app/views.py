#!/usr/bin/python

from flask import render_template, request, Blueprint
from validator_app import app
import subprocess
import os
import tempfile
import json

print(app.config)
bp = Blueprint("burritos", __name__)

temp_dir = tempfile.gettempdir()
temp_dir = "/Users/joaoalmeida/Desktop/hl7pt/wrapper-fhir-validator/tmp"


def validating_resource(file, ig, temp_folder):
    jar_path = (
        "/Users/joaoalmeida/Desktop/hl7pt/wrapper-fhir-validator/validator_cli.jar"
    )
    if not os.path.isfile(jar_path):
        print(f"Error: The specified jar file does not exist at {jar_path}")
        return ""
    ##java -jar validator_cli\ \(1\).jar /Users/joaoalmeida/Desktop/hl7pt/adr-ig/fsh-generated/resources/AdverseEvent-AdverseEvent-1.json -ig package\ \(2\).tgz
    command = [
        "java",
        "-jar",
        jar_path,
        file,
        "-ig",
        ig,
        "-output",
        temp_folder + "/output.json",
        "-output-style",
        "json",
    ]
    print(command)
    try:
        # Run the command and capture the output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Output:\n", result.stdout)
        print("Errors:\n", result.stderr)
        return {"result": "Success", "file": temp_folder + "/output.json"}
    except subprocess.CalledProcessError as e:
        print("ERRRRROR")
        return {"result": "Success", "file": temp_folder + "/output.json"}


@bp.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        # Get JSON data from textarea
        json_data = request.form.get("serverBase")

        # Save JSON data to a temp file
        json_file_path = os.path.join(temp_dir, "uploaded_data.json")
        with open(json_file_path, "w") as json_file:
            json_file.write(json_data)

        # Get uploaded .tgz file
        uploaded_file = request.files.get("tgzFile")
        print(uploaded_file)
        if uploaded_file and uploaded_file.filename.endswith(".tgz"):
            tgz_file_path = os.path.join(temp_dir, uploaded_file.filename)
            uploaded_file.save(tgz_file_path)
        print(json_file_path, tgz_file_path)
        outcome = validating_resource(json_file_path, tgz_file_path, temp_dir)
        file = outcome["file"]
        with open(file, "r", encoding="utf-8") as file:
            result = json.load(file)
        return render_template("index.html", result=result)

    else:
        return render_template("index.html")


# https://github.com/jkiddo/ember
@bp.route("/upload-ig", methods=["POST"])
def upig():
    """
    file: docs/upload-ig.yml
    """
    data = request.json
    print(data)
    serverBase = data["serverBase"]
    packageId = data.get("packageId", None)
    usePUT = data.get("usePUT", True)
    loadRecursively = data.get("loadRecursively", False)
    packagebase64 = data.get("packagebase64", None)
    packageURL = data.get("packageURL", None)
    print([packageId is not None, packagebase64 is not None, packageURL is not None])
    if (
        sum([packageId is not None, packagebase64 is not None, packageURL is not None])
        > 1
    ):
        return (
            "Only 1 of Package ID OR package base64 OR package URL must be provided. Not more than 1.",
            404,
        )
    if not serverBase:
        return "Server base must be provided.", 404

    return None


app.register_blueprint(bp, url_prefix="/fhir-validator")
