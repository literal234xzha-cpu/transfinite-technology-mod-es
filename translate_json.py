#!/usr/bin/env python3
"""
Traduce "name" y "description" en todos los JSONs de content/
Solo toca los valores que contienen chino.
Modifica los archivos in-place.
"""
import os
import re
import time
import translators as ts

CONTENT_DIR = "content"
BACKENDS = ["alibaba", "baidu", "bing"]
translated = 0
skipped = 0
errors = 0

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
    global translated, skipped, errors
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        original = content
        changed = False

        # Traducir "name": "..."
        def replace_name(m):
            global translated, skipped
            prefix = m.group(1)
            value = m.group(2)
            if has_chinese(value):
                es = translate(value)
                time.sleep(1.0)
                translated += 1
                return f'{prefix}"{es}"'
            skipped += 1
            return m.group(0)

        # Traducir "description": "..."
        def replace_desc(m):
            global translated, skipped
            prefix = m.group(1)
            value = m.group(2)
            if has_chinese(value):
                es = translate(value)
                time.sleep(1.0)
                translated += 1
                return f'{prefix}"{es}"'
            skipped += 1
            return m.group(0)

        content = re.sub(
            r'("name"\s*:\s*)"((?:[^"\\]|\\.)*)"',
            lambda m: replace_name(type('', (), {
                'group': lambda self, n: [m.group(0), m.group(1), m.group(2)][n]
            })()),
            content
        )
        content = re.sub(
            r'("description"\s*:\s*)"((?:[^"\\]|\\.)*)"',
            lambda m: replace_desc(type('', (), {
                'group': lambda self, n: [m.group(0), m.group(1), m.group(2)][n]
            })()),
            content
        )

        if content != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        errors += 1
        print(f"  ERROR {path}: {e}")
        return False

# Reemplazar con regex directo más simple
def process_file_v2(path):
    global translated, skipped, errors
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        original = content

        for field in ['"name"', '"description"', '"details"']:
            pattern = re.compile(
                r'(' + re.escape(field) + r'\s*:\s*)"((?:[^"\\]|\\.)*)"'
            )
            def replacer(m, f=field):
                global translated, skipped
                val = m.group(2)
                if has_chinese(val):
                    es = translate(val)
                    time.sleep(0.9)
                    if es != val:
                        translated += 1
                        print(f"  [{f}] {val[:40]} -> {es[:40]}")
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
        errors += 1
        print(f"  ERROR {path}: {e}")
        return False

# Encontrar todos los JSON
all_json = []
for root, dirs, files in os.walk(CONTENT_DIR):
    for fname in files:
        if fname.endswith(".json"):
            all_json.append(os.path.join(root, fname))

total = len(all_json)
print(f"[*] Total archivos JSON: {total}")

for i, path in enumerate(all_json):
    # Saltar archivos ya traducidos (tienen texto en español)
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if re.search(r'[áéíóúñü]', content):
            print(f"[{i+1}/{total}] SKIP (ya traducido): {path}")
            continue
    except:
        pass
    print(f"\n[{i+1}/{total}] {path}")
    process_file_v2(path)

print(f"\n=== COMPLETADO ===")
print(f"Campos traducidos: {translated}")
print(f"Saltados (sin chino): {skipped}")
print(f"Errores: {errors}")
