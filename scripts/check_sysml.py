"""Validate the SysML v2 models and render their diagrams.

Runs inside the solent-usv-sysml image (official OMG pilot implementation as a Jupyter kernel):
    docker run --rm -v "$PWD":/ws solent-usv-sysml python scripts/check_sysml.py
Exits with 1 if the kernel reports any error, so it can run in CI.
"""
import pathlib
import subprocess
import sys

from jupyter_client.manager import start_new_kernel

MODELS = pathlib.Path("docs/sysml")
DIAGRAMS = MODELS / "diagrams"
# (file name, %viz command) for each diagram I keep in the README, by Arcadia level.
VIEWS = [
    ("1_operational_context", "%viz --view=Tree OperationalAnalysis::solent"),
    ("2_system_context", "%viz --view=Interconnection SystemAnalysis::SolentContext"),
    ("2_system_requirements", "%viz --view=Tree SystemAnalysis::systemRequirements"),
    ("3_logical_architecture", "%viz --view=Interconnection LogicalArchitecture::LogicalUSV"),
    ("3_operating_mode", "%viz --view=State LogicalArchitecture::OperatingMode"),
    ("4_physical_architecture", "%viz --view=Interconnection PhysicalArchitecture::PhysicalUSV"),
]


def run(client, code):
    """Execute code in the kernel and return (text output, svg images, error flag)."""
    msg_id = client.execute(code)
    texts, svgs, failed = [], [], False
    while True:
        msg = client.get_iopub_msg(timeout=300)
        if msg["parent_header"].get("msg_id") != msg_id:
            continue
        kind, content = msg["msg_type"], msg["content"]
        if kind == "stream":
            texts.append(content["text"])
            failed |= "ERROR" in content["text"]
        elif kind in ("display_data", "execute_result"):
            data = content["data"]
            if "image/svg+xml" in data:
                svgs.append(data["image/svg+xml"])
            elif "text/plain" in data:
                texts.append(data["text/plain"])
        elif kind == "error":
            texts.append("\n".join(content["traceback"]))
            failed = True
        elif kind == "status" and content["execution_state"] == "idle":
            return "".join(texts), svgs, failed


def main():
    manager, client = start_new_kernel(kernel_name="sysml", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # hide the kernel's Java logs
    ok = True
    try:
        for model in sorted(MODELS.glob("*.sysml")):
            text, _, failed = run(client, model.read_text())
            print(f"--- {model}\n{text}")
            ok &= not failed
        if ok:
            DIAGRAMS.mkdir(exist_ok=True)
            for name, command in VIEWS:
                text, svgs, failed = run(client, command)
                if failed or not svgs:
                    print(f"--- {name}: no diagram\n{text}")
                    ok = False
                    continue
                (DIAGRAMS / f"{name}.svg").write_text(svgs[0])
                print(f"--- {name}: {DIAGRAMS / name}.svg")
    finally:
        client.stop_channels()
        manager.shutdown_kernel()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
