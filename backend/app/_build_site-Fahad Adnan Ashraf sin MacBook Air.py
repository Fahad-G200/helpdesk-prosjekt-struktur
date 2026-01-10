from pathlib import Path
import markdown
import shutil

DOCS = Path("docs")
OUT = Path("site")
OUT.mkdir(exist_ok=True)

TEMPLATE = """<!doctype html>
<html lang="no">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <style>
    body{{font-family:system-ui,Arial;margin:0;background:#f7f9fc;color:#222}}
    header{{background:#2c3e50;color:#fff;padding:18px}}
    main{{max-width:900px;margin:0 auto;padding:18px}}
    article{{background:#fff;border-radius:10px;padding:16px;box-shadow:0 2px 6px rgba(0,0,0,.08)}}
    a{{color:#2c3e50}}
  </style>
</head>
<body>
  <header><h1>{title}</h1><p><a href="index.html" style="color:white">← Tilbake</a></p></header>
  <main><article>{content}</article></main>
</body>
</html>
"""

# Tøm site/ så du alltid får en ren build
for p in OUT.glob("*"):
    if p.is_file():
        p.unlink()
    else:
        shutil.rmtree(p)

# Kopier index.html (din forside)
index_src = DOCS / "index.html"
if index_src.exists():
    shutil.copy2(index_src, OUT / "index.html")

# Konverter alle .md til .html
for md_file in DOCS.glob("*.md"):
    text = md_file.read_text(encoding="utf-8")
    html = markdown.markdown(text, extensions=["tables", "fenced_code"])
    title = md_file.stem.replace("-", " ").replace("_", " ").title()
    (OUT / f"{md_file.stem}.html").write_text(
        TEMPLATE.format(title=title, content=html),
        encoding="utf-8"
    )
    print("Bygget:", OUT / f"{md_file.stem}.html")

print("Ferdig. Åpne site/index.html eller bygg Docker på nytt.")