# scrapbot

`scrapbot`, verdiğin OpenStax kitap URL'sinden yalnızca aynı kitabın bölüm
sayfalarını izleyen küçük bir [Scrapy](https://scrapy.org/) uygulamasıdır.
Başka kitaplara, hesap sayfalarına veya OpenStax'ın geri kalanına yayılmaz.

## Kurulum

Python 3.10 veya üstü gerekir.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Windows PowerShell'de etkinleştirme komutu:

```powershell
.venv\Scripts\Activate.ps1
```

## Kullanım

```bash
scrapbot "https://openstax.org/details/books/prealgebra-2e" \
  --output data/prealgebra-2e.jsonl
```

Paket komutu PATH üzerinde görünmezse aynı işlem şöyle çalıştırılabilir:

```bash
python -m scrapbot "https://openstax.org/details/books/prealgebra-2e" \
  --output data/prealgebra-2e.jsonl
```

Çıktının her satırı bir kitap sayfasıdır ve şu alanları içerir:

- `title`, `source_url`, `content_text`, `content_html`
- kitap ve sayfa kimlikleri
- dil, lisans bağlantısı ve sayfa bazında OpenStax atfı
- OpenStax'ın LLM/generative-AI kullanım uyarısı

Bot `robots.txt` kurallarına uyar, otomatik hız ayarlama kullanır ve aynı anda
en fazla iki isteği yalnızca seçilen kitap kapsamında çalıştırır.

## Çeviri hakkında

Chrome'un yerleşik “Türkçeye çevir” özelliği Scrapy'nin çağırabileceği kararlı
ve belgelenmiş bir API değildir. Headless Chrome üzerinden bu menüyü zorlamak
kırılgan olduğu için bu sürüm, içeriği çevrilmiş gibi göstermiyor ve ücretsiz
Google Translate uç noktalarını izinsiz kullanmıyor.

Çeviri eklenirse, çıktıdaki `content_text` alanını **yerel** bir çeviri
motoruna gönderen ayrı bir adım tercih edilmelidir. OpenStax sayfasındaki
LLM/generative-AI kısıtlaması nedeniyle kitap metnini bir üretken yapay zekâ
servisine izinsiz göndermeyin. Çeviriyi dağıtırken kitap lisansının atıf,
gayriticari kullanım ve aynı lisansla paylaşım şartlarını koruyun.

## Test

```bash
python -m pip install -e ".[dev]"
pytest
```

Testler ağa çıkmaz; sayfa kapsamı ve çıkarım davranışını küçük HTML örnekleriyle
doğrular.

## Lisans ve kullanım notu

Örnek `Prealgebra 2e` kitabı **CC BY-NC-SA 4.0** lisanslıdır; “CC-BY-NA”
değildir. Her dijital sayfa görünümünde kaynak atfını koruyun. OpenStax'ın
sayfada yayımladığı güncel lisans ve kullanım koşulları her zaman belirleyicidir.
