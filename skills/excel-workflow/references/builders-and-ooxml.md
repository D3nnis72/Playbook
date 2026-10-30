# Workbooks ohne laufendes Excel bauen, prüfen und über OOXML ergänzen

Diese Referenz gilt für das Prüfen und Ändern von Arbeitsmappen mit `openpyxl` oder direktem OOXML-Zugriff sowie für das Erzeugen neuer Arbeitsmappen mit `@oai/artifact-tool` in der Codex-Laufzeit.

## 1. `openpyxl`: Zwei-Pass-Lesen und sichere Änderungen

`openpyxl` wertet niemals Formeln aus und trennt beim Laden zwischen Formeltext und gecachtem Wert:

* **`data_only=False` (Standard):** Liefert die Formelstrings (`=SUM(B2:B10)`), aber keine berechneten Ergebnisse. Nur dieser Modus darf zum Bearbeiten und Speichern verwendet werden.
* **`data_only=True`:** Liefert die zuletzt von Excel oder einem Recalc-Lauf gespeicherten Werte, verwirft aber alle Formeln. **Eine mit `data_only=True` geöffnete Arbeitsmappe niemals speichern**, sonst sind sämtliche Formeln dauerhaft durch Festwerte überschrieben.
* **Frisch geschriebene Formeln:** Schreibt `openpyxl` eine neue Formel in eine Zelle, ist ihr gecachter Wert beim anschließenden Lesen mit `data_only=True` `None`, bis Excel, LibreOffice oder `@oai/artifact-tool` die Mappe neu berechnet hat.
* **Verbunde (`MergedCell`):** Immer nur die linke obere Ankerzelle beschreiben; alle übrigen Zellen des Verbunds sind schreibgeschützt.
* **Tabellennamen mit Leerzeichen in Formeln:** In Blattverweisen immer in einfache Anführungszeichen setzen (`='Article check'!$A$8:$A$200`), sonst entsteht `#VALUE!`.
* **Fensterfixierung (`freeze_panes`) vergleichen:** Beim Vorher-Nachher-Vergleich nur `(view.workbookViewId, view.pane.state, view.pane.xSplit, view.pane.ySplit)` prüfen. `topLeftCell` ist lediglich die aktuelle Scrollposition und darf nach nativen Operationen abweichen.

## 2. Direkte OOXML-Eingriffe im `.xlsx`-ZIP

Ein `.xlsx` ist ein ZIP-Archiv aus XML-Dateien. Ein kompletter Parse-und-Serialize-Durchlauf eines Arbeitsblatts mit `xml.etree.ElementTree` kann jedoch Namespace-Deklarationen entfernen oder umbenennen, die nur als Präfix in Attributwerten wie `mc:Ignorable="x14ac xr xr2 xr3"` oder `mc:Choice Requires="..."` vorkommen. `openpyxl` liest eine solche Datei oft klaglos ein, während Microsoft Excel beim Öffnen eine Reparaturwarnung zeigt.

Deshalb gelten für direkte XML-Änderungen drei Regeln:
1. Direkte XML-Bearbeitung im ZIP nur einsetzen, wenn die Ziel-API die Funktion nicht beherrscht (zum Beispiel native relative Datei-Hyperlinks nach einem `@oai/artifact-tool`-Export).
2. Falls nach einer freien XML-Bearbeitung Microsoft Excel verfügbar ist, die Datei in Excel öffnen, sicherstellen, dass keine Reparaturwarnung erscheint, neu berechnen und speichern. Ist kein Excel verfügbar, diese Prüfgrenze offen im Bericht nennen.
3. Für relative Hyperlinks im Worksheet-XML die Standard-Namespaces registrieren und das `<hyperlinks>`-Element exakt an der vom OOXML-Schema verlangten Position vor `printOptions`, `pageMargins`, `pageSetup` oder `tableParts` einfügen:

```python
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

SHEET = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

AFTER_HYPERLINKS = {
    "printOptions", "pageMargins", "pageSetup", "headerFooter",
    "rowBreaks", "colBreaks", "customProperties", "cellWatches",
    "ignoredErrors", "smartTags", "drawing", "legacyDrawing",
    "legacyDrawingHF", "picture", "oleObjects", "controls",
    "webPublishItems", "tableParts", "extLst",
}


def attach_relative_hyperlinks(xlsx_path: Path, sheet_xml: str, links_spec: list[tuple[str, str]]) -> None:
    """Attach (cell_ref, relative_target) hyperlinks to sheet_xml inside xlsx_path."""
    ET.register_namespace("", SHEET)
    ET.register_namespace("r", OFFICE)
    sheet_path = f"xl/worksheets/{sheet_xml}"
    rel_path = f"xl/worksheets/_rels/{sheet_xml}.rels"

    with zipfile.ZipFile(xlsx_path) as source:
        sheet = ET.fromstring(source.read(sheet_path))
        rels = (
            ET.fromstring(source.read(rel_path))
            if rel_path in source.namelist()
            else ET.Element(f"{{{REL}}}Relationships")
        )
        links = ET.Element(f"{{{SHEET}}}hyperlinks")
        used_ids = {r.get("Id") for r in rels}
        for cell_ref, target in links_spec:
            assert not target.startswith("/") and ".." not in target, f"Unsicherer relativer Pfad: {target}"
            rid = f"rIdLink_{cell_ref}"
            assert rid not in used_ids
            used_ids.add(rid)
            ET.SubElement(links, f"{{{SHEET}}}hyperlink", {"ref": cell_ref, f"{{{OFFICE}}}id": rid})
            ET.SubElement(
                rels,
                f"{{{REL}}}Relationship",
                {"Id": rid, "Type": f"{OFFICE}/hyperlink", "Target": target, "TargetMode": "External"},
            )
        insert_idx = next(
            (i for i, child in enumerate(sheet) if child.tag.split("}")[-1] in AFTER_HYPERLINKS),
            len(sheet),
        )
        sheet.insert(insert_idx, links)
        replacements = {
            sheet_path: ET.tostring(sheet, encoding="utf-8", xml_declaration=True),
            rel_path: ET.tostring(rels, encoding="utf-8", xml_declaration=True),
        }
        with tempfile.NamedTemporaryFile(dir=xlsx_path.parent, suffix=".xlsx", delete=False) as fh:
            temp = Path(fh.name)
        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED) as output:
            for entry in source.infolist():
                output.writestr(entry, replacements.pop(entry.filename, source.read(entry.filename)))
            for name, value in replacements.items():
                output.writestr(name, value)
    temp.replace(xlsx_path)
```

## 3. Arbeitsmappen in der Codex-Laufzeit mit `@oai/artifact-tool` bauen

Wenn in der Codex-Laufzeit eine Arbeitsmappe neu aufgebaut wird, bietet `@oai/artifact-tool` eine eigene Berechnungs- und Render-Engine ohne laufendes Desktop-Excel. Damit der Build sicher und reproduzierbar bleibt, dieses Muster einhalten:

1. **Quell- und Ziel-Fingerprints vor dem Lauf sichern:**
   SHA-256 der Eingabedaten, der bisherigen Quell-Arbeitsmappe (falls daraus manuelle Spalten übernommen werden) und der Zieldatei vor dem Lauf bestimmen.
2. **Manuelle Review-Spalten vor dem Neubau einlesen:**
   Über `scripts/xlsx_stream.py inputs` (oder `read_keyed_inputs`) bestehende Dropdown-Entscheidungen, Freigaben und Freitextnotizen anhand stabiler fachlicher Schlüssel (zum Beispiel Lieferantennummer oder Artikel-ID) aus der bestehenden Datei auslesen und in die neuen Zeilen mischen.
3. **Berechnen und auf Formel-Fehler prüfen:**
   ```javascript
   wb.recalculate();
   const errors = await wb.inspect({
     kind: 'match',
     searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
     options: { useRegex: true, maxResults: 100 },
     maxChars: 2500,
   });
   if (errors.ndjson.includes('"match"')) {
     throw new Error(`Formula errors: ${errors.ndjson.slice(0, 500)}`);
   }
   ```
4. **Summenabgleich und Live-Formel-Probe:**
   * Berechnete Summenzellen in der Tabelle und auf dem Overview-Blatt gegen die Summe der Eingabedaten prüfen (`Math.abs(shown - expected) <= 0.01`).
   * **Live-Probe:** Eine Eingabezelle (etwa einen Betrag oder ein Review-Dropdown) im Speicher kurz ändern, `wb.recalculate()` aufrufen, prüfen, dass sich die abhängige Summe oder der `COUNTIFS`-Zähler um genau das erwartete Delta bewegt, den Originalwert wieder eintragen, erneut `wb.recalculate()` rufen und die vollständige Wiederherstellung bestätigen.
5. **PNG-Vorschauen rendern und wirklich ansehen:**
   Relevante Ausschnitte (Kopf, linke und rechte Spalten, Summenzeile, Guide/Overview) mit `await wb.render({ sheetName, range, scale: 1.2, format: 'png' })` in ein Arbeitsverzeichnis schreiben und die erzeugten PNG-Dateien zur Sichtprüfung öffnen.
6. **Gestuft speichern und Artefakte aufräumen:**
   * Zuerst in ein Arbeitsverzeichnis exportieren (`await out.save(stagingTarget)`).
   * Falls `@oai/artifact-tool` eine `${target}.inspect.ndjson` neben der Datei abgelegt hat, diese sofort mit `await fs.rm(`${target}.inspect.ndjson`, { force: true })` löschen, damit keine Prüf-Logs im Lieferordner landen.
   * Falls nötig, relative Hyperlinks auf `stagingTarget` ergänzen.
   * Direkt vor `fs.copyFile(stagingTarget, deliverable)` prüfen, dass sich die SHA-256-Hashes von Eingabedaten, Quell-Workbook und Ziel-Workbook während des Laufs nicht verändert haben, damit keine parallelen Änderungen überschrieben werden.

## 4. Unabhängige OOXML-Rekonzilierung nach einem Rebuild

Nach einem Neubau oder einer größeren Änderung sollte ein kurzes Prüfskript Vorher- und Nachher-Datei direkt auf OOXML-Ebene (`zipfile` + `xml.etree.ElementTree`) vergleichen:
* Stimmen die Schlüssel-Mengen (`set(old_keys) == set(new_keys)`) und die Zeilenzahlen pro Blatt?
* Wurden alle nicht zur Änderung beauftragten Felder und alle manuellen Review-Spalten pro Schlüssel exakt erhalten?
* Sind `dataValidations`, `conditionalFormatting` (mit aufgelösten `dxfId`-Stilen statt volatiler Indexnummern), `sheetViews`, `tableParts` und `hyperlinks` (mit aufgelösten `_rels`-Zielen) vollständig vorhanden?
