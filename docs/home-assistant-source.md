# Sorgente Home Assistant

## Package reale da analizzare

Il package climatizzazione attuale della casa si trova in Home Assistant in:

```text
/homeassistant/packages/climatizzazione/
```

Nella repo GitHub `EnrCol/home-assistant-config` il path atteso è:

```text
packages/climatizzazione/
```

La cartella contiene circa 14 file YAML, non tutti attualmente in uso.

## Obiettivo analisi

La centralina deve leggere e comprendere questi elementi dalla configurazione esistente:

- termostati ambiente;
- testine/attuatori zona;
- pompa ricircolo pavimento sopra la valvola miscelatrice;
- logica chiamata PDC;
- logica deumidificatori idronici giorno/notte;
- sensori umidità;
- sensori punto rugiada;
- sensori comfort già presenti;
- entità di consenso climatizzazione;
- eventuali blocchi sicurezza già esistenti.

## Nota

Non tutti i file nella cartella sono necessariamente attivi. L'analisi deve distinguere tra:

- file realmente inclusi/usati;
- file storici;
- file sperimentali;
- file da ignorare.

## Primo step operativo

Ottenere l'elenco dei file presenti in:

```bash
find /homeassistant/packages/climatizzazione -maxdepth 1 -type f | sort
```

oppure dalla repo:

```bash
git ls-tree -r --name-only HEAD packages/climatizzazione
```
