# Changelog

## [0.2.1] - 2026-06-27

### Changed

- Rinominata la logica osservatore rugiada: la stanza mostrata è ora la più vicina alla rugiada, non necessariamente critica.
- Aggiunta azione `raffrescamento_attivo` per distinguere il recupero reale dall'anticipo predittivo.
- `anticipo_raffrescamento` resta usato solo quando la soglia viene anticipata grazie al trend.
- Migliorati i testi di motivo target e motivo azione quando il trend non è ancora disponibile.
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
  - stanza più calda;
  - trend temperatura casa;
  - punto rugiada massimo casa;
  - stanza più vicina alla rugiada;
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
- Sensori base temperatura/umidità/rugiada/target.
