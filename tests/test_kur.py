"""kur.py için çevrimdışı testler. Ağa çıkmaz; indirme işlevi sahte veriyle değiştirilir.

Çalıştırma:  python3 -m unittest discover -s tests -v
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import kur  # noqa: E402


class HtmlToMarkdown(unittest.TestCase):
    def test_kalin_ve_egik_bosluklari_disari_tasinir(self):
        md = kur.html_to_md("<p><b>1.&nbsp;</b>Kural:&nbsp;<i>bin, milyon</i>,&nbsp;<i>milyar&nbsp;</i>ve&nbsp;<i>trilyon</i></p>")
        self.assertEqual(md, "**1.** Kural: _bin, milyon_, _milyar_ ve _trilyon_\n")

    def test_yumusak_tire_ve_bom_silinir(self):
        md = kur.html_to_md("﻿<p>haf­tanın</p>")
        self.assertEqual(md, "haftanın\n")

    def test_basliklar(self):
        md = kur.html_to_md("<h1>BAŞLIK</h1><h2>Alt</h2><p>metin</p>")
        self.assertEqual(md, "# BAŞLIK\n\n## Alt\n\nmetin\n")

    def test_tablo_satirlari_bitisik_kalir(self):
        md = kur.html_to_md("<table><tr><td>.</td><td>nokta</td></tr><tr><td>|</td><td>dik <b>çizgi</b></td></tr></table>")
        self.assertEqual(md, "| . | nokta |\n|---|---|\n| \\| | dik **çizgi** |\n")

    def test_ust_simge(self):
        self.assertEqual(kur.html_to_md("<p>6<sup>4</sup>ten</p>"), "6⁴ten\n")

    def test_listeler(self):
        md = kur.html_to_md("<ol><li>bir</li><li>iki</li></ol><ul><li>madde</li></ul>")
        self.assertEqual(md, "1. bir\n\n2. iki\n\n- madde\n")

    def test_stil_ve_betik_atlanir(self):
        md = kur.html_to_md("<head><style>p{}</style></head><script>x()</script><p>görünür</p>")
        self.assertEqual(md, "görünür\n")


class Yardimcilar(unittest.TestCase):
    def test_isaretler_tablosu(self):
        md = "| . | nokta |\n|---|---|\n| x | ve . çarpma işareti, çarpı |\n"
        self.assertEqual(
            kur.isaretler_tablosunu_duzelt(md),
            "| İşaret | Adı |\n|---|---|\n| . | nokta |\n| x ve . | çarpma işareti, çarpı |\n",
        )

    def test_js_atamasi(self):
        self.assertEqual(kur.js_atamasi_coz('window.X = {"a": 1};\n'), {"a": 1})

    def test_turkce_siralama(self):
        kelimeler = ["Ü", "U", "Ç", "C", "İ", "I", "Ğ", "G", "Z"]
        self.assertEqual(sorted(kelimeler, key=kur._tr_sira), ["C", "Ç", "G", "Ğ", "I", "İ", "U", "Ü", "Z"])

    def test_tsv_sekme_ve_satir_sonu_temizlenir(self):
        self.assertEqual(kur._tsv("a\tb\nc"), "a b c")


HARITA = {f"content/{k}.html": f"<h1>{k}</h1><p>metin <i>örnek</i></p>" for k, _ in kur.TDK_SAYFALAR}
HARITA["content/14-noktalama-isaretleri-ve-diger-isaretler.html"] = (
    "<h1>İŞARETLER</h1><table><tr><td>.</td><td>nokta</td></tr><tr><td>x</td><td>ve . çarpı</td></tr></table>"
)
DIZIN = [{"m": "iş birliği"}, {"m": "abak", "e": "-ğı"}, {"m": "hâl", "e": "-li", "a": "durum"}]
KISALTMA = {"kavramlar": [
    {"tr": "Türk Dil Kurumu", "kisaltmalar": [{"kisaltma": "TDK", "dil": "Türkçe", "yabanci": None}]},
    {"tr": "Avukat", "kisaltmalar": [{"kisaltma": "Av.", "dil": "Türkçe", "yabanci": None}]},
]}
DD_SAYFA = "<html><table><tr><td>TDK</td><td>Türk Dil Kurumu</td></tr><tr><td>DD</td><td>Dil Derneği</td></tr></table></html>"


def sahte_indir(url, zaman_asimi):
    if url == kur.TDK_CONTENT_MAP:
        return ("window.CONTENT_MAP = " + json.dumps(HARITA) + ";").encode()
    if url == kur.TDK_DIZIN:
        return json.dumps(DIZIN).encode()
    if url == kur.TDK_KISALTMALAR:
        return ("window.KISALTMALAR=" + json.dumps(KISALTMA) + ";").encode()
    if url == kur.DIL_DERNEGI:
        return DD_SAYFA.encode()
    if url.endswith(".pdf") or ".pdf" in url:
        return b"%PDF-1.4 sahte"
    raise kur.IndirmeHatasi(url)


class Kurulum(unittest.TestCase):
    def setUp(self):
        self.gecici = tempfile.TemporaryDirectory()
        self.hedef = self.gecici.name

    def tearDown(self):
        self.gecici.cleanup()

    def oku(self, goreli):
        with open(os.path.join(self.hedef, goreli), encoding="utf-8") as f:
            return f.read()

    @mock.patch("sys.stdout")
    @mock.patch.object(kur, "indir", side_effect=sahte_indir)
    def test_tam_kurulum(self, _, __):
        # depoda izlenen bir dosya kurulumdan etkilenmemeli
        os.makedirs(os.path.join(self.hedef, "tez"))
        with open(os.path.join(self.hedef, "tez", "marmara-sbe.md"), "w", encoding="utf-8") as f:
            f.write("elle yazılmış özet\n")

        self.assertEqual(kur.main(["--hedef", self.hedef]), 0)

        for _, ad in kur.TDK_SAYFALAR:
            self.assertTrue(os.path.exists(os.path.join(self.hedef, ad + ".md")), ad)
        self.assertIn("| İşaret | Adı |", self.oku("12-isaretler-tablosu.md"))
        self.assertIn("| x ve . | çarpı |", self.oku("12-isaretler-tablosu.md"))
        self.assertIn("\nhâl\t-li\tdurum\n", self.oku("14-dizin.tsv"))
        kisaltma = [s for s in self.oku("13-kisaltmalar-dizini.tsv").splitlines() if not s.startswith("#")]
        self.assertEqual(kisaltma, ["Av.\tAvukat\tTürkçe\t", "TDK\tTürk Dil Kurumu\tTürkçe\t"])
        self.assertIn("TDK\tTürk Dil Kurumu\tTürk Dil Kurumu", self.oku("ek-kisaltmalar-dil-dernegi.tsv"))
        self.assertIn("DD\tDil Derneği\t\n", self.oku("ek-kisaltmalar-dil-dernegi.tsv"))
        for goreli, _, _ in kur.PDFLER:
            self.assertTrue(os.path.exists(os.path.join(self.hedef, goreli)), goreli)
        self.assertEqual(self.oku("tez/marmara-sbe.md"), "elle yazılmış özet\n")

        manifest = json.loads(self.oku("KURULUM.json"))
        self.assertEqual(manifest["kaynaklar"]["tdk"]["dizin_madde"], 3)
        self.assertEqual(manifest["uyarilar"], [])
        self.assertIn("14-dizin.tsv", manifest["dosyalar"])

    @mock.patch("sys.stdout")
    @mock.patch.object(kur, "indir", side_effect=sahte_indir)
    def test_yalniz_tdk(self, _, __):
        self.assertEqual(kur.main(["--hedef", self.hedef, "--yalniz-tdk"]), 0)
        self.assertFalse(os.path.exists(os.path.join(self.hedef, "ek-kisaltmalar-dil-dernegi.tsv")))
        self.assertFalse(os.path.exists(os.path.join(self.hedef, "tez")))

    def test_tdk_erisilemezse_hicbir_sey_degismez(self):
        onceki = os.path.join(self.hedef, "14-dizin.tsv")
        with open(onceki, "w", encoding="utf-8") as f:
            f.write("eski\n")

        def hep_hata(url, zaman_asimi):
            raise kur.IndirmeHatasi(url)

        with mock.patch.object(kur, "indir", side_effect=hep_hata), \
                mock.patch("sys.stderr"), mock.patch("sys.stdout"):
            self.assertEqual(kur.main(["--hedef", self.hedef]), 1)
        self.assertEqual(self.oku("14-dizin.tsv"), "eski\n")
        self.assertFalse(os.path.exists(os.path.join(self.hedef, "KURULUM.json")))

    def test_pdf_yerine_html_gelirse_uyari(self):
        def html_donen(url, zaman_asimi):
            if ".pdf" in url:
                return b"<html>hata</html>"
            return sahte_indir(url, zaman_asimi)

        with mock.patch.object(kur, "indir", side_effect=html_donen), mock.patch("sys.stdout"):
            self.assertEqual(kur.main(["--hedef", self.hedef]), 0)
        manifest = json.loads(self.oku("KURULUM.json"))
        self.assertEqual(len(manifest["uyarilar"]), len(kur.PDFLER))


if __name__ == "__main__":
    unittest.main()
