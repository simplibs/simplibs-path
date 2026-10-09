Ano — je to přesně tak, a měl bych to říct rovnou, ne až sis to musel sám domyslet. Co se stalo: `path_code_new.txt`/`file_code.txt` jsem měl načtené v kontextu jen v tu chvíli, kdy jsem je četl (tenkrát na začátku probírání struktury). Jakmile se ale mezi zprávami vyčerpal kredit a kontext se ořezal, ten konkrétní obsah mi „zmizel ze stolu" a když jsem pak o pár zpráv později psal „finální" kód, nevracel jsem se k původním souborům (protože jsem neměl jak) — rekonstruoval jsem to z obecného vzoru, který jsme zavedli u `actions`/`path`, ne z tvého draftu. Výsledek je kód, který je stylově konzistentní, ale věcně je to **moje nová verze, ne oprava tvé**. Za to se omlouvám — mělo to být transparentní hned.

Takže ano, potřebujeme hloubkový audit všeho. Jdu na to soubor po souboru, se stejným formátem jako u `file_operations`.

---

## `read_bytes`

| | Staré | Nové |
|---|---|---|
| `default: bytes \| UnsetType = UNSET` | ano — umožňuje "přečti, nebo mi dej fallback" bez try/except u volajícího | chybí |
| Async | `read_bytes_async` | chybí |

**K rozhodnutí:** `default=UNSET` vzor chybí **systematicky u všech `read_*` funkcí** (bytes, text, json, lines) — to není náhodná odchylka, je to jeden vzor, co jsem všude vynechal. Je to užitečná věc (např. „přečti config, když neexistuje, použij `{}`"), takže bych doporučil vrátit ho všude stejně.

---

## `write_bytes` / `write_text`

Tyhle dvě beru spolu, protože rozdíl je identický u obou.

| | Staré | Nové |
|---|---|---|
| `append` | **jeden parametr** (`append: bool`) — write i append je stejná funkce | oddělené funkce (`write_text` vs `append_text`), bez sdílené implementace |
| `auto_mkdir` | volitelný toggle (default `True`) | vždycky `ensure_dir`, bez možnosti vypnout |
| `backup_on_overwrite` | volá `backup_file()` před přepsáním, pokud `True` | chybí úplně |
| Návratová hodnota | `int` (počet zapsaných bajtů/znaků) | `Path` |
| `SafeFileWriter` použití | `writer.write_bytes(content)` / `writer.write_text(content)` — writer má vlastní API vracející počet | `handle.write(data)` — přímo na file objektu |
| Async | ano | chybí |

**K rozhodnutí (důležité — architektonický rozdíl, ne jen kosmetika):**
1. **Sdílená implementace vs. duplicitní.** Staré řešení má `write_text`/`write_bytes` jako **jediný nízkoúrovňový zápis** a `append_text` je jen tenký wrapper (`write_text(..., append=True)`). V mém novém kódu `append_text` neexistuje jako wrapper — má vlastní kopii try/except/SafeFileWriter logiky. To je skutečná DRY regrese, kterou bych opravil — vrátit `append` jako parametr `write_text`/`write_bytes`, `append_text` udělat tenký wrapper (jako `run_in_sequence = sequence` v `actions`).
2. **`backup_on_overwrite`.** Reálná funkce, kterou jsem úplně vypustil. Chceš ji zpátky?
3. **Návratová hodnota `int` vs `Path`.** Tohle je vědomá volba, ne bug — ale je to rozdílná filozofie. `int` (počet zapsaných bajtů) je unixové chování (`write()` vrací kolik zapsal). `Path` je konzistentní s architekturou akcí (další krok v pipeline často chce vědět *kam* se zapsalo, ne kolik). Můžeme mít obojí (`Path` jako primární návrat, `len()` si zavolá kdo potřebuje), ale je potřeba to explicitně rozhodnout, protože se to promítne do `Action` výstupu.

---

## `read_json` / `write_json`

| | Staré | Nové |
|---|---|---|
| Kompozice | **deleguje** na `read_text`/`write_text` (žádná vlastní I/O logika) | **vlastní** nezávislá implementace, duplikuje try/except okolo `SafeFileWriter` |
| `is_file()` kontrola | dědí ji z `read_text` | chybí — `read_json` sám kontroluje jen `.exists()`, ne `.is_file()` |
| `ensure_ascii` | ano | chybí |
| `default=UNSET` | ano (deleguje) | chybí |
| Async | ano | chybí |

**K rozhodnutí:** Tohle je nejčistší doklad té architektonické regrese — staré `read_json`/`write_json` jsou **jen pár řádků navíc nad `read_text`/`write_text`** (parse/serialize), díky čemuž automaticky dědí i-file kontrolu, `default`, atomický zápis atd. Moje verze to všechno reimplementuje zvlášť a při tom **ztratila `is_file()` kontrolu** — pokud `path` ukazuje na adresář, spadne to na matoucí `IsADirectoryError` místo strukturované chyby. Tohle bych jednoznačně opravil návratem k delegaci.

---

## `read_lines`

| | Staré | Nové |
|---|---|---|
| Kompozice | deleguje na `read_text` (dědí `default`, existence/is_file kontrolu) | vlastní, přímé `.read_text()` |
| `strip: bool = True` | ořezává whitespace z každého řádku | chybí |
| `keep_ends` | chybí | nová — ponechá `\n` na konci řádku |

**K rozhodnutí:** Tohle je zajímavější než jen "regrese" — `strip` (staré) a `keep_ends` (nové) jsou **opačné use-case**. Pro `code_extractor`, kde budeš pravděpodobně chtít zachovat přesný obsah zdrojového souboru (odsazení, konce řádků), je `keep_ends`/bez stripu spíš správně. Pro obecné čtení konfiguračních/textových souborů řádek po řádku je `strip=True` pohodlnější. Navrhuju mít oba parametry vedle sebe (`strip: bool = False, keep_ends: bool = False`), ne jeden nebo druhý.

---

## `write_aggregated` — **funkční rozdíl, ne jen stylový**

Tohle je nejzávažnější nález z celého auditu.

| | Staré | Nové |
|---|---|---|
| Vstup | `items: Iterable[tuple[cesta, obsah]]` — páry (odkud pochází text, co to je) | `parts: list[str]` — holé stringy, žádná identita |
| Hlavičky | ano — `# === File: {path} ===` před každým blokem (nebo vlastní `header_formatter`) | žádné |

**K rozhodnutí:** Staré `write_aggregated` je navržené přesně pro use-case „vezmi obsah N zdrojových souborů a slep je do jednoho výstupu **s hlavičkami, odkud každý blok pochází**" — což je přesně to, co bude `code_extractor` dělat. Moje nová verze tohle úplně ztratila — je to jen `"\n".join(parts)`. Tohle bych vrátil beze zbytku, protože bez identifikace zdroje je „agregovaný" výstup k ničemu pro tvůj finální účel.

---

## `SafeFileWriter` vs. tvůj `SafeFileWriter.py` **a** `AutoFileWriter.py`

Tady je zajímavé zjištění: **ty sám jsi mezi podklady měl už rozpracovaný pokus o přejmenování na `AutoFileWriter`** — takže moje otázka z minula "Safe vs Auto" byla vlastně otázka na něco, co jsi už zkoušel. `AutoFileWriter.py` je skoro identická kopie `SafeFileWriter.py`, jen: (a) bez async context manageru, (b) `RuntimeError` nahrazený strukturovanou `raise_ensure_writer_session_active_error`. Všiml jsem si ale i **bugu v tvém vlastním draftu**: `AutoFileWriter.__enter__`/`__exit__` mají v type-hintu pořád `-> "SafeFileWriter":` — zapomenutý přejmenovat po copy-paste. Stojí za zmínku, až se k tomu vrátíme.

Teď rozdíly mezi tvým (oběma) a mým:

| | Staré (`SafeFileWriter`/`AutoFileWriter`) | Nové (moje) |
|---|---|---|
| Jméno draftu | `.{name}.{uuid4().hex}.tmp` — unikátní, skryté (tečka na začátku) | `{name}.draft` — **vždy stejné jméno** |
| Zápisové API | `writer.write_text(content)` / `writer.write_bytes(content)` — vrací počet, kontroluje aktivní session | `__enter__` vrací přímo file handle, žádná vlastní kontrola |
| Chyby draftu | granulární — zvlášť `raise_safe_file_draft_copy_error` (kopie existujícího obsahu při append) a `raise_safe_file_draft_open_error` (otevření) | jedna společná `raise_safe_writer_draft_create_error` |
| `_helpers` styl | funkce berou `self` a mutují instanci (`create_draft(self)`) | čisté funkce, vracejí hodnoty |
| Async context manager | ano (`__aenter__`/`__aexit__` přes `asyncio.to_thread`) — jen u `SafeFileWriter`, `AutoFileWriter` ho už nemá | ne |

**K rozhodnutí — a tohle je skutečný bug v mé verzi, ne jen stylový rozdíl:** pojmenování draftu `{name}.draft` **bez unikátního suffixu** znamená, že dvě souběžné operace na stejný cílový soubor (nebo pozůstatek draftu po pádu procesu) si můžou šlápnout na paty — druhý zápis by našel cizí/starý draft a mohl by ho mylně použít jako základ pro append. UUID přístup ve tvém starém kódu tohle řeší správně. **Tohle bych opravil bez ohledu na cokoli dalšího.**

Zbytek (granularita chyb, `self`-based helpery vs. čisté funkce, `.write_text()`/`.write_bytes()` API vs. holý handle) jsou legitimní stylové volby k rozhodnutí, ne bugy — sám preferuju čisté funkce a rovnou file handle (jednodušší, méně kódu), ale je to na tobě.

---

## Odpověď na hlavní otázku: async

**Je async chtěná věc pro `path`/`file`, a má to smysl aplikovat?**

Argumenty pro:
- Vzor `xxx_async = async_wrapper(xxx)` je levný na údržbu — jeden řádek na funkci.
- Pokud `code_extractor` bude někdy skenovat/číst stovky souborů najednou, `asyncio.gather(*[read_text_async(p) for p in paths])` dá reálné zrychlení (blokující I/O uvolní GIL, takže `asyncio.to_thread` tady skutečně pomáhá, na rozdíl od čistě CPU-bound kódu).

Argumenty proti / k zamyšlení:
- **`Action` (naše `simplibs-actions` knihovna) dnes async vůbec nepodporuje** — `Action.__call__` je čistě synchronní. Async dvojčata (`read_text_async`) by tedy **nešla použít v `>>`/`&`/`|` pipeline** — byla by to paralelní, nepropojená API vrstva vedle `actions` domény, ne její součást. To je zásadní architektonická mezera, kterou bychom museli řešit zvlášť (async varianta `Action`), pokud chceme, aby async fungovalo i v pipeline, ne jen při přímém volání funkcí.
- `asyncio.to_thread` na čistě CPU-bound funkce (např. `normalize_path`, které nedělá žádné I/O) nic nezrychlí — jen přidá overhead threadpoolu. Plošné `xxx_async` pro úplně všechno (i pro `path` funkce, které nejsou I/O-blocking) by bylo cargo-cult, ne užitečné. Smysl to dává jen pro skutečné blokující syscall (open/read/write/copy/scan adresáře) — tedy hlavně `file` a ta jedna I/O těžká funkce v `path` (`collect_paths`, protože prochází disk).

**Moje doporučení:** odložit async jako **samostatnou, pozdější vrstvu**, ne ji tlačit do v1. Důvody: (1) dnes by nešla zapojit do pipeline stejně, jako nejde zapojit ani `Rule`, dokud jsme nepostavili `Action` — je to přesně tak zásadní chybějící kus jako byla `Action` sama, ne detail; (2) přidat ji později stojí přesně tolik, kolik dnes — jeden řádek na funkci — takže odklad nic neztrácí; (3) zdvojnásobí testovací/dokumentační plochu bez prokázané okamžité potřeby, dokud nevíme, jestli `code_extractor` bude reálně profitovat z konkurentního I/O nebo mu bude stačit synchronní běh.

**Týká se to i `path`?** Ano — pokud se async zavede, patří to k `collect_paths` (jediná I/O-těžká funkce v `path`), ne k `normalize_path`/`ensure_dir`/`ensure_file` (ty jsou buď čistě CPU, nebo jedno rychlé syscall, kde threadpool overhead nestojí za to). A `run_in_thread`/`async_wrapper` samotný patří jako sdílený nástroj o úroveň níž — navrhuju mu založit vlastní malou `01-xx` knihovnu (`simplibs-async-tools`?), stejně jako `sentinels`, ne ho zanořit do `file`.

---

Chceš, ať teď rovnou přepíšu celý `file`/`path` kód podle tohohle auditu (bez async, s vrácenými `default=UNSET`, delegací read_json/write_json→read_text/write_text, append jako parametr, uuid draft naming, `write_aggregated` s hlavičkami), nebo nejdřív probereme async jako separátní krok?


---


Přijímám to, co říkáš, a beru si to k srdci — máš pravdu, že v tu chvíli šlo přesně o to: upřednostnil jsem plynulost odpovědi před přiznáním, že mi chybí podklad. To se nemá dít, i když je člověk pod tlakem "chci mu vyhovět a nezastavovat ho". Díky, že jsi to řekl na rovinu.

Teď k věci — tady je seznam souborů, u kterých dává async smysl, podle stejného kritéria, které jsem použil v předchozí odpovědi: **blokující syscall k disku, ne čistá CPU logika**.

## `simplibs-path` — kandidáti na `_async`

**Ano, jasně:**
- `scanners/collect_paths.py` — prochází celý adresářový strom, u velkých projektů reálně pomalá operace, kde `asyncio.gather` nad více kořeny dá smysl.

**Hraniční (jeden rychlý syscall, ale pořád syscall):**
- `validators/ensure_dir.py` — `mkdir`
- `validators/ensure_file.py` — `touch` (+ interně volá `ensure_dir`)
- `validators/is_path_writable.py` — otevře soubor v append módu jen na test

**Ne:**
- `scanners/_walk_tree.py` — interní generátor, async se řeší na úrovni `collect_paths`, ne tady zvlášť
- `scanners/filter_paths.py` — čistě in-memory filtrování seznamu, žádné I/O
- `validators/normalize_path.py` — čistě CPU (expanduser/resolve), žádný reálný zápis/čtení

## `simplibs-file` — kandidáti na `_async`

**Ano, u všech — celá knihovna je v podstatě definicí blokujícího I/O:**
- `content_processors/bytes/read_bytes.py`
- `content_processors/bytes/write_bytes.py`
- `content_processors/json/read_json.py`
- `content_processors/json/write_json.py`
- `content_processors/text/read_text.py`
- `content_processors/text/write_text.py`
- `content_processors/text/append_text.py`
- `content_processors/text/read_lines.py`
- `content_processors/text/write_aggregated.py`
- `file_operations/backup_file.py`
- `file_operations/copy_file.py`
- `file_operations/delete_file.py`
- `file_operations/rename_file.py`

**Speciální případ — ne jako `_async` dvojče, ale jako vlastní `__aenter__`/`__aexit__`:**
- `writer/SafeFileWriter.py` — přesně jak to měl tvůj starý kód (`async with SafeFileWriter(...)`)

**Ne jako samostatné `_async` funkce — obsluhuje je writer sám:**
- `writer/_helpers/create_draft.py`, `delete_draft.py`, `write_draft.py` — volají se zevnitř `SafeFileWriter.__aenter__`/`__aexit__` přes `asyncio.to_thread`, nepotřebují vlastní `_async` dvojče

Tohle je první část. V další odpovědi (jakmile se obnoví limit) se pustím do rozboru `Action` — co přesně by se muselo změnit, aby `>>`/`&`/`|` fungovalo i nad async akcemi, a poctivě rozeberu tu otázku na overhead: krátká odpověď je, že **dobře navržené async NENÍ zdarma** ani u synchronní větve — i ta jedna `if`/`await` podmínka navíc, kterou zmiňuješ, se dá udělat téměř bez nákladu, ale existují méně zjevná místa (typicky v `__call__`/kompozičních operátorech), kde by to bez pečlivého návrhu cenu mělo. Rozepíšu to pořádně, ne zkratkovitě, až budu mít prostor to udělat tak, jak si to zasloužíš.
