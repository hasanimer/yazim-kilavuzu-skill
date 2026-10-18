#!/usr/bin/env python3
"""TDK Yazım Kılavuzu skill'inin referans dosyalarını resmî kaynaklarından kurar.

Depoda TDK'nın, Dil Derneği'nin ve Marmara Üniversitesinin metinleri bulunmaz;
bu betik onları kuran kişinin bilgisayarına, doğrudan yayımlayan kurumun
sitesinden indirir ve skill'in okuyabileceği biçime (Markdown / TSV) çevirir.

Kullanım:
    python3 scripts/kur.py                      # her şeyi kur
    python3 scripts/kur.py --yalniz-tdk         # yalnızca TDK kuralları, dizin, kısaltmalar
    python3 scripts/kur.py --hedef /baska/yer   # references/ yerine başka klasöre yaz

Yalnızca Python standart kütüphanesini kullanır (3.9+). urllib SSL sertifikası
bulamazsa (macOS'taki python.org kurulumlarında sık görülür) curl'e geçer.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import html
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from html.parser import HTMLParser

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VARSAYILAN_HEDEF = os.path.join(KOK, "references")
UA = "Mozilla/5.0 (yazim-kilavuzu-skill kurulum betigi)"

TDK_KOK = "https://yazim.tdk.gov.tr"
TDK_CONTENT_MAP = TDK_KOK + "/assets/content-map.js"
TDK_DIZIN = TDK_KOK + "/assets/dizin.json"
TDK_KISALTMALAR = TDK_KOK + "/assets/kisaltmalar-data.js"
TDK_KISALTMALAR_JSON = TDK_KOK + "/assets/kisaltmalar.json"

# TDK sayfası -> skill'deki dosya adı
TDK_SAYFALAR = [
    ("00-sunus", "00-sunus"),
    ("01-ses-harf-ve-alfabe", "01-ses-harf-ve-alfabe"),
    ("02-sesler-ve-ses-uyumlari", "02-sesler-ve-ses-uyumlari"),
    ("03-bazi-kelime-ve-eklerin-yazilisi", "03-bazi-kelime-ve-eklerin-yazilisi"),
    ("04-sayilarin-yazilisi", "04-sayilarin-yazilisi"),
    ("05-buyuk-harflerin-kullanildigi-yerler", "05-buyuk-harfler"),
    ("06-birlesik-kelimelerin-yazilisi", "06-birlesik-kelimeler"),
    ("07-alinti-kelimelerin-yazilisi", "07-alinti-kelimeler"),
    ("08-yabanci-ozel-adlarin-yazilisi", "08-yabanci-ozel-adlar"),
    ("09-noktalama-isaretleri", "09-noktalama-ve-kesme"),
    ("11-kisaltmalar", "10-kisaltmalar"),
    ("12-simgeler", "11-simgeler"),
    ("14-noktalama-isaretleri-ve-diger-isaretler", "12-isaretler-tablosu"),
]

DIL_DERNEGI = "https://www.dildernegi.org.tr/TR,278/kisaltmalar-dizelgesi.html"

PDFLER = [
    # (hedef yol, URL, açıklama)
    ("resmi-yazisma/rg-20200610-yonetmelik-ve-ekler.pdf",
     "https://www.resmigazete.gov.tr/eskiler/2020/06/20200610-8.pdf",
     "Resmî Gazete 10.06.2020/31151: Resmî Yazışma Yönetmeliği ve örnek belgeler"),
    ("tez/marmara-sbe-tez-yazim-kilavuzu.pdf",
     "https://sbe.marmara.edu.tr/dosya/sbe/mevzuat/SBE-yeni_tez_yaz%C4%B1m_k%C4%B1lavuzu.2023.pdf",
     "Marmara Üniversitesi SBE Lisansüstü Tez ve Proje Yazım Kılavuzu"),
    ("tez/marmara-ebe-tez-yazim-kilavuzu.pdf",
     "https://ebe.marmara.edu.tr/dosya/ebe/Tez_Yaz%C4%B1m_K%C4%B1lavuzu%20(1).pdf",
     "Marmara Üniversitesi EBE Tez Yazım Kılavuzu"),
]

TR_ALFABE = "aâbcçdefgğhıiîjklmnoöprsştuûüvyz"


# --------------------------------------------------------------------------- indirme

class IndirmeHatasi(RuntimeError):
    pass


def indir(url: str, zaman_asimi: int) -> bytes:
    istek = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(istek, timeout=zaman_asimi) as yanit:
            return yanit.read()
    except urllib.error.URLError as hata:
        sertifika = isinstance(getattr(hata, "reason", None), ssl.SSLError) or "CERTIFICATE" in str(hata)
        if sertifika and shutil.which("curl"):
            return _curl(url, zaman_asimi)
        raise IndirmeHatasi(f"{url} indirilemedi: {hata}") from hata
    except (TimeoutError, OSError) as hata:
        if shutil.which("curl"):
            return _curl(url, zaman_asimi)
        raise IndirmeHatasi(f"{url} indirilemedi: {hata}") from hata


def _curl(url: str, zaman_asimi: int) -> bytes:
    sonuc = subprocess.run(
        ["curl", "-sSL", "--fail", "-m", str(zaman_asimi), "-A", UA, url],
        capture_output=True,
    )
    if sonuc.returncode != 0:
        raise IndirmeHatasi(f"{url} indirilemedi (curl): {sonuc.stderr.decode(errors='replace').strip()}")
    return sonuc.stdout


def js_atamasi_coz(metin: str) -> object:
    """`window.X = {...};` biçimindeki JS dosyasından JSON değerini çıkarır."""
    baslangic = metin.index("=") + 1
    return json.loads(metin[baslangic:].strip().rstrip(";"))


# --------------------------------------------------------------------------- HTML -> Markdown

YUMUSAK_TIRE = "­"
UST_SIMGE = str.maketrans("0123456789+-()no", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾ⁿᵒ")
ATLANAN = ("style", "script", "head", "title", "input", "label")


class _MarkdownCevirici(HTMLParser):
    """TDK'nın Word'den üretilmiş HTML sayfalarını sade Markdown'a çevirir."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.bloklar: list[str] = []
        self.tampon: list[str] = []
        self.atla = 0
        self.tablo: list[list[str]] | None = None
        self.satir: list[str] | None = None
        self.hucre: list[str] | None = None
        self.ust = False
        self.listeler: list[int | None] = []

    # Kalın/eğik işaretleri boşluğun dışına taşınır: "<i>a </i>b" -> "_a_ b".
    @staticmethod
    def _acilislari_duzelt(metin: str) -> str:
        return re.sub(r"\x00(\*\*|_)([ \t\r\n\xa0]*)", r"\2\1", metin)

    def _hedef(self) -> list[str]:
        return self.hucre if self.hucre is not None else self.tampon

    def _ac(self, isaret: str) -> None:
        self._hedef().append("\x00" + isaret)

    def _kapat(self, isaret: str) -> None:
        hedef = self._hedef()
        birlesik = "".join(hedef)
        govde = birlesik.rstrip(" \t\r\n\xa0")
        hedef[:] = [govde, isaret, birlesik[len(govde):]]

    def _blok_bitir(self, onek: str = "") -> None:
        metin = self._acilislari_duzelt("".join(self.tampon))
        self.tampon = []
        metin = metin.replace(YUMUSAK_TIRE, "").replace("\xa0", " ")
        metin = re.sub(r"[ \t\r\n]+", " ", metin).strip()
        metin = re.sub(r"\*\*\s*\*\*", "", metin)
        metin = re.sub(r"(?<![\w*])__(?!\w)", "", metin)
        metin = re.sub(r"_(\s+)_", r"\1", metin)
        if metin:
            self.bloklar.append(onek + metin)

    def handle_starttag(self, etiket, nitelikler):
        if etiket in ATLANAN:
            self.atla += 1
            return
        if self.atla:
            return
        if etiket == "table":
            self._blok_bitir()
            self.tablo = []
        elif etiket == "tr" and self.tablo is not None:
            self.satir = []
        elif etiket in ("td", "th") and self.satir is not None:
            self.hucre = []
        elif etiket in ("b", "strong"):
            self._ac("**")
        elif etiket in ("i", "em"):
            self._ac("_")
        elif etiket == "sup":
            self.ust = True
        elif etiket == "br":
            self._hedef().append(" " if self.hucre is not None else "\n")
        elif etiket == "code":
            self._hedef().append("`")
        elif etiket in ("p", "div", "h1", "h2", "h3", "h4") and self.hucre is None:
            self._blok_bitir()
        elif etiket == "ol":
            self.listeler.append(0)
        elif etiket == "ul":
            self.listeler.append(None)
        elif etiket == "li":
            self._blok_bitir()
            if self.listeler and self.listeler[-1] is not None:
                self.listeler[-1] += 1

    def handle_endtag(self, etiket):
        if etiket in ATLANAN:
            self.atla = max(0, self.atla - 1)
            return
        if self.atla:
            return
        if etiket in ("td", "th") and self.hucre is not None:
            metin = self._acilislari_duzelt("".join(self.hucre))
            metin = metin.replace(YUMUSAK_TIRE, "").replace("\xa0", " ")
            metin = re.sub(r"\s+", " ", metin).strip().replace("|", "\\|")
            self.satir.append(re.sub(r"\*\*\s*\*\*", "", metin))
            self.hucre = None
        elif etiket == "tr" and self.satir is not None:
            if any(self.satir):
                self.tablo.append(self.satir)
            self.satir = None
        elif etiket == "table" and self.tablo is not None:
            satirlar, self.tablo = self.tablo, None
            if satirlar:
                genislik = max(len(s) for s in satirlar)
                satirlar = [s + [""] * (genislik - len(s)) for s in satirlar]
                self.bloklar.append("| " + " | ".join(satirlar[0]) + " |")
                self.bloklar.append("|" + "---|" * genislik)
                self.bloklar.extend("| " + " | ".join(s) + " |" for s in satirlar[1:])
        elif etiket in ("b", "strong"):
            self._kapat("**")
        elif etiket in ("i", "em"):
            self._kapat("_")
        elif etiket == "sup":
            self.ust = False
        elif etiket == "code":
            self._hedef().append("`")
        elif self.hucre is None and etiket in ("h1", "h2", "h3", "h4"):
            self._blok_bitir("#" * int(etiket[1]) + " ")
        elif self.hucre is None and etiket in ("p", "div"):
            self._blok_bitir()
        elif etiket == "li":
            sira = self.listeler[-1] if self.listeler else None
            self._blok_bitir("- " if sira is None else f"{sira}. ")
        elif etiket in ("ol", "ul") and self.listeler:
            self.listeler.pop()

    def handle_data(self, veri):
        if self.atla:
            return
        if self.ust:
            veri = veri.translate(UST_SIMGE)
        self._hedef().append(veri)


def html_to_md(kaynak: str) -> str:
    cevirici = _MarkdownCevirici()
    cevirici.feed(kaynak.lstrip("﻿"))
    cevirici._blok_bitir()
    metin = "\n\n".join(cevirici.bloklar)
    metin = re.sub(r"\|\n\n\|", "|\n|", metin)          # tablo satırları bitişik kalsın
    metin = re.sub(r"(?<=[’\w])__(?=\s)", "", metin)      # Word'ün boş eğik parçaları
    metin = metin.replace("****", "")
    metin = re.sub(r"[ \t]+", " ", metin)
    metin = re.sub(r"\n{3,}", "\n\n", metin)
    return metin.strip() + "\n"


def isaretler_tablosunu_duzelt(md: str) -> str:
    """İşaretler tablosuna başlık satırı ekler, iki sütuna bölünmüş hücreleri onarır."""
    md = md.replace("| . | nokta |\n|---|---|\n", "| İşaret | Adı |\n|---|---|\n| . | nokta |\n", 1)
    md = re.sub(r"^\| (\S+) \| ve (\S+) (.+?) \|$", r"| \1 ve \2 | \3 |", md, flags=re.M)
    return md


# --------------------------------------------------------------------------- TDK

def tdk_kur(gecici: str, zaman_asimi: int, tarih: str) -> dict:
    sayfalar: dict[str, str] = {}
    try:
        harita = js_atamasi_coz(indir(TDK_CONTENT_MAP, zaman_asimi).decode("utf-8"))
        for kaynak, _ in TDK_SAYFALAR:
            sayfalar[kaynak] = harita[f"content/{kaynak}.html"]
    except (IndirmeHatasi, ValueError, KeyError) as hata:
        print(f"  content-map.js kullanılamadı ({hata}); sayfalar tek tek indiriliyor.")
        for kaynak, _ in TDK_SAYFALAR:
            sayfalar[kaynak] = indir(f"{TDK_KOK}/content/{kaynak}.html", zaman_asimi).decode("utf-8-sig")

    ozet = {"sayfalar": []}
    for kaynak, hedef in TDK_SAYFALAR:
        md = html_to_md(sayfalar[kaynak])
        if hedef == "12-isaretler-tablosu":
            md = isaretler_tablosunu_duzelt(md)
        kunye = (f"<!-- Kaynak: TDK Yazım Kılavuzu (2026 baskısı), "
                 f"{TDK_KOK}/#page=content%2F{kaynak}.html — indirildi {tarih} -->\n\n")
        _yaz(os.path.join(gecici, hedef + ".md"), kunye + md)
        ozet["sayfalar"].append(hedef + ".md")

    dizin = json.loads(indir(TDK_DIZIN, zaman_asimi).decode("utf-8"))
    satirlar = [
        f"# TDK Yazım Kılavuzu Dizini (2026 baskısı) — kaynak: {TDK_DIZIN} — {len(dizin)} madde — indirildi {tarih}",
        "# Sütunlar: madde<TAB>ek alınca aldığı biçim (ör. -ğı)<TAB>açıklama (eş yazılışları ayırt etmek için)",
    ]
    satirlar += [f"{_tsv(m['m'])}\t{_tsv(m.get('e', ''))}\t{_tsv(m.get('a', ''))}" for m in dizin]
    _yaz(os.path.join(gecici, "14-dizin.tsv"), "\n".join(satirlar) + "\n")
    ozet["dizin_madde"] = len(dizin)

    try:
        veri = js_atamasi_coz(indir(TDK_KISALTMALAR, zaman_asimi).decode("utf-8"))
    except (IndirmeHatasi, ValueError):
        veri = json.loads(indir(TDK_KISALTMALAR_JSON, zaman_asimi).decode("utf-8"))
    kayitlar = [
        (k["kisaltma"], kavram["tr"], k.get("dil") or "", k.get("yabanci") or "")
        for kavram in veri["kavramlar"] for k in kavram["kisaltmalar"]
    ]
    kayitlar.sort(key=lambda r: _tr_sira(r[0]))
    satirlar = [
        f"# TDK Kısaltmalar Dizini (2026 baskısı) — kaynak: {TDK_KOK} — {len(kayitlar)} satır — indirildi {tarih}",
        "# Sütunlar: kısaltma<TAB>Türkçe açılımı<TAB>kısaltmanın dili<TAB>yabancı açılım",
    ]
    satirlar += ["\t".join(_tsv(h) for h in r) for r in kayitlar]
    _yaz(os.path.join(gecici, "13-kisaltmalar-dizini.tsv"), "\n".join(satirlar) + "\n")
    ozet["kisaltma_satir"] = len(kayitlar)
    return ozet


def _tsv(deger: str) -> str:
    return re.sub(r"[\t\r\n]+", " ", str(deger)).strip()


def _tr_sira(kelime: str) -> list[int]:
    kucuk = kelime.replace("I", "ı").replace("İ", "i").lower()
    return [TR_ALFABE.index(c) if c in TR_ALFABE else 100 + ord(c) for c in kucuk]


# --------------------------------------------------------------------------- Dil Derneği

def dil_dernegi_kur(gecici: str, zaman_asimi: int, tarih: str) -> int:
    sayfa = indir(DIL_DERNEGI, zaman_asimi).decode("utf-8", errors="replace")
    tablo = re.search(r"<table.*?</table>", sayfa, re.S)
    if not tablo:
        raise IndirmeHatasi("Dil Derneği sayfasında kısaltma tablosu bulunamadı")
    satirlar = []
    for tr in re.findall(r"<tr.*?</tr>", tablo.group(0), re.S):
        hucreler = [
            re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()
            for h in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)
        ]
        if len(hucreler) >= 2 and hucreler[0]:
            satirlar.append(hucreler[:2])

    tdk: dict[str, list[str]] = {}
    tdk_yolu = os.path.join(gecici, "13-kisaltmalar-dizini.tsv")
    if os.path.exists(tdk_yolu):
        with open(tdk_yolu, encoding="utf-8") as f:
            for satir in f:
                if not satir.startswith("#"):
                    parca = satir.rstrip("\n").split("\t")
                    tdk.setdefault(parca[0], []).append(parca[1])

    cikti = [
        f"# Dil Derneği Kısaltmalar Dizelgesi — kaynak: {DIL_DERNEGI} — {len(satirlar)} kısaltma — indirildi {tarih}",
        "# UYARI: Dil Derneği TDK değildir; yazım tercihleri TDK'dan farklı olabilir (ör. \"İşbirliği\", "
        "\"Açık Öğretim\"). Çelişkide 13-kisaltmalar-dizini.tsv (TDK) esastır.",
        "# Sütunlar: kısaltma<TAB>Dil Derneği açılımı<TAB>TDK dizininde aynı kısaltma varsa TDK açılımı (yoksa boş)",
    ]
    cikti += [f"{_tsv(k)}\t{_tsv(v)}\t{_tsv(' / '.join(tdk.get(k, [])))}" for k, v in satirlar]
    _yaz(os.path.join(gecici, "ek-kisaltmalar-dil-dernegi.tsv"), "\n".join(cikti) + "\n")
    return len(satirlar)


# --------------------------------------------------------------------------- yardımcılar

def _yaz(yol: str, icerik) -> None:
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    kip = "wb" if isinstance(icerik, bytes) else "w"
    with open(yol, kip, **({} if kip == "wb" else {"encoding": "utf-8", "newline": "\n"})) as f:
        f.write(icerik)


def _sha256(yol: str) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 16), b""):
            h.update(parca)
    return h.hexdigest()


def _tasi(gecici: str, hedef: str) -> list[str]:
    """Geçici klasördeki dosyaları hedefe taşır; hedefteki depo dosyalarına dokunmaz."""
    tasinan = []
    for kok, _, dosyalar in os.walk(gecici):
        for ad in dosyalar:
            kaynak = os.path.join(kok, ad)
            goreli = os.path.relpath(kaynak, gecici)
            varis = os.path.join(hedef, goreli)
            os.makedirs(os.path.dirname(varis), exist_ok=True)
            shutil.move(kaynak, varis)
            tasinan.append(goreli)
    return sorted(tasinan)


# --------------------------------------------------------------------------- ana akış

def main(argv: list[str] | None = None) -> int:
    ayr = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ayr.add_argument("--hedef", default=VARSAYILAN_HEDEF, help="referans klasörü (öntanımlı: references/)")
    ayr.add_argument("--yalniz-tdk", action="store_true", help="Dil Derneği ve PDF'leri atla")
    ayr.add_argument("--dil-dernegi-yok", action="store_true", help="Dil Derneği kısaltmalarını atla")
    ayr.add_argument("--pdf-yok", action="store_true", help="Resmî Gazete ve tez kılavuzu PDF'lerini atla")
    ayr.add_argument("--zaman-asimi", type=int, default=120, help="istek başına saniye (öntanımlı 120)")
    secenek = ayr.parse_args(argv)

    tarih = _dt.date.today().strftime("%d.%m.%Y")
    hedef = os.path.abspath(secenek.hedef)
    os.makedirs(hedef, exist_ok=True)
    manifest: dict = {"kurulum_tarihi": tarih, "kaynaklar": {}, "dosyalar": {}, "uyarilar": []}

    with tempfile.TemporaryDirectory(prefix="yazim-kur-") as gecici:
        print("TDK Yazım Kılavuzu (yazim.tdk.gov.tr) indiriliyor…")
        try:
            manifest["kaynaklar"]["tdk"] = tdk_kur(gecici, secenek.zaman_asimi, tarih)
        except (IndirmeHatasi, ValueError, KeyError) as hata:
            print(f"HATA: TDK kaynakları kurulamadı: {hata}", file=sys.stderr)
            print("Hiçbir dosya değiştirilmedi. İnternet bağlantısını denetleyip yeniden çalıştırın.", file=sys.stderr)
            return 1
        tdk_ozet = manifest["kaynaklar"]["tdk"]
        print(f"  {len(tdk_ozet['sayfalar'])} kural sayfası, {tdk_ozet['dizin_madde']} dizin maddesi, "
              f"{tdk_ozet['kisaltma_satir']} kısaltma satırı")

        if not (secenek.yalniz_tdk or secenek.dil_dernegi_yok):
            print("Dil Derneği kısaltmaları indiriliyor…")
            try:
                adet = dil_dernegi_kur(gecici, secenek.zaman_asimi, tarih)
                manifest["kaynaklar"]["dil_dernegi"] = {"url": DIL_DERNEGI, "kisaltma": adet}
                print(f"  {adet} kısaltma")
            except IndirmeHatasi as hata:
                manifest["uyarilar"].append(str(hata))
                print(f"  UYARI: {hata} (atlandı)")

        if not (secenek.yalniz_tdk or secenek.pdf_yok):
            for goreli, url, aciklama in PDFLER:
                print(f"{aciklama} indiriliyor…")
                try:
                    veri = indir(url, secenek.zaman_asimi)
                    if not veri.startswith(b"%PDF"):
                        raise IndirmeHatasi(f"{url} PDF döndürmedi")
                    _yaz(os.path.join(gecici, goreli), veri)
                    manifest["kaynaklar"][goreli] = {"url": url, "bayt": len(veri)}
                except IndirmeHatasi as hata:
                    manifest["uyarilar"].append(str(hata))
                    print(f"  UYARI: {hata} (atlandı)")

        for kok, _, dosyalar in os.walk(gecici):
            for ad in dosyalar:
                yol = os.path.join(kok, ad)
                manifest["dosyalar"][os.path.relpath(yol, gecici)] = _sha256(yol)
        _tasi(gecici, hedef)

    _yaz(os.path.join(hedef, "KURULUM.json"), json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Tamam: {len(manifest['dosyalar'])} dosya {hedef} altına kuruldu.")
    if manifest["uyarilar"]:
        print(f"{len(manifest['uyarilar'])} uyarı var; ayrıntı için KURULUM.json dosyasına bakın.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
