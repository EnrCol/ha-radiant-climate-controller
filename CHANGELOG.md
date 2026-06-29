# Changelog

## [0.4.0] - 2026-06-29

### Added

- Added target commandable binary sensor.
- Added target commandable reason sensor.
- Added binary sensor platform.
- Updated ESPHome and entity documentation.

### Notes

This release prepares ESPHome integration but does not command the PID yet.

## [0.3.8] - 2026-06-29

### Documentation

- README aggiornato con stato attuale e sviluppo previsto.
- Documenti aggiornati: architecture, entities, esphome-adapter, system-model, design-principles.
- Aggiunto docs/future-development.md.

## [0.3.7] - 2026-06-29

### Changed

- Disattivato il recupero anticipato basato sul trend.
- Il recupero entra solo quando la temperatura supera la soglia reale di recupero.
- Restano attivi normale anticipato e spinto anticipato.
