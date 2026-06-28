# Changelog

## [0.3.4] - 2026-06-28

### Fixed

- Aggiunti i nomi mancanti per i nuovi sensori trend.
- Migliorata la leggibilita dei nomi mostrati da Home Assistant.

### Notes

Dopo aggiornamento e riavvio, i nomi visualizzati dovrebbero essere corretti. Gli entity_id gia generati da Home Assistant potrebbero restare invariati e vanno rinominati manualmente se necessario.

## [0.3.3] - 2026-06-28

### Added

- Aggiunta state machine con memoria dello stato radiante precedente.
- Aggiunta isteresi fissa di 0.3 C per uscire dagli stati normale, spinto e recupero.

### Changed

- Il trend positivo continua ad anticipare gli stati piu forti.
- Il trend negativo non forza l uscita immediata da uno stato alto.
- La centralina resta nello stato precedente finche la temperatura non scende sotto la soglia di uscita.

### Notes

Questa versione stabilizza lo stato radiante prima del futuro collegamento a ESPHome.

## [0.3.2] - 2026-06-28

### Fixed

- Aggiunto refresh immediato quando cambiano le entita sorgente della centralina.
- Le temperature stanza, umidita, rugiada, standby, ACS e richiesta deumidifica ora forzano il ricalcolo del coordinator.
- Corretto il caso in cui temperatura massima casa, stanza piu calda e trend restavano fermi per ore.

### Notes

Il polling resta attivo ogni 30 secondi, ma ora non e piu l unico meccanismo di aggiornamento.

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

- Aggiunte entita number per configurare da UI:
  - soglie stato normale/spinto/recupero;
  - soglie anticipo normale/spinto/recupero;
  - trend minimo normale/spinto/recupero;
  - target mandata mantenimento/normale/spinto/recupero;
  - margine punto rugiada.
- Aggiunta entita select per forzare manualmente lo stato radiante:
  - auto;
  - mantenimento;
  - normale;
  - spinto;
  - recupero.
- I valori modificati da UI vengono salvati nelle opzioni della config entry.

### Changed

- Il coordinator usa i parametri configurati da UI invece dei soli default hardcoded.
- hacs.json resta compatibile con lo schema HACS corrente.

### Notes

La centralina resta osservativa: la v0.3 non comanda ancora ESPHome, termostati, testine o deumidificatori.

## [0.2.1] - 2026-06-27

### Changed

- Rinominata la logica osservatore rugiada: la stanza mostrata e ora la piu vicina alla rugiada, non necessariamente critica.
- Aggiunta azione raffrescamento_attivo per distinguere il recupero reale dall anticipo predittivo.
- anticipo_raffrescamento resta usato solo quando la soglia viene anticipata grazie al trend.
- Migliorati i testi di motivo target e motivo azione quando il trend non e ancora disponibile.
- Aggiunto workflow GitHub Actions per validazione HACS.
- Aggiunto logo SVG nel README.

### Notes

Questa versione resta osservativa: non comanda ancora ESPHome, termostati, testine o deumidificatori.

## [0.2.0] - 2026-06-27

### Added

- Modello stanze reale per l impianto di Enrico.
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
