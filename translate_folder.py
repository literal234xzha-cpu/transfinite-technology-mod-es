#!/usr/bin/env python3
"""
Traduce "name", "description", "details" en JSONs de una carpeta específica.
Uso: python3 translate_folder.py <carpeta> <logfile>
"""
import os
import re
import sys
import time
import translators as ts

FOLDER = sys.argv[1]
LOGFILE = sys.argv[2] if len(sys.argv) > 2 else "translate_folder.log"

BACKENDS = ["alibaba", "baidu", "bing"]
translated = 0
skipped = 0

def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', str(text)))

def translate(text):
    if not text or not has_chinese(text):
        return text
    for backend in BACKENDS:
        for attempt in range(2):
            try:
                result = ts.translate_text(text, translator=backend, from_language="zh", to_language="es")
                if result and result.strip():
                    return result.strip()
            except Exception as e:
                time.sleep(1.5)
    return text

def process_file(path):
    global translated, skipped
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Skip si ya tiene español
        if re.search(r'[áéíóúñü]', content):
            return False

        original = content

        for field in ['"name"', '"description"', '"details"']:
            pattern = re.compile(r'(' + re.escape(field) + r'\s*:\s*)"((?:[^"\\]|\\.)*)"')
            def replacer(m, f=field):
                global translated, skipped
                val = m.group(2)
                if has_chinese(val):
                    es = translate(val)
                    time.sleep(0.8)
                    if es != val:
                        translated += 1
                        return m.group(1) + '"' + es + '"'
                skipped += 1
                return m.group(0)
            content = pattern.sub(replacer, content)

        if content != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        log(f"ERROR {path}: {e}")
        return False

log_f = open(LOGFILE, "w", encoding="utf-8")
def log(msg):
    print(msg)
    log_f.write(msg + "\n")
    log_f.flush()

all_json = []
for root, dirs, files in os.walk(FOLDER):
    for fname in files:
        if fname.endswith(".json"):
            all_json.append(os.path.join(root, fname))

total = len(all_json)
log(f"[*] {FOLDER}: {total} archivos")

for i, path in enumerate(all_json):
    log(f"[{i+1}/{total}] {path}")
    process_file(path)

log(f"=== DONE {FOLDER} === traducidos:{translated} saltados:{skipped}")
log_f.close()
