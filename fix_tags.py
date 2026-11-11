#!/usr/bin/env python3
"""
Post-proceso: restaurar tags de Mindustry que quedaron HTML-escapados
y limpiar artefactos de traducción
"""
import re

SOURCE_ZH = "bundles/bundle_zh_CN.properties"
OUTPUT_ES  = "bundles/bundle_es.properties"

PROP_RE = re.compile(r'^([^#=\s][^=]*)=(.*)$')

# Leer el archivo chino original para recuperar los tags
zh_tags = {}
for line in open(SOURCE_ZH, encoding="utf-8"):
    raw = line.rstrip("\n")
    m = PROP_RE.match(raw)
    if not m:
        continue
    key   = m.group(1).rstrip()
    value = m.group(2).strip()
    tags  = re.findall(r'\[[^\]]*\]', value)
    if tags:
        zh_tags[key] = tags

# Leer el archivo ES y reparar
lines_es = open(OUTPUT_ES, encoding="utf-8").readlines()
out = []

for line in lines_es:
    raw = line.rstrip("\n")
    m = PROP_RE.match(raw)
    if not m:
        out.append(raw)
        continue

    key   = m.group(1).rstrip()
    value = m.group(2)

    tags = zh_tags.get(key, [])

    # Reemplazar HTML-escapes de los placeholders: &lt;&lt;T0&gt;&gt; → tag real
    def restore_tag(match):
        idx_str = match.group(1)
        try:
            idx = int(idx_str)
            if idx < len(tags):
                return tags[idx]
        except:
            pass
        return match.group(0)

    # Patrones de placeholder escapado por los backends
    value = re.sub(r'&lt;&lt;T(\d+)&gt;&gt;', restore_tag, value)
    value = re.sub(r'<<T(\d+)>>', restore_tag, value)
    value = re.sub(r'<< T(\d+) >>', restore_tag, value)
    value = re.sub(r'&lt;&lt; T(\d+) &gt;&gt;', restore_tag, value)

    # Limpiar artefactos comunes de traducción
    value = value.replace("\\ N", "\\n").replace("\\ n", "\\n")
    value = value.replace("\\N ", "\\n").replace(" \\n", "\\n")

    out.append(f"{key}={value}")

with open(OUTPUT_ES, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

print("✓ Tags reparados en bundle_es.properties")

# Mostrar muestra de resultado final
print("\n=== MUESTRA FINAL ===")
count = 0
for line in open(OUTPUT_ES, encoding="utf-8"):
    raw = line.strip()
    m = PROP_RE.match(raw)
    if m and re.search(r'[a-záéíóúñü]', m.group(2), re.IGNORECASE):
        print(f"  {raw[:100]}")
        count += 1
        if count >= 20:
            break
