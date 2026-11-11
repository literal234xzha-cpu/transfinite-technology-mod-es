#!/usr/bin/env python3
"""
Traducción final - simple y directo con deep_translator + Google
Solo archivos que aún tienen chino
"""
import os
import re
import time
from deep_translator import MyMemoryTranslator

CONTENT_DIR = "content"
translator = MyMemoryTranslator(source="zh-CN", target="es-ES")

def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', str(text)))

def translate(text):
    if not text or not has_chinese(text):
        return text
    for attempt in range(4):
        try:
            result = translator.translate(text[:500])  # límite MyMemory
            if result and result.strip():
                return result.strip()
        except Exception as e:
            wait = (attempt + 1) * 2
            print(f"    retry {attempt+1} ({wait}s): {e}")
            time.sleep(wait)
    return text

FIELD_RE = re.compile(r'("(?:name|description|details)"\s*:\s*)"((?:[^"\\]|\\.)*)"')

all_files = []
for root, dirs, files in os.walk(CONTENT_DIR):
    for fname in files:
        if fname.endswith(".json"):
            all_files.append(os.path.join(root, fname))

total = len(all_files)
translated_count = 0
files_modified = 0

print(f"[*] {total} archivos JSON encontrados")

for i, path in enumerate(all_files):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Skip si no tiene chino
        if not has_chinese(content):
            continue

        original = content
        file_changed = False

        for m in reversed(list(FIELD_RE.finditer(content))):
            val = m.group(2)
            if has_chinese(val):
                es = translate(val)
                time.sleep(0.5)
                if es != val:
                    new = m.group(1) + '"' + es + '"'
                    content = content[:m.start()] + new + content[m.end():]
                    translated_count += 1
                    file_changed = True
                    print(f"[{i+1}/{total}] {os.path.basename(path)}")
                    print(f"  ZH: {val[:60]}")
                    print(f"  ES: {es[:60]}")

        if file_changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            files_modified += 1

    except Exception as e:
        print(f"ERROR {path}: {e}")

print(f"\n=== COMPLETADO ===")
print(f"Campos traducidos: {translated_count}")
print(f"Archivos modificados: {files_modified}")
