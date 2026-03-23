import subprocess
SECRET = "demo"

def run(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True).decode()
