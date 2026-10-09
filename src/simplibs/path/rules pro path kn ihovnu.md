Jasně, navazuju. 🙂 Rule.py a README k pravidlům jsem si mezitím načetl, takže už vím, jak přesně vypadá kontrakt (`describe()` je metoda, výchozí je název třídy, nesmí vyhodit výjimku) a které presety existují (`StartsWith`, `EndsWith`, `Regex`, `Equals`, `InRange`, `HasLength`, ...).

## 🐍 Python 3.11, nebo 3.12+?

**Doporučuji zůstat na 3.11+**, a to pro celý ekosystém, ne jen pro `path`.

- **Důvod pro změnu v zásadě není.** `Path.walk()` (3.12+) je tenká vrstva nad `os.walk`/`os.scandir` a nic nezrychlí. Pro náš `walk_tree` je `os.scandir` lepší: dává cachované typy položek a ošetření chyb po jedné položce, což `Path.walk` nenabízí.
- **Konzistence.** `build_typing_rule` má v design notes výslovně cíl 3.11+. Zvednout jen jednu knihovnu by znamenalo, že extractor vyžaduje 3.12, ale `rules`/`validate` běží na 3.11.
- **Dosah.** 3.11 má podporu do října 2027, takže je to stále rozumná spodní hranice (3.10 končí právě teď).
- **Doporučení pro CI:** `requires-python = ">=3.11"` a testovat na nejnovějších verzích, které existují. Až se 3.11 bude blížit konci, přejdi ekosystémem najednou, ne knihovnu po knihovně.

Související věc stranou: uživatelé na 3.12+ mohou psát `type X = ...` aliasy. `build_typing_rule` je dnes odmítne jako nepodporované (`TypeAliasType` nemá origin, není `type` a nemá `__supertype__`). Nesouvisí to s `path`, ale stojí za to si to poznamenat pro `rules`.

## 🧩 Dělat pravidla pro `path`? Ano, ale střídmě

Rule tu nepřidává novou logiku, ta zůstává v čistých funkcích a pravidlo je tenká vrstva (stejně jako dnešní `IsPathWritable`). Přidaná hodnota je ve třech místech, kde se pravidla opravdu použijí:

1. **Anotace s `validate_call`.** `ExistingDir = validated_type(Path, IsDir())` a funkce dostane kontrolu vstupu s hotovou chybovou kartou.
2. **Filtry.** `include_filter=HasSuffix(".py") & ~IsHidden()` je skládatelné a díky `describe()` čitelné i v logu: `suffix .py & not hidden`. Lambda tohle neumí a nejde ani serializovat, což se může hodit u `simplibs-serialize` a u deklarativní konfigurace extractoru.
3. **Brány v pipeline.** `IsDir() >> CollectFiles() >> FilterPaths(rule=...)`. Reflektované operátory z `Action` dělají z pravidla krok `guard`, který pustí data dál beze změny, nebo vyhodí kartu pravidla. Pro extractor („co, odkud, kam") je to přesně ten vláček procesů, o kterém mluvíš.

**Kritérium, které navrhuji:** pravidlo vznikne, jen pokud je to čistý predikát bez vedlejších efektů, použitelný alespoň ve dvou ze tří míst výše, a pokud má smysluplnou chybovou kartu. Mutace (`ensure_*`, `normalize_path`) pravidla nedostanou, ty zůstávají akcemi.

**Navržená sada (~12 pravidel), rozdělená podle toho, jestli sahají na disk:**

| Skupina | Pravidla | Poznámka |
|---|---|---|
| **Lexikální** (bez I/O, levné, vhodné do filtrů) | `HasSuffix(*suffixes, ignore_case=True)`, `NameIs(rule)`, `StemIs(rule)`, `IsAbsolutePath`, `IsRelativePath`, `IsHidden` (podle názvu), `IsWithin(root)`, `IsValidFilename` | `NameIs`/`StemIs` jsou „čočky": převedou část cesty na `str` a předají ji existujícímu presetu (`StartsWith`, `Regex`, `Equals`, ...), takže nic nepřepisujeme. `IsWithin` je klíčové pro ochranu proti path traversal při zápisu výstupů. `IsValidFilename` kontroluje zakázané znaky, rezervované názvy Windows (`CON`, `NUL`), koncové tečky/mezery a délku. |
| **Souborový systém** (sahají na disk) | `PathExists`, `IsFile`, `IsDir`, `IsSymlink`, `IsPathWritable` (už existuje), `IsPathReadable` | Kontrakt `Rule` říká, že `is_valid` nesmí vyhazovat. Chyby `OSError`/`ValueError` se tedy mapují na `False`. |

**Odložil bych:** pravidla na velikost a čas změny (`HasSize(rule)` jako čočka nad `InRange`/`LessOrEqual`) až do file knihovny, kde dávají větší smysl, a detekci textového/binárního obsahu, která patří také tam.

**Dvě upozornění k návrhu:**
- **TOCTOU.** „Existuje" ve chvíli validace neznamená „bude existovat při použití". Je to fail-fast s dobrou hláškou, ne záruka, a dokumentace to musí říct.
- **Co se považuje za cestu.** Pravidla se vyhodnocují před `normalize_path`, takže `~/proj` by bez expanze selhalo. Navrhuji lehkou konverzi `Path(value).expanduser()` bez `resolve()` (žádné syscally navíc), takže pravidla jsou konzistentní s funkcemi, ale použitelná i ve filtrech nad tisíci položek. Dnešní `IsPathWritable` normalizuje plně; sjednotím to.

**Překryv s `raise_*` helpery** (`StateError`, `NotFoundError`) je malý a záměrný: pravidla popisují *validaci vstupu*, helpery *selhání operace*. Ponechal bych je oddělené.

Pokud ti tahle sada sedí (případně něco škrtni nebo přidej), v další zprávě navrhnu kompletní strukturu složek a souborů pro `path` včetně nových `rules/` a přejmenované složky, a pak ji začneme plnit kódem. Sedí ti ta sada pravidel?