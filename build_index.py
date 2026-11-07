import os
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
CONTEXT = BASE / "context"
NOTAS = CONTEXT / "Notas"
MESES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}

def build_index():
    hoy = datetime.now()
    mes = MESES[hoy.month]
    mes_folder = NOTAS / mes
    mes_folder.mkdir(parents=True, exist_ok=True)
    
    index_file = mes_folder / f"INDEX_{mes}.md"
    
    lines = [f"# Índice — {mes} {hoy.year}\n"]
    
    # Chats
    chats = sorted(CONTEXT.glob("chat_*.md"), key=lambda x: x.stat().st_mtime)
    chats = [c for c in chats if c.stat().st_size > 0]
    if chats:
        lines.append(f"\n## Chats ({len(chats)})\n")
        for c in chats:
            size = c.stat().st_size // 1024
            fecha = c.stem.replace("chat_", "").replace("_", " ")
            lines.append(f"- `{c.name}` — {size} KB — {fecha}")
    
    # Resúmenes diarios
    resumenes = sorted(mes_folder.glob("resumen_*.md"))
    if resumenes:
        lines.append(f"\n## Resúmenes diarios ({len(resumenes)})\n")
        for r in resumenes:
            lines.append(f"- `{r.name}`")
    
    # Notas sueltas
    notas = sorted(mes_folder.glob("*.txt")) + sorted(mes_folder.glob("*.md"))
    notas = [n for n in notas if n.name != index_file.name and not n.name.startswith("resumen_") and n.name != "INDEX_Octubre.md"]
    if notas:
        lines.append(f"\n## Notas sueltas ({len(notas)})\n")
        for n in notas:
            size = n.stat().st_size // 1024
            lines.append(f"- `{n.name}` — {size} KB")
    
    index_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Índice guardado: {index_file}")
    print(f"   Chats: {len(chats)} | Resúmenes: {len(resumenes)} | Notas: {len(notas)}")

if __name__ == "__main__":
    build_index()
