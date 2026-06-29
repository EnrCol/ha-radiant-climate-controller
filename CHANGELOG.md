# Changelog

## [0.3.8] - 2026-06-29

### Documentation

- README aggiornato con stato attuale e sviluppo previsto.
- Documenti aggiornati: architecture, entities, esphome-adapter, system-model, design-principles.
- Aggiunto docs/future-development.md.

### Notes

Aggiornamento documentale. La logica runtime resta quella della v0.3.7.

## [0.3.7] - 2026-06-29

### Changed

- Disattivato il recupero anticipato basato sul trend.
- Il recupero entra solo quando la temperatura supera la soglia reale di recupero.
- Restano attivi normale anticipato e spinto anticipato.

### Notes

Questa versione riduce i passaggi rapidi tra recupero anticipato e spinto quando la temperatura e quasi stabile.

## [0.3.6] - 2026-06-29

### Changed

- Stanza piu vicina alla rugiada ora e diagnostica e disabilitata di default.
- Zona piu vicina alla rugiada ora e diagnostica e disabilitata di default.

### Notes

Le entita gia create da Home Assistant possono restare attive nel registro entita. In quel caso vanno disattivate manualmente una sola volta.

## [0.3.5] - 2026-06-29

### Changed

- Aggiunta stabilizzazione della stanza piu calda con delta minimo di 0.2 C prima di cambiare stanza visualizzata.
- Resi piu stabili i testi di motivo target e motivo azione usando descrizioni del trend meno variabili.
- Campioni trend temperatura ora e una entita diagnostica disabilitata di default.

### Notes

La temperatura massima casa resta sempre il massimo reale tra le stanze. La stanza piu calda visualizzata invece viene stabilizzata per evitare oscillazioni tra stanze quasi uguali.

## [0.3.4] - 2026-06-28

### Fixed

- Aggiunti i nomi mancanti per i nuovi sensori trend.
- Migliorata la leggibilita dei nomi mostrati da Home Assistant.

## [0.3.3] - 2026-06-28

### Added

- Aggiunta state machine con memoria dello stato radiante precedente.
- Aggiunta isteresi fissa di 0.3 C per uscire dagli stati normale, spinto e recupero.

### Changed

- Il trend positivo continua ad anticipare gli stati piu forti.
- Il trend negativo non forza l uscita immediata da uno stato alto.
- La centralina resta nello stato precedente finche la temperatura non scende sotto la soglia di uscita.

## [0.3.2] - 2026-06-28

### Fixed

- Refresh immediato quando cambiano le entita sorgente della centralina.
- Le temperature stanza, umidita, rugiada, standby, ACS e richiesta deumidifica forzano il ricalcolo del coordinator.
- Corretto il caso in cui temperatura massima casa, stanza piu calda e trend restavano fermi per ore.

## [0.3.1] - 2026-06-27

### Added

- Trend temperatura filtrati a 15, 30 e 60 minuti.
- Sensori per fonte trend usata e numero campioni trend.

### Changed

- La logica predittiva usa il trend 30 minuti quando disponibile.
- Se il trend 30 minuti non e disponibile, usa il trend 15 minuti.
- Rimosso il trend istantaneo a breve intervallo.

## [0.3.0] - 2026-06-27

### Added

- Entita number per soglie, anticipi, trend minimi, target e margine rugiada.
- Entita select per stato manuale.
- Salvataggio opzioni da UI.

## [0.2.1] - 2026-06-27

### Changed

- Rinominata la logica osservatore rugiada.
- Aggiunta azione raffrescamento_attivo.
- Migliorati i testi motivo target e motivo azione.
- Aggiunto workflow GitHub Actions per validazione HACS.
- Aggiunto logo SVG nel README.

## [0.2.0] - 2026-06-27

### Added

- Modello stanze reale.
- Zone deumidifica giorno/notte.
- Sensori predittivi principali.

## [0.1.0] - 2026-06-27

### Added

- Scaffold iniziale custom integration.
- Config flow.
- Sensori base temperatura, umidita, rugiada e target.
