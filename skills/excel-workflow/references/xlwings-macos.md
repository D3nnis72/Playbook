# Native Excel-Steuerung mit xlwings unter macOS

Diese Referenz gilt, wenn eine bestehende Arbeitsmappe live in Microsoft Excel berechnet, über native Kopierbefehle geändert oder als originales Zellbild (`copy_picture`) exportiert werden muss, oder wenn der Nutzer Excel parallel geöffnet hat.

## 1. Instanz, Hintergrundstart und Dateifreigabe

Sandboxed Microsoft Excel unter macOS zeigt bei direkten Apple-Event-Öffnungen neuer Pfade (`app.books.open()`) häufig `Grant Access`-Dialoge oder holt das Fenster ungewollt in den Vordergrund. Deshalb werden Excel und Arbeitsmappen über Launch Services geöffnet:

```python
from pathlib import Path
import subprocess
import sys
import time
import xlwings as xw

EXCEL = "/Applications/Microsoft Excel.app"
_launched = set()


def attach_or_launch(timeout=60):
    pids = list(xw.apps.keys())
    if len(pids) > 1:
        raise RuntimeError("Mehr als eine Excel-Instanz offen; bitte vor dem Lauf bereinigen")
    if pids:
        return xw.apps[pids[0]], False
    # -g laesst die aktive App vorn, -j startet Excel komplett ausgeblendet
    subprocess.run(["open", "-g", "-j", "-a", EXCEL], check=True)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        pids = list(xw.apps.keys())
        if len(pids) == 1:
            app = xw.apps[pids[0]]
            try:
                len(app.books)
                _launched.add(app.pid)
                return app, True
            except Exception:
                pass
        time.sleep(0.2)
    raise RuntimeError(f"Excel antwortete nicht innerhalb von {timeout} Sekunden")


def open_workbook(app, path: Path, timeout=30):
    path = Path(path).resolve()
    if sys.platform != "darwin":
        return app.books.open(str(path), update_links=False, read_only=False)
    hidden = app.pid in _launched
    flags = ["-g", "-j"] if hidden else ["-g"]
    subprocess.run(["open", *flags, "-a", EXCEL, str(path)], check=True)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for book in app.books:
            if Path(book.fullname).resolve() == path:
                return app.books[path.name]
        time.sleep(0.2)
    hint = " Excel laeuft ausgeblendet; eventuell wartet ein Dialog im Dock-Symbol." if hidden else ""
    raise RuntimeError(f"Excel hat {path} nicht innerhalb von {timeout} Sekunden geoeffnet.{hint}")


def quit_if_idle(app, timeout=20):
    if app.pid not in _launched or len(app.books):
        return False
    pid = app.pid
    app.quit()
    deadline = time.monotonic() + timeout
    while pid in xw.apps.keys():
        if time.monotonic() > deadline:
            raise RuntimeError("Ausgeblendetes Excel hat sich nicht beendet")
        time.sleep(0.2)
    _launched.discard(pid)
    return True
```

Wichtige Regeln für Sitzung und Schließen:
* Hat der Prozess Excel selbst versteckt gestartet (`launched == True`), schließt er am Ende alle selbst geöffneten Mappen und beendet Excel über `quit_if_idle(app)`.
* Lief Excel bereits mit Nutzermappen, bleiben diese Mappen und die Excel-Instanz offen. Nach dem Schließen der eigenen Arbeitsmappe wird die zuvor aktive Nutzermappe nur dann über `previous.api.activate_object()` reaktiviert, wenn durch das Schließen eine andere Mappe aktiv wurde. `book.activate(steal_focus=False)` nicht verwenden, weil es Excel kurz nach vorn holen kann.
* Wenn macOS eine Berechtigung für Automation oder Dateizugriff verlangt, bestätigt der Nutzer den Systemdialog. Keine Umgehungen über TCC-Datenbanken, unsignierte App-Kopien oder Hilfs-Runner bauen.

## 2. Sperren, offene Dateien und Saved-Zustand prüfen

Eine Sperrdatei `~$<Name>.xlsx` bedeutet für sich allein noch keinen Konflikt, weil sie zu genau der Mappe gehören kann, die in der bekannten Excel-Instanz offen ist. Vor jedem Schreibzugriff prüfen:

1. **Aufgelöster Pfad:** In `app.books` über `Path(book.fullname).resolve() == path.resolve()` suchen. Ist dieselbe Datei mehrfach offen, sofort abbrechen.
2. **Sperrdatei zuordnen:** Existiert `path.with_name("~$"+path.name)` und die Datei ist in dieser Excel-Instanz nicht offen, gehört die Sperre einer anderen Sitzung oder ist verwaist. Sofort stoppen und die Sperrdatei niemals löschen.
3. **Schreibschutz und ungespeicherte Arbeit:** Ist die Mappe offen, müssen `not book.api.read_only.get()` und `book.api.saved.get()` gelten (sofern der Projekt-Skill keine explizite Ausnahme für feste Dateien dokumentiert). Den `Saved`-Schalter niemals manuell auf `True` setzen, um eine Prüfung zu umgehen.
4. **Externe Links:** Vor dem Öffnen mit `openpyxl` prüfen, dass `not wb._external_links` gilt, damit Launch Services beim Öffnen keine fremden Arbeitsmappen aktualisiert.

## 3. Gezielte Berechnung statt globaler Umschaltung

Wenn in derselben Excel-Instanz andere Mappen des Nutzers offen sind, darf der globale Berechnungsmodus (`app.calculation`) nicht für einen Probelauf auf automatisch umgestellt werden, weil das Nebenwirkungen und ungespeicherte Zustände in fremden Mappen auslöst.

* Vor Änderungen `(app.screen_updating, app.calculation, app.api.calculate_before_save.get())` erst lesen, sobald mindestens eine Arbeitsmappe geladen ist (ohne offene Mappe liefert Excel keine Berechnungseinstellungen).
* Während der Mutation `app.screen_updating = False` setzen und nur die betroffenen Blätter gezielt berechnen:
  ```python
  book.app.api.calculate(book.sheets[sheet_name].used_range.api)
  ```
* Vor dem finalen `original.save()` etwaige Änderungen an `app.calculation` zurückstellen, damit die Rückstellung das frisch gespeicherte Buch nicht wieder als ungespeichert (`saved == False`) markiert.
* Im `finally`-Block `screen_updating` und, falls noch mindestens eine Mappe offen ist, `calculation` und `calculate_before_save` wiederherstellen. Schlägt die Wiederherstellung oder das Schließen fehl, gilt der Lauf als fehlgeschlagen (`cleanup_errors` / `settings_restore_errors`).

## 4. Live-Werte mit dem gespeicherten Stand vergleichen

Excel gibt Formeln und Datumswerte über `xlwings` leicht anders zurück als `openpyxl` aus dem XML liest:
* Live-Formeltext in Excel lässt Kompatibilitätspräfixe wie `_xlfn.` und `_xlws.` weg. Beim Abgleich zwischen Live-Buch und Datei diese Präfixe auf beiden Seiten normalisieren.
* Excel rundet gebrochene Datums-Seriennummern beim Lesen über die Formel-API minimal. Bei bekannten `datetime`-Zellen eine Toleranz von `abs(float(actual) - to_excel(expected)) <= 1e-9` erlauben.

## 5. Zwischenablage schützen und native PNG-Vorschauen exportieren

Sowohl `Range.copy()` (für Format- oder Zeilenblöcke) als auch `Range.copy_picture()` überschreiben unter macOS die System-Zwischenablage.

* **Zwischenablage sichern:** Wenn in einer Nutzersitzung mit `copy()` oder `copy_picture()` gearbeitet wird, vor dem Kopieren den aktuellen Inhalt und den `changeCount` von `NSPasteboard.generalPasteboard` sichern, nach der Nutzung prüfen, dass der Nutzer nicht parallel etwas Neues kopiert hat, und den alten Inhalt wiederherstellen.
* **Bildschirmaktualisierung für `copy_picture`:** Unter macOS kann `copy_picture(appearance="screen", format="bitmap")` ein komplett weißes Bild liefern, wenn `app.screen_updating == False` steht. Für den Bildexport `book.app.screen_updating = True` vorübergehend einschalten und im `finally` zurücksetzen.
* **Kein Fokus-Diebstahl:** Zellbereiche direkt über `sheet.range((top, left), (bottom, right)).copy_picture(...)` exportieren, ohne vorher das Blatt zu aktivieren oder Zellen zu selektieren.
* **Transiente Fehler und Leertest:** Bei `OSERROR: -50` den Export desselben Bereichs bis zu dreimal mit kurzer Pause (`0.25s`, `0.5s`) wiederholen. Nach dem Zusammenfügen von Kopfzeile und Datenzeile mit `PIL.ImageChops.difference` gegen ein weißes Bild prüfen; ist die Bounding Box `None`, ist das Bild leer und die Sichtprüfung bleibt offen.
* **Durchgestrichene Werte im manuellen Modus:** Steht Excel auf manueller Berechnung, zeigt Excel nicht neu berechnete Formelzellen im Bild durchgestrichen an (Stale-Value-Formatting). Vor dem Bildexport einer wieder geöffneten Probe die betroffenen Blätter gezielt berechnen.
