# Changelog

## [0.3.1] - 2026-06-27

### Added

- Aggiunti trend temperatura filtrati:
  - 15 minuti;
  - 30 minuti;
  - 60 minuti.
- Aggiunti sensori per fonte trend usata e numero campioni trend.

### Changed

- La logica predittiva usa il trend 30 minuti quando disponibile.
- Se il trend 30 minuti non e ancora disponibile, usa il trend 15 minuti.
- Rimosso il trend istantaneo a breve intervallo per ridurre rumore e falsi anticipi.

### Notes

I trend sono ancora calcolati in memoria. Dopo riavvio o reload integrazione servono circa 15 minuti per il primo trend utile e circa 30 minuti per il trend principale.

## [0.3.0] - 2026-06-27

### Added

- Aggiunte entita `number` per configurare da UI:
  - soglie stato normale/spinto/recupero;
  - soglie anticipo normale/spinto/recupero;
  - trend minimo normale/spinto/recupero;
  - target mandata mantenimento/normale/spinto/recupero;
  - margine punto rugiada.
- Aggiunta entita `select` per forzare manualmente lo stato radiante:
  - auto;
  - mantenimento;
  - normale;
  - spinto;
  - recupero.
- I valori modificati da UI vengono salvati nelle opzioni della config entry.

### Changed

- Il coordinator usa i parametri configurati da UI invece dei soli default hardcoded.
- `hacs.json` dichiara anche i domini `number` e `select`.

### Notes

La centralina resta osservativa: la v0.3 non comanda ancora ESPHome, termostati, testine o deumidificatori.

## [0.2.1] - 2026-06-27

### Changed

- Rinominata la logica osservatore rugiada: la stanza mostrata e ora la piu vicina alla rugiada, non necessariamente critica.
- Aggiunta azione `raffrescamento_attivo` per distinguere il recupero reale dall'anticipo predittivo.
- `anticipo_raffrescamento` resta usato solo quando la soglia viene anticipata grazie al trend.
- Migliorati i testi di motivo target e motivo azione quando il trend non e ancora disponibile.
- Aggiunto workflow GitHub Actions per validazione HACS.
- Aggiunto logo SVG nel README.

### Notes

Questa versione resta osservativa: non comanda ancora ESPHome, termostati, testine o deumidificatori.

## [0.2.0] - 2026-06-27

### Added

- Modello stanze reale per l'impianto di Enrico.
- Zone deumidifica giorno/notte.
- Sensori predittivi:
  - temperatura massima casa;
  - stanza piu calda;
  - trend temperatura casa;
  - punto rugiada massimo casa;
  - stanza piu vicina alla rugiada;
  - target mandata comfort;
  - target mandata sicuro;
  - target mandata consigliato;
  - azione consigliata;
  - motivo target;
  - motivo azione.

## [0.1.0] - 2026-06-27

### Added

- Scaffold iniziale custom integration.
- Config flow.
- Sensori base temperatura/umidita/rugiada/target.
