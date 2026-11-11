#!/usr/bin/env python3
"""
Traduce bundle_zh_CN.properties de chino a español
Genera bundle_es.properties
"""
import re
import time
from deep_translator import GoogleTranslator

INPUT  = "bundles/bundle_zh_CN.properties"
OUTPUT = "bundles/bundle_es.properties"

translator = GoogleTranslator(source="zh-CN", target="es")

def translate(text):
    if not text.strip():
        return text
    try:
        result = translator.translate(text)
        return result if result else text
    except Exception as e:
        print(f"  [!] Error traduciendo '{text[:40]}': {e}")
        return text

# Regex para detectar línea de propiedad: clave = valor
PROP_RE = re.compile(r'^([^#=\s][^=]*)=(.*)$')

lines_in  = open(INPUT,  encoding="utf-8").readlines()
out_lines = []
total     = len(lines_in)

for i, line in enumerate(lines_in):
    raw = line.rstrip("\n")

    # Línea vacía o comentario → pasar tal cual
    if raw.strip() == "" or raw.strip().startswith("#"):
        out_lines.append(raw)
        continue

    m = PROP_RE.match(raw)
    if not m:
        out_lines.append(raw)
        continue

    key   = m.group(1)          # e.g.  block.foo.name
    value = m.group(2).strip()  # e.g.  泽塔议会

    if not value:
        out_lines.append(raw)
        continue

    # Preservar tags de color de Mindustry: [red], [blue], [#rrggbb]
    # y formato [+], [stat], etc. — los extraemos, traducimos el resto
    # Estrategia: reemplazar tags con placeholders, traducir, restaurar
    tags   = re.findall(r'\[[^\]]*\]', value)
    ph_val = re.sub(r'\[[^\]]*\]', lambda m2: f"__TAG{tags.index(m2.group())}__", value)

    translated = translate(ph_val)
    time.sleep(0.3)   # respetar rate-limit de Google

    # Restaurar tags
    for idx, tag in enumerate(tags):
        translated = translated.replace(f"__TAG{idx}__", tag)
        translated = translated.replace(f"__tag{idx}__", tag)
        translated = translated.replace(f"__ TAG{idx} __", tag)

    new_line = f"{key}={translated}"
    out_lines.append(new_line)
    print(f"[{i+1}/{total}] {key}")
    print(f"   ZH: {value}")
    print(f"   ES: {translated}")

# Escribir output
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines) + "\n")

print(f"\n✓ Traducción completada → {OUTPUT}")
print(f"  Líneas procesadas: {total}")
