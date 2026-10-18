#!/usr/bin/env python3
"""Skill paketini denetler.

    python3 scripts/dogrula.py            # paket denetimi; kurulum varsa onu da denetler
    python3 scripts/dogrula.py --kurulum  # kurulum yapılmamışsa hata ver

Denetlenenler:
  1. SKILL.md ön bilgisi (name, description) Claude Code skill kurallarına uygun mu?
  2. SKILL.md'nin andığı her references/ dosyası var mı? (kurulumla gelenler kurulum varsa)
  3. Kurulum yapılmışsa: dizin ve kısaltma dosyaları beklenen büyüklükte mi, örnek sorgular doğru mu?
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(KOK, "references")

# Depoda izlenen (kurulumdan bağımsız) referanslar
IZLENEN = {
    "references/ek-sik-yapilan-hatalar-vikipedi.md",
    "references/resmi-yazisma/yonetmelik-2646.md",
    "references/resmi-yazisma/ozet.md",
    "references/tez/marmara-sbe.md",
    "references/tez/marmara-ebe.md",
}
# Kurulumla gelmesi beklenmeyen, yalnızca yerelde bulunabilecek dosyalar
ISTEGE_BAGLI = {"references/ek-2023-degisiklikleri-ogretmen-derlemesi.md"}


def on_bilgi(metin: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", metin, re.S)
    if not m:
        return {}
    alanlar = {}
    for satir in m.group(1).splitlines():
        if ":" in satir and not satir.startswith(" "):
            anahtar, deger = satir.split(":", 1)
            alanlar[anahtar.strip()] = deger.strip()
    return alanlar


def main(argv: list[str] | None = None) -> int:
    ayr = argparse.ArgumentParser()
    ayr.add_argument("--kurulum", action="store_true", help="kurulum yapılmamışsa hata ver")
    secenek = ayr.parse_args(argv)
    hatalar: list[str] = []
    notlar: list[str] = []

    with open(os.path.join(KOK, "SKILL.md"), encoding="utf-8") as f:
        skill = f.read()
    alan = on_bilgi(skill)
    ad = alan.get("name", "")
    aciklama = alan.get("description", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", ad) or len(ad) > 64:
        hatalar.append(f"SKILL.md name geçersiz: {ad!r}")
    if not aciklama:
        hatalar.append("SKILL.md description boş")
    elif len(aciklama) > 1024:
        hatalar.append(f"SKILL.md description {len(aciklama)} karakter; sınır 1024")
    if re.search(r"[<>]", aciklama):
        hatalar.append("SKILL.md description içinde < veya > olmamalı")

    kurulum_var = os.path.exists(os.path.join(REF, "KURULUM.json"))
    if secenek.kurulum and not kurulum_var:
        hatalar.append("Kurulum yok: önce python3 scripts/kur.py çalıştırın")

    anilan = sorted(set(re.findall(r"references/[\w./-]+\.(?:md|tsv|pdf|json)", skill)))
    for yol in anilan:
        tam = os.path.join(KOK, yol)
        if os.path.exists(tam):
            continue
        if yol in IZLENEN:
            hatalar.append(f"Depoda olması gereken dosya yok: {yol}")
        elif yol in ISTEGE_BAGLI:
            notlar.append(f"İsteğe bağlı dosya yok (sorun değil): {yol}")
        elif kurulum_var:
            hatalar.append(f"Kurulumda beklenen dosya yok: {yol}")
        else:
            notlar.append(f"Kurulum yapılınca gelecek: {yol}")
    for yol in IZLENEN:
        if yol not in anilan:
            hatalar.append(f"SKILL.md bu dosyayı anmıyor: {yol}")

    if kurulum_var:
        hatalar += kurulum_denetle()

    for n in notlar:
        print("not:", n)
    for h in hatalar:
        print("HATA:", h, file=sys.stderr)
    print(f"{len(anilan)} referans anıldı; kurulum {'var' if kurulum_var else 'yok'}; "
          f"{len(hatalar)} hata.")
    return 1 if hatalar else 0


def _tsv_ilk_sutun(ad: str) -> set[str]:
    with open(os.path.join(REF, ad), encoding="utf-8") as f:
        return {s.split("\t", 1)[0] for s in f if not s.startswith("#")}


def kurulum_denetle() -> list[str]:
    hatalar = []
    with open(os.path.join(REF, "KURULUM.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    dizin = _tsv_ilk_sutun("14-dizin.tsv")
    if len(dizin) < 70000:
        hatalar.append(f"Dizin beklenenden küçük: {len(dizin)} madde")
    beklenen = {"iş birliği": True, "işbirliği": False, "ünvan": True, "her şey": True,
                "herşey": False, "yüzyıl": True, "öz geçmiş": True}
    for kelime, var in beklenen.items():
        if (kelime in dizin) != var:
            hatalar.append(f"Dizin sorgusu beklenmedik: {kelime!r} {'yok' if var else 'var'}")
    kisaltma = _tsv_ilk_sutun("13-kisaltmalar-dizini.tsv")
    if len(kisaltma) < 900:
        hatalar.append(f"Kısaltmalar Dizini beklenenden küçük: {len(kisaltma)}")
    for k in ("TBMM", "AİHM", "vb.", "Av."):
        if k not in kisaltma:
            hatalar.append(f"Kısaltmalar Dizini'nde {k} yok")
    with open(os.path.join(REF, "09-noktalama-ve-kesme.md"), encoding="utf-8") as f:
        noktalama = f.read()
    if "## Kesme İşareti" not in noktalama or "Kanun’un 17" not in noktalama:
        hatalar.append("09-noktalama-ve-kesme.md beklenen Kesme İşareti bölümünü içermiyor")
    for uyari in manifest.get("uyarilar", []):
        print("kurulum uyarısı:", uyari)
    return hatalar


if __name__ == "__main__":
    sys.exit(main())
