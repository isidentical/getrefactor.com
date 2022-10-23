import subprocess

subprocess.check_output(
    [
        "panel",
        "convert",
        "index.py",
        "--to",
        "pyodide-worker",
        "--out",
        "build",
        "--requirements",
        "refactor==0.6.0",
    ]
)

with open("build/index.js") as stream:
    source_code = stream.read()

source_code = source_code.replace(
    "json.loads('${msg.patch}')",
    "json.loads(${JSON.stringify(msg.patch)})",
)

with open("build/index.js", "w") as stream:
    stream.write(source_code)
