#!/usr/bin/env python3
"""
Traduce bundle_zh_CN.properties de chino a español
Genera bundle_es.properties
Usa translators lib con múltiples backends
"""
import re
import time
import translators as ts

INPUT  = "bundles/bundle_zh_CN.properties"
OUTPUT = "bundles/bundle_es.properties"

BACKENDS = ["alibaba", "baidu", "bing", "google"]

def translate(text, retries=3):
    if not text.strip():
        return text
    for backend in BACKENDS:
        for attempt in range(retries):
            try:
                result = ts.translate_text(text, translator=backend, from_language="zh", to_language="es")
                if result and result.strip():
                    return result.strip()
            except Exception as e:
                print(f"  [!] {backend} error: {e}")
                time.sleep(2)
    return text  # fallback: devolver original

PROP_RE = re.compile(r'^([^#=\s][^=]*)=(.*)$')

lines_in  = open(INPUT, encoding="utf-8").readlines()
out_lines = []
total     = len(lines_in)
translated_count = 0
skipped_count = 0

for i, line in enumerate(lines_in):
    raw = line.rstrip("\n")

    if raw.strip() == "" or raw.strip().startswith("#"):
        out_lines.append(raw)
        continue

    m = PROP_RE.match(raw)
    if not m:
        out_lines.append(raw)
        continue

    key   = m.group(1).rstrip()
    value = m.group(2).strip()

    if not value:
        out_lines.append(raw)
        continue

    # Preservar tags de color de Mindustry: [red], [blue], [#rrggbb], etc.
    tags   = re.findall(r'\[[^\]]*\]', value)
    ph_val = value
    for idx, tag in enumerate(tags):
        ph_val = ph_val.replace(tag, f"<<T{idx}>>", 1)

    # Solo traducir si hay texto chino real
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', ph_val))
    if not has_chinese:
        out_lines.append(raw)
        skipped_count += 1
        continue

    translated = translate(ph_val)
    time.sleep(1.2)

    # Restaurar tags
    for idx, tag in enumerate(tags):
        translated = translated.replace(f"<<T{idx}>>", tag)
        translated = translated.replace(f"<< T{idx} >>", tag)
        translated = translated.replace(f"<<t{idx}>>", tag)

    new_line = f"{key}={translated}"
    out_lines.append(new_line)
    translated_count += 1

    print(f"[{i+1}/{total}] {key}")
    print(f"   ZH: {value[:80]}")
    print(f"   ES: {translated[:80]}")

# Escribir output
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines) + "\n")

print(f"\n✓ Traducción completada → {OUTPUT}")
print(f"  Traducidas: {translated_count}")
print(f"  Saltadas (sin chino): {skipped_count}")
