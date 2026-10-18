---
name: yazim-kilavuzu
description: Türkçe metinleri TDK Yazım Kılavuzu (2026 baskısı) kurallarına göre yazma, düzeltme ve denetleme; 81.141 maddelik resmî Yazım Kılavuzu Dizini ve TDK Kısaltmalar Dizini ile kelime kelime doğrulama. Büyük harf, kesme işareti (kanun ve kurum adlarına gelen ekler dâhil), bitişik/ayrı yazım, de/da, ki, mi, sayılar, kısaltmalar, noktalama ve düzeltme işaretini kapsar. Ek modüller - kamu kurumlarına yazılan yazılarda Resmî Yazışma Yönetmeliği (2646) biçim kuralları; Marmara Üniversitesi SBE ve EBE tez yazım kılavuzları (kapak, biçim, atıf ve kaynakça). Kullanıcı "TDK'ya göre", "yazım kılavuzu", "imla", "yazım hatası", "noktalama", "doğru yazılışı", "bitişik mi ayrı mı", "kesme işareti gerekir mi", "metni düzelt / redakte et / imla kontrolü yap", "resmî yazı", "üst yazı", "arz ederim mi rica ederim mi", "tez yazım kılavuzu", "kaynakça nasıl yazılır" dediğinde ya da dilekçe, sözleşme, rapor, resmî yazı veya tez gibi bir Türkçe metnin son okuması istendiğinde kullan.
---

# TDK Yazım Kılavuzu

Esas kaynak: TDK'nın resmî çevrim içi Yazım Kılavuzu, **2026 baskısı** — https://yazim.tdk.gov.tr. Kural metinleri, dizin ve kısaltmalar `references/` altında tam olarak bulunur; bu dosyadaki özet hızlı karar içindir. Kesin hüküm vereceğin her durumda ilgili referans dosyasındaki asıl ifadeyi ve TDK'nın örneğini kontrol et.

**Yollar:** Bu belgedeki `references/…` ve `scripts/…` yolları skill klasörüne görelidir (Claude Code bu klasörü "Base directory for this skill" olarak verir; kişisel kurulumda `~/.claude/skills/yazim-kilavuzu`). Komutları bu klasörde çalıştır ya da yolun başına klasörü ekle.

**Kurulum denetimi:** TDK metinleri, dizin ve PDF'ler depoda bulunmaz; `scripts/kur.py` onları kaynak sitelerden indirir. `references/14-dizin.tsv` yoksa kurulum yapılmamıştır: kullanıcıya bunu söyle ve onayını alarak `python3 scripts/kur.py` çalıştır (yalnızca Python standart kütüphanesi; birkaç saniye). Kurulum yapılamazsa yalnızca bu dosyadaki özet kurallarla ve depodaki özet dosyalarıyla çalıştığını açıkça belirt.

## Referans dosyaları

**Resmî TDK metinleri (2026, kurulumla gelir)** — çelişkide her zaman bunlar esastır:

| Dosya | İçerik |
|---|---|
| `references/01-ses-harf-ve-alfabe.md` | Alfabe, harf adları ve kodları |
| `references/02-sesler-ve-ses-uyumlari.md` | Ünlü/ünsüz nitelikleri, uzun ünlü, **düzeltme işareti**, büyük/küçük ünlü uyumu, ünlü daralması/düşmesi, ünsüz uyumu/türemesi |
| `references/03-bazi-kelime-ve-eklerin-yazilisi.md` | Soru eki *mi*, bağlaç *de/da*, bağlaç *ki*, *ile*, bulunma eki *-de/-da*, fiil çekimi, mastarlara gelen ekler, ek-fiil, pekiştirmeli sözler |
| `references/04-sayilarin-yazilisi.md` | Sayılar, Romen rakamları, sıra ve üleştirme sayıları |
| `references/05-buyuk-harfler.md` | **Büyük harflerin kullanıldığı yerler** |
| `references/06-birlesik-kelimeler.md` | **Bitişik** ve **ayrı** yazılan birleşik kelimeler, deyimler, ikilemeler |
| `references/07-alinti-kelimeler.md` | Alıntı (Batı kökenli) kelimelerin yazılışı |
| `references/08-yabanci-ozel-adlar.md` | Latin, Arap-Fars, Yunan, Rus, Uzak Doğu ve Türk dünyası özel adları |
| `references/09-noktalama-ve-kesme.md` | Bütün noktalama işaretleri, **Kesme İşareti** bölümü, **hece yapısı ve satır sonunda bölme** |
| `references/10-kisaltmalar.md` | Kısaltma kuralları ve **kısaltmalara gelen ekler** |
| `references/11-simgeler.md` | Element simgeleri |
| `references/12-isaretler-tablosu.md` | Noktalama ve diğer işaretlerin tablosu |
| `references/13-kisaltmalar-dizini.tsv` | TDK Kısaltmalar Dizini, 1.089 satır: `kısaltma⇥açılım⇥dil⇥yabancı açılım` |
| `references/14-dizin.tsv` | **Yazım Kılavuzu Dizini, 81.141 madde**: `madde⇥ek alınca aldığı biçim⇥açıklama` |
| `references/00-sunus.md` | Kılavuzun tarihçesi (kural içermez) |

**Modüller:**

| Dosya | İçerik |
|---|---|
| `references/resmi-yazisma/ozet.md` | Resmî Yazışma Yönetmeliği'nin uygulama özeti: belge bölümleri, ölçüler, kontrol listesi, Resmî Gazete'deki örnek belgelerin sayfa dizini, Yönetmelik ile TDK 2026 arasındaki yazım farkları |
| `references/resmi-yazisma/yonetmelik-2646.md` | Yönetmeliğin tam metni (madde madde) |
| `references/resmi-yazisma/rg-20200610-yonetmelik-ve-ekler.pdf` | Resmî Gazete nüshası; örnek belgeler görsel (kurulumla gelir; sayfayı `ozet.md`deki dizinden bulup Read ile aç) |
| `references/tez/marmara-sbe.md` | Marmara Üniversitesi Sosyal Bilimler Enstitüsü tez yazım kılavuzunun özeti |
| `references/tez/marmara-ebe.md` | Marmara Üniversitesi Eğitim Bilimleri Enstitüsü tez yazım kılavuzunun ve teslim kurallarının özeti; SBE ile karşılaştırma |
| `references/tez/marmara-sbe-tez-yazim-kilavuzu.pdf`, `references/tez/marmara-ebe-tez-yazim-kilavuzu.pdf` | Kılavuzların asılları (kurulumla gelir; kapak örnekleri gibi görsel ayrıntılar için Read ile aç) |

**Ek kaynaklar (resmî değil)** — yalnızca tarama ve bilgi için; TDK ile çelişirse TDK esastır:

| Dosya | İçerik |
|---|---|
| `references/ek-sik-yapilan-hatalar-vikipedi.md` | Vikipedi'nin "Türkçede sık yapılan hatalar" sayfası (CC BY-SA 4.0): sık yanlış yazılan kelimeler (hatalı → doğru), sık karıştırılan sözler, TDK–Dil Derneği farkları |
| `references/ek-kisaltmalar-dil-dernegi.tsv` | Dil Derneği Kısaltmalar Dizelgesi (684 kısaltma, kurulumla gelir); 3. sütunda TDK karşılığı. Dil Derneği'nin yazım tercihleri TDK'dan farklı olabilir (*İşbirliği, Açık Öğretim*) |
| `references/ek-2023-degisiklikleri-ogretmen-derlemesi.md` | Yalnızca yerel kurulumlarda bulunabilir, pakette yoktur. Varsa: 2023'te TDK sözlüğünde değişen 67 yazım (ör. *unvan → ünvan*) |

`.md` dosyaları büyük olabilir (09 ve 06 özellikle); tamamını okumak yerine `grep -n` ile ilgili bölümü bul ve oku. `.tsv` dosyalarını **asla bütünüyle okuma**, yalnızca `grep` ile sorgula.

## Kelime sorgulama

Tek bir kelimenin yazılışı (bitişik/ayrı, düzeltme işareti, ek alınca aldığı biçim) için önce resmî dizine bak:

```bash
# tam eşleşme (madde sütunu)
grep -P '^iş birliği\t' references/14-dizin.tsv
# aday biçimleri birlikte görmek için (bitişik/ayrı/şapkalı)
grep -iP '^(iş ?birliği|işbirliği)\t' references/14-dizin.tsv
# kısaltma
grep -P '^AİHM\t' references/13-kisaltmalar-dizini.tsv
```

- Madde dizinde varsa yazılış odur. İkinci sütundaki ek bilgisi ek alırken alacağı biçimi gösterir (ör. `abak⇥-ğı`: *abağı*). Üçüncü sütun eş yazılışları ayırt eder (ör. `hâl⇥-li⇥durum`).
- **Dizinde olmaması yanlış olduğunu kanıtlamaz.** Dizin serbest söz öbeklerini (ör. *bir şey*) ve her türevi listelemez. Bu durumda kurala bak; gerekirse TDK Güncel Türkçe Sözlük'e sor:
  ```bash
  curl -s -m 60 -A "Mozilla/5.0" "https://sozluk.gov.tr/gts?ara=bir+%C5%9Fey"
  ```
  (URL kodla, boşluk `+`). `{"error":"Sonuç bulunamadı"}` o biçimin sözlükte olmadığını gösterir. Servis yavaş olabilir; yanıt gelmezse bunu açıkça söyle, tahmini kesin bilgi gibi sunma.
- Kısaltmalar Dizini her kısaltmayı içermez (ör. *ABD* yalnızca "Ana bilim dalı" olarak geçer; oysa 10-kisaltmalar.md'de Amerika Birleşik Devletleri örneği olarak kullanılır). Bulamazsan kuralı uygula ve bunu belirt.

## Çalışma biçimi

1. **Tek kelime/yapı sorusu** (ör. "bitişik mi ayrı mı?"): dizinde ara. Sonuç kurala dayanıyorsa ilgili referans dosyasından kuralı ve TDK örneğini kısa alıntıyla ver.
2. **Metin düzeltme/denetleme**:
   - Metnin anlamını, üslubunu, terimlerini ve hukuki/teknik içeriğini değiştirme; yalnızca yazım ve noktalama düzelt (kullanıcı ayrıca üslup düzeltmesi istemedikçe).
   - Şüpheli kelimeleri dizinde doğrula. Ek olarak `ek-sik-yapilan-hatalar-vikipedi.md` içindeki "Sıklıkla hatalı yazılan bazı sözcükler" tablosuyla tarama yapabilirsin. Oradan bulduğun düzeltmeyi uygulamadan önce dizinle teyit et.
   - Önce düzeltilmiş metnin tamamını ver, ardından değişiklikleri tablo hâlinde göster:

     | # | Yanlış | Doğru | Kural |
     |---|---|---|---|
     | 1 | Türk Dil Kurumu'na | Türk Dil Kurumuna | Kurum adlarına gelen ekler kesmeyle ayrılmaz (Kesme İşareti, UYARI) |
     | 2 | Türk Medeni Kanununa | Türk Medeni Kanunu'na | Kanun adlarına gelen ekler kesmeyle ayrılır (Kesme İşareti, 1) |

   - Kılavuzun iki yazımı da kabul ettiği yerlerde (ör. *ile / -le*, *idi / -dı*, *iken / -ken* hem ayrı hem bitişik yazılabilir) değişiklik yapma; gerekiyorsa not düş.
   - Alıntılar, mevzuat ve karar metinlerinden aynen yapılan alıntılar ve özel adlar (kişi, şirket, tescilli kurum adları) **değiştirilmez**; yalnızca kullanıcının kendi metni düzeltilir.
3. **Yeni metin yazarken**: aşağıdaki kontrol listesini uygula.
4. **Resmî yazı** (kamu kurumuna yazılan ya da kamu kurumunca hazırlanan yazı, üst yazı, "arz/rica ederim" sorusu): `references/resmi-yazisma/ozet.md` dosyasını oku; biçimi (başlık, sayı, tarih, konu, muhatap, ilgi, metin, imza, ek, dağıtım) oradaki kontrol listesiyle denetle ve her bulguya Yönetmelik maddesini yaz (ör. "m.13/1"). Maddenin tam ifadesi gerekiyorsa `yonetmelik-2646.md`de `grep -n "### Madde 13"` ile bul. Kullanıcı örnek belge görmek isterse `ozet.md`deki örnekler dizininden sayfayı bulup PDF'i Read ile o sayfadan aç. Yönetmelik yalnızca kamu kurum ve kuruluşlarını bağlar (m.1/2); avukat dilekçesi veya özel bir belge için ancak biçim önerisi olarak kullan ve bunu söyle. Yazım ve noktalama için Yönetmelik m.16/8 gereği güncel TDK esastır; Yönetmelik metninden yapılan aynen alıntılara dokunma.
5. **Tez** (Marmara Üniversitesi SBE veya EBE): önce hangi enstitü olduğunu belirle (belli değilse sor). İlgili özet dosyasını (`references/tez/marmara-sbe.md` ya da `marmara-ebe.md`) oku. Biçim, kapak, atıf ve kaynakça konusunda kılavuzu; yazım ve noktalama konusunda TDK'yı esas al; kılavuzla danışman görüşü çelişirse son sözün danışmanda olduğunu belirt. Kapak ya da sayfa düzeni gibi görsel ayrıntılarda özet yetmezse PDF'i Read ile aç. Başka bir üniversite ya da enstitü sorulursa bu özetleri kural gibi uygulama; o kurumun kılavuzunu iste.

## Hızlı kontrol listesi

**Kesme işareti** (`09-noktalama-ve-kesme.md` → "Kesme İşareti")
- Özel adlara gelen iyelik, durum ve bildirme ekleri kesmeyle ayrılır: *Ankara'da, Atatürk'ün, Türkiye'mizin*.
- **Kanun, tüzük, yönetmelik adlarına ve *Resmî Gazete*'ye gelen ekler kesmeyle ayrılır**: *Millî Eğitim Temel Kanunu'na, Telif Hakkı Yayın ve Satış Yönetmeliği'ni, Resmî Gazete'de*. Belli bir kanun kastedilerek büyük harfle yazılan *Kanun, Yönetmelik* sözlerine de: *Bu Kanun'un 17. maddesi, Yönetmelik'in 2'nci maddesi*.
- **Kurum, kuruluş, kurul, birleşim, oturum ve iş yeri adlarına gelen ekler kesmeyle ayrılmaz**: *Türkiye Büyük Millet Meclisine, Türk Dil Kurumundan, Yürütme Kuruluna, 112'nci Birleşiminin 2'nci Oturumunda*. İstisna: *Avrupa Birliği'ne*.
- Akım, çağ, dönem ve tarihî olay adlarına: *Eski Çağ'ın, Tanzimat Dönemi'nde, Kurtuluş Savaşı'nı*.
- Kişi adlarından sonra gelen saygı ve ünvan sözlerine: *Ayşe Hanım'dan, Türk Dil Kurumu Başkanı'na*.
- Yapım ekleri, çokluk eki ve sonrakiler kesmeyle ayrılmaz: *Türkçenin, Avrupalı, Konyalı, Ahmetler, Türklerin*.
- Kısaltmalara gelen ekler kesmeyle ayrılır ve **son harfin Türkçe adının okunuşuna** uyar. Harf adları (01-ses-harf-ve-alfabe.md): b **be**, c **ce**, ç **çe**, d **de**, f **fe**, g **ge**, ğ **yumuşak ge**, h **he**, j **je**, k **ke**, l **le**, m **me**, n **ne**, p **pe**, r **re**, s **se**, ş **şe**, t **te**, v **ve**, y **ye**, z **ze**; ünlüler kendi seslerini verir. Türkçede ünsüz harfin adı ünsüz + *e*'dir (*M* = **me**, *em* değil; *K* = **ke**, *ka* değil). Bütün ünsüz harf adları ince ünlü *e* ile biter, bu yüzden ek her zaman ince ve ünlüden sonra gelen biçimdedir: *TBMM'ye, TBMM'nin, TDK'ye, TDK'den, AİHM'ye, ABD'de, THY'de, TL'nin* (*TBMM'e, AİHM'e, ABD'da* yanlış). Kelime gibi okunanlar okunuşa göre: *NATO'dan, ASELSAN'da*. Sert ünsüz yumuşamaz: *RTÜK'e, TÜBİTAK'ın*. Noktalı kısaltmalarda kesme yok: *vb.leri, Alm.dan*; küçük harfli ölçü kısaltmalarında okunuşa göre: *cm'yi, kg'dan*.
- Sayılara ve belirli tarih bildiren ay/gün adlarına: *1985'te, 8'inci madde, 17 Aralık'a kadar*.
- Özel ad yerine kullanılan *o* zamiri küçük yazılır, kesme almaz.

**Büyük harf** (`05-buyuk-harfler.md`)
- Kurum, kurul, kanun, yönetmelik ve eser adlarının her kelimesi büyük; asılları kastedildiğinde tek başına da büyük: *Kanun, Kurum, Meclis, Bakanlık*.
- Özel ad içindeki *ve, ile, ya, veya, yahut, ki, da, de* ve *mı/mi* küçük: *Atatürk Kültür, Dil ve Tarih Yüksek Kurumu*.
- Saygı sözlerinden sonraki makam sözleri ve resmî yazışmalardaki hitaplar büyük: *Sayın Bakan, Sayın Başkan*. Akrabalık bildiren kelimeler küçük: *Ayşe teyzemin*.
- Özel ada dâhil olmayan *il, ilçe, köy, gazete, dergi* küçük: *Konya ili, Milliyet gazetesi*. Para birimleri küçük: *lira, avro, dolar*.
- Belirli tarih bildiren ay ve gün adları büyük (*29 Ekim 1923 Pazartesi*); belirli tarih bildirmeyenler küçük (*perşembe günleri*).
- İki noktadan sonra cümle gelirse büyük, cümle ve özel ad olmayan sıralama gelirse küçük başlar.

**Bağlaç ve ekler** (`03-bazi-kelime-ve-eklerin-yazilisi.md`)
- Bağlaç *de/da* ayrı yazılır, asla *te/ta* olmaz, kesmeyle ayrılmaz: *Ayşe de geldi*, *ya da*. Bulunma eki bitişik: *evde, işte*.
- Bağlaç *ki* ayrı: *demek ki, kaldı ki*. Kalıplaşmış bitişikler: *belki, çünkü, hâlbuki, mademki, meğerki, oysaki, sanki*.
- Soru eki *mı/mi/mu/mü* ayrı, sonrasındaki ekler ona bitişik: *Gelecek misin?*
- *-acak/-ecek, -an/-en* vb. öncesinde söyleyişe bakılmaz: *başlayacağım, gelmeyen*.

**Birleşik kelimeler** (`06-birlesik-kelimeler.md`; şüphede dizine bak)
- Bitişik: *birçok, birkaç, birtakım, biraz, herhangi, hiçbir*; *-ev, -hane, -name, -zade, -zede* (*yayınevi, beyanname, depremzede*); ses olayıyla *etmek/olmak* (*hissetmek, kaybolmak, affetmek*); anlam kaymasıyla oluşanlar (*aslanağzı*); somut yer bildirmeyen *alt/üst* (*bilinçaltı, olağanüstü, suçüstü, gözaltı*); kanunda bitişik geçen kurum adları (*İçişleri, Dışişleri, Yükseköğretim Kurulu*).
- Ayrı: *iş birliği, iş bölümü, ön yargı, ön söz, art niyet, alt kurul, karşı oy, peşin hüküm*; ses olayı olmayan *etmek/olmak* (*kabul etmek, terk etmek, ilan etmek*); *dış, iç, sıra* ile kurulanlar (*yasa dışı, olağan dışı, yurt içi, yanı sıra*); somut yer bildiren *alt/üst* (*yer altı*); deyimler ve ikilemeler (*yavaş yavaş, baş başa*).

**Sayılar** (`04-sayilarin-yazilisi.md`)
- Saat, para, ölçü, istatistikte rakam: *1.500.000 lira*. Dört ve daha çok basamaklılarda üçlü gruplar nokta ile, kesirler virgülle: *4.567; 15,2*.
- Birden fazla kelimeli sayılar ayrı (*iki yüz elli*); senet, çek gibi belgelerde bitişik (*altıyüzelliTL*).
- *%25* (boşluksuz). Üleştirme sayıları yazıyla (*ikişer*). Sıra sayısı *15.* veya *15'inci* (*15.'inci* değil). Cümle rakamla başlamaz.

**Kısaltmalar** (`10-kisaltmalar.md`, `13-kisaltmalar-dizini.tsv`)
- Büyük harfli kısaltmalarda nokta yok (*TBMM*); gelenekleşmiş istisnalar *T.C., T.* Unvan ve cins isim kısaltmalarında nokta var: *Prof., Dr., Av., vb., çev.*

**Noktalama** (`09-noktalama-ve-kesme.md`)
- Nokta, virgül, noktalı virgül, iki nokta, üç nokta, soru, ünlem, tırnak, ayraç ve kesme işaretleri önceki kelimeye bitişik yazılır.
- Üç nokta üç noktadır; soru ve ünlemden sonra iki nokta yeterlidir (*?..*, *!..*).
- Tırnak içindeki alıntının sonundaki nokta, soru, ünlem işareti tırnağın içinde kalır.

**Düzeltme işareti** (`02-sesler-ve-ses-uyumlari.md`)
- Anlam ayırt etmek için: *hâlâ / hala, âdet / adet, âlem / alem, âşık / aşık, hâl / hal* (*katil, kadir* işaretsiz).
- Arapça ve Farsça kökenli kelimelerde ince *g, k*'den sonra gelen *a, u* üzerine: *dükkân, hikâye, kâğıt, mahkûm, sükût*. Kişi ve yer adlarında ince *l*'den sonra: *Lâle, Halûk, Elâzığ*.
- Nispet *î*'si: *askerî, resmî, millî, dinî*; ek alınca korunur: *millîleştirmek, resmîlik*.

**Hukuk metinlerinde sık geçen kelimeler** (dizinde doğrulanmış): *ünvan* (2023'ten beri; *unvan* dizinde yok), *kayyım* (dizinde *kayyum* da var), *hâlbuki, yalnız, iş birliği, art arda, öz geçmiş, olağan dışı, her şey*.

## Dikkat

- Bu özet sadeleştirilmiştir. Kesin hüküm vermeden önce referanstaki asıl ifadeyi kontrol et; yanıtta kuralın adını ve dosyasını belirt.
- Yalnızca "ek-" önekli dosyalara dayanan bir düzeltmeyi kesin TDK hükmü gibi sunma; kaynağını söyle.
