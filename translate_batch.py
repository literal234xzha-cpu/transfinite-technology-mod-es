#!/usr/bin/env python3
"""
Traducción en batch - extrae TODOS los textos chinos, los manda de golpe,
y los reinyecta. Mucho más rápido que uno por uno.
"""
import os
import re
import json
import time
from deep_translator import GoogleTranslator

CONTENT_DIR = "content"
SEPARATOR = "\n|||SPLIT|||\n"
BATCH_SIZE = 20  # textos por batch

def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', str(text)))

def translate_batch(texts):
    """Traduce una lista de textos usando translators con múltiples backends"""
    results = []
    for text in texts:
        translated = text
        for backend in ["alibaba", "baidu", "bing"]:
            try:
                import translators as ts
                result = ts.translate_text(text, translator=backend, from_language="zh", to_language="es")
                if result and result.strip() and result != text:
                    translated = result.strip()
                    break
            except Exception as e:
                time.sleep(1)
        results.append(translated)
        time.sleep(0.5)
    return results

# 1. EXTRAER todos los textos chinos de todos los JSONs
print("[1] Extrayendo textos chinos de todos los JSONs...")

all_files = []
for root, dirs, files in os.walk(CONTENT_DIR):
    for fname in files:
        if fname.endswith(".json"):
            all_files.append(os.path.join(root, fname))

# Lista de (filepath, field, original_value, match_start, match_end)
replacements = []
file_contents = {}

FIELD_RE = re.compile(r'("(?:name|description|details)"\s*:\s*)"((?:[^"\\]|\\.)*)"')

for path in all_files:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        file_contents[path] = content

        for m in FIELD_RE.finditer(content):
            val = m.group(2)
            if has_chinese(val):
                replacements.append({
                    "path": path,
                    "prefix": m.group(1),
                    "original": val,
                    "start": m.start(),
                    "end": m.end(),
                    "translated": None
                })
    except:
        pass

total_texts = len(replacements)
print(f"[+] Encontrados {total_texts} textos chinos en {len(all_files)} archivos")

# 2. TRADUCIR en batches
print(f"\n[2] Traduciendo en batches de {BATCH_SIZE}...")

for i in range(0, total_texts, BATCH_SIZE):
    batch = replacements[i:i+BATCH_SIZE]
    texts = [r["original"] for r in batch]
    
    print(f"  Batch {i//BATCH_SIZE + 1}/{(total_texts+BATCH_SIZE-1)//BATCH_SIZE} ({len(texts)} textos)...")
    
    translated = translate_batch(texts)
    time.sleep(1.5)
    
    for j, r in enumerate(batch):
        r["translated"] = translated[j]
        
    print(f"  -> Ej: '{texts[0][:30]}' -> '{translated[0][:30]}'")

# 3. REINYECTAR en los archivos
print(f"\n[3] Reinyectando traducciones en archivos...")

# Agrupar por archivo
from collections import defaultdict
by_file = defaultdict(list)
for r in replacements:
    by_file[r["path"]].append(r)

modified = 0
for path, reps in by_file.items():
    content = file_contents[path]
    
    # Aplicar reemplazos de atrás hacia adelante para no desplazar índices
    reps_sorted = sorted(reps, key=lambda x: x["start"], reverse=True)
    
    for r in reps_sorted:
        if r["translated"] and r["translated"] != r["original"]:
            new_val = r["prefix"] + '"' + r["translated"] + '"'
            content = content[:r["start"]] + new_val + content[r["end"]:]
    
    if content != file_contents[path]:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        modified += 1

print(f"\n=== COMPLETADO ===")
print(f"Archivos modificados: {modified}")
print(f"Textos traducidos: {total_texts}")
