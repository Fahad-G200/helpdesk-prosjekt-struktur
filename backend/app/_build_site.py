from pathlib import Path
import markdown

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
  <header><h1>{title}</h1><p><a href="index.html" style="color:white">← Tilbake til forsiden</a></p></header>
  <main><article>{content}</article></main>
</body>
</html>
"""

for md_file in DOCS.glob("*.md"):
    text = md_file.read_text(encoding="utf-8")
    html = markdown.markdown(text, extensions=["tables", "fenced_code"])
    title = md_file.stem.replace("-", " ").replace("_", " ").title()
    out_file = OUT / f"{md_file.stem}.html"
    out_file.write_text(TEMPLATE.format(title=title, content=html), encoding="utf-8")
    print("Bygget:", out_file)

# Kopier forsiden til site/
index_src = DOCS / "index.html"
if index_src.exists():
    (OUT / "index.html").write_text(index_src.read_text(encoding="utf-8"), encoding="utf-8")
    print("Kopierte index.html til site/")