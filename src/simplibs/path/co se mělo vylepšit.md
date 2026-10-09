# Audit knihovny `simplibs-path`

## 🔴 Chyby, které bych opravil

**1. `collect_paths`: neobyčejné položky obejdou typový filtr (krok 6.2).**
Rozbitý symlink, FIFO nebo socket nejsou `is_file()` ani `is_dir()`. Obě podmínky `continue` se tedy nespustí a položka se přidá do výsledku, i když `collect_files=True, collect_dirs=False`. Stačí obrátit logiku na pozitivní:

```python
if not ((is_file and collect_files) or (is_dir and collect_dirs)):
    continue
```

**2. `is_path_writable` vytváří soubory.**
`open("a")` na neexistující cestě soubor vytvoří a nechá po sobě prázdný soubor. Docstring přitom slibuje kontrolu bez vedlejších efektů. Navíc:
- `normalize_path` se volá mimo `try`, takže funkce může vyhodit `AccessError`, ačkoli má být „without raising".
- Pro adresář vždy vrátí `False`, ale `IsPathWritable` v `expected` hlásí „file path **or directory**".

Návrh sémantiky:
- Existující soubor: `open("a")` (nemění obsah).
- Existující adresář: `os.access(W_OK | X_OK)`.
- Neexistující cesta: sonda v rodiči přes `tempfile.TemporaryFile(dir=parent)`, která nezanechá stopu a je spolehlivější než `os.access`, zvlášť na Windows.

**3. `normalize_path`: neošetřená `ValueError` a prázdný řetězec.**
- Cesta s `\0` vyhazuje `ValueError`, ne `OSError`, a prosákne ven mimo vaše strukturované chyby.
- `""` se tiše změní na aktuální pracovní adresář. `ensure_dir("")` tak „uspěje" a `collect_paths("")` skenuje cwd. To je typická past; vhodné je odmítnout prázdný řetězec typem (např. `str_not_empty` ze `simplibs.types`).

**4. `ignore_dirs` je v rozporu se svým obsahem.**
`walk_tree` ignoruje jen položky, pro které platí `is_dir`. Přitom:
- `.DS_Store` a `Thumbs.db` (IGNORE_SYSTEM) jsou soubory, takže celá skupina je mrtvá.
- `.coverage` (IGNORE_BUILD) je soubor a `.env` (IGNORE_ENV) je typicky soubor.
- `build`, `dist`, `site`, `env` jsou běžné názvy legitimních složek, např. `src/site/`. Výchozí skrývání může tiše vyřadit uživatelův obsah, takže bych je z výchozí sady buď vyřadil, nebo přesunul do volitelné.
- Chybějí věci typu `.eggs`, `.hypothesis`, `.ipynb_checkpoints`, `.gradle`, `$RECYCLE.BIN`, `System Volume Information` (relevantní pro Windows disky).
- Shoda je jen přesným názvem (žádné `*.egg-info`) a rozlišuje velikost písmen.

Rozhodnutí je na tobě: buď ignorování platí i pro soubory (a parametr se přejmenuje na `ignore_names`), nebo se souborové názvy odstraní.

**5. `ignore_dirs` přijme holý `str`.**
`str` je `Iterable[str]`, takže `ignore_dirs=".git"` se tiše změní na množinu znaků `{".", "g", "i", "t"}`. Doporučuji ho explicitně odmítnout. Taky ověřit, že `validate_call` u `Iterable[str]` nespotřebuje generátor, který by někdo předal.

**6. `CollectDirs`/`CollectFiles` nejsou „locked", i když to docstring tvrdí, a pravděpodobně ani nevzniknou.**
- `inspect.signature(partial)` zachová `collect_files`/`collect_dirs` jako klíčové parametry se změněnými defaulty. Vygenerovaný `__init__` je tedy dál nabízí a `CollectDirs(collect_files=True)` předvolbu přepíše.
- V `create_act` krok 8 (`generated_act.__name__ = func.__name__`) by u `functools.partial` měl hodit `AttributeError`, protože `partial` nemá `__name__`. Pokud ti to běží, existuje ošetření, které jsem neviděl. Prosím ověř.
- Čistší řešení je tenká funkce přes `@to_action`, která `collect_paths` volá s pevnými hodnotami a vystaví jen `recursive`, filtry a `ignore_dirs`. Dostaneš skutečný zámek, pravdivý docstring i signaturu.

**7. `walk_tree`: `@validate_call` na rekurzivním interním generátoru.**
Při každém navštíveném adresáři se znovu validují všechny parametry, včetně `set[str]` s ~30 prvky. Pro strom o desítkách tisíc složek je to zbytečná režie na hot path. Argumenty už ověřil `collect_paths`, takže bych dekorátor z interního helperu odstranil (nebo použil vaše bypass).

## 🟠 Chování, které bych zpřesnil

- **`walk_tree` polyká chyby.** Když je nečitelný kořen, výsledkem je tiše prázdný seznam a nejde odlišit „prázdné" od „nečitelné". `try` obalující celý `for` navíc ukončí výpis zbytku adresáře, pokud selže `is_dir()` na jedné položce. Lepší je per-entry `try` a chybu na kořeni povýšit, případně přidat `on_error: Literal["skip", "raise"]`.
- **Výkon.** `iterdir()` + `is_dir()` + `is_symlink()` a pak v `collect_paths` ještě `is_file()` + `is_dir()` jsou ~4–5 syscallů na položku. `os.scandir` vrací `DirEntry` s cachovanými typy (na Windows zdarma). `walk_tree` by mohl vracet i druh položky a `collect_paths` by se nemusel znovu ptát disku.
- **`collect_paths` při `collect_files=False, collect_dirs=False`** vrátí `[]` ještě před kontrolou kořene, takže neexistující kořen se tiše projde. Doporučuji kořen ověřit vždy. Obě `False` bych zvážil jako `ParamError`, protože je to téměř jistě chyba volajícího.
- **`exclude_filter` neořezává podstrom.** Vyřazení složky nevyřadí její obsah, ořezává jen `ignore_dirs`. Je to legitimní, ale je třeba to napsat do dokumentace (a případně nabídnout `prune_filter`).
- **Symlinky.** Symlink na složku se vyhlásí za adresář (`is_dir` ho následuje), ale nerekuruje se do něj. To je dobře, ale nikde to nestojí. Symlink na soubor se sbírá jako soubor.
- **`normalize_path` resolvuje symlinky.** `data -> /mnt/x` se vrátí jako `/mnt/x`. Pro extractor, který chce zachovat cestu „tak jak je", může překvapit. Zvaž `resolve_symlinks: bool = True`.
- **`sorted(results)`** řadí podle částí cesty (strom, ne text) a na Windows bez rozlišení velikosti písmen. Chování je dobré, ale docstring říká „alphabetically".
- **Filtry:** `getattr(x, "is_valid", x)` duplikuje to, co dělá `as_predicate` v actions, jen soukromě. `HasIsValid` by měl být `@runtime_checkable`, pokud ho `validate_call` kontroluje přes `isinstance`. Komentáře u `PathPredicate` jsou česky, zbytek anglicky.
- **`filter_paths`** přijímá jen `Path`, kdežto `collect_paths` `str | Path`. U `FilterPaths` je `rule=None` no-op akce, takže by mohl být povinný. Argument je navíc nejen `Rule`, ale i callable, takže `predicate` by sedělo lépe.
- **Redundance:** `except (PermissionError, OSError)` je všude zbytečně dvojité, protože `PermissionError ⊂ OSError`. U `ensure_dir` může závod (cíl vznikne jako soubor mezi kontrolou a `mkdir`) skončit zavádějící hláškou o oprávněních.
- **Typ cesty:** `str | Path` nepřijme `os.PathLike` (např. `DirEntry`). Jeden sdílený `PathLike` typ by to sjednotil.

## 🟡 Pojmenování a struktura

- Balíček `validators/` obsahuje `normalize_path`, `ensure_dir`, `ensure_file`, které nic neověřují, ale zaručují nebo mutují. Název `ensure/` nebo `guarantors/` by sedělo lépe.
- Chybové helpery mají prefix `raise_ensure_…` i tam, kde žádné `ensure` není (`raise_ensure_normalize_path_error`, `raise_ensure_collect_paths_*`).
- `error_name="PATH_NOT_WRITABLE_ERROR"` má na rozdíl od ostatních (`PATH_IS_NOT_A_FILE`, `FILE_NOT_FOUND`) příponu `_ERROR`.
- Akce jsou PascalCase třídy, kdežto v actions je konvence jinde (např. `guard`, `parallel`). Chci vědět, jestli je to záměr.

## 🟢 Co bych přidal (nepovinné)

- **Rules** pro `include_filter`: `IsFile`, `IsDir`, `PathExists`, `HasSuffix`, `NameMatches` (nabízí se `simplibs-regex`/`patterns`), `IsHidden`, `IsSymlink`, `IsWithin(root)`. Bez nich musí uživatel psát lambdy.
- **Funkce pro extractor:** `ensure_parent_dir` (lehčí než `ensure_file`, file knihovna ho bude potřebovat před zápisem), `rebase_path(path, src_root, dst_root)` pro mapování „odkud kam", `is_within(root, path)` proti path traversal, `unique_path` proti kolizím názvů a `iter_paths` jako líná varianta pro velké stromy.
- **Logování:** `use_logging=True` je výchozí. Chci ověřit, jestli `log_this` zkracuje návratové hodnoty, protože `list[Path]` o desítkách tisíc položek by šlo do logu celý.

## 🧪 Poznámky k testům

Několik věcí se bude testovat jinak než čistá logika, a proto s nimi počítám dopředu:
- Symlinky na Windows vyžadují admin nebo vývojářský režim, takže testy musí mít `skip`, když se symlink nepodaří vytvořit.
- `chmod 000` na Windows nefunguje a pod rootem na Linuxu nic neblokuje, takže testy oprávnění potřebují platformní/root podmínky.
- Všude `tmp_path`, nic mimo něj.

