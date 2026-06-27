# Release process

## Versioning

Il progetto usa SemVer:

```text
MAJOR.MINOR.PATCH
```

Regole pratiche:

- `PATCH`: fix, rinomina sensori, testi, piccoli aggiustamenti compatibili.
- `MINOR`: nuovi sensori, nuova logica, nuove entità, compatibile con configurazione esistente.
- `MAJOR`: cambi incompatibili o migrazione necessaria.

## Procedura release HACS

1. Aggiornare `custom_components/radiant_climate_controller/manifest.json`:

```json
"version": "0.2.1"
```

2. Aggiornare `CHANGELOG.md`.

3. Fare commit e push.

4. Creare una GitHub Release:

```text
Tag: v0.2.1
Title: v0.2.1
```

5. Copiare nella descrizione della release la sezione corrispondente del changelog.

6. In Home Assistant / HACS:

```text
HACS → Radiant Climate Controller → Check for updates
```

oppure attendere la scansione automatica.

## Nota importante

HACS mostra aggiornamenti in modo più pulito quando esiste una GitHub Release.

Il tag deve essere coerente con il campo `version` del manifest:

```text
manifest version: 0.2.1
release tag: v0.2.1
```
