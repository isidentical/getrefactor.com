import subprocess

subprocess.check_output(
    [
        "panel",
        "convert",
        "index.py",
        "--to",
        "pyodide-worker",
        "--out",
        "docs",
        "--requirements",
        "refactor==0.6.1",
    ]
)

with open("docs/index.js") as stream:
    source_code = stream.read()

source_code = source_code.replace(
    "json.loads('${msg.patch}')",
    "json.loads(${JSON.stringify(msg.patch)})",
)

with open("docs/index.js", "w") as stream:
    stream.write(source_code)
