# Modello impianto

## Stanze considerate

La centralina deve considerare tutte le stanze servite dal radiante:

- soggiorno
- cucina
- bagno
- studio
- camera
- camera Ricky

## Sensori umidità da tenere come riferimento

```text
sensor.umidita_media_zona_giorno
sensor.umidita_media_zona_notte
sensor.umidita_soggiorno
sensor.umidita_cucina
sensor.umidita_bagno
sensor.umidita_studio
sensor.umidita_camera
sensor.umidita_camera_ricky
```

## Zone deumidificazione

### Zona giorno

Servita da un deumidificatore idronico dedicato.

Stanze:

- soggiorno
- cucina

### Zona notte

Servita da un secondo deumidificatore idronico.

Stanze:

- bagno
- studio
- camera
- camera Ricky

## Principio di controllo

La temperatura più alta tra le stanze guida la richiesta di raffrescamento.

La stanza più vicina alla rugiada guida la sicurezza.

La media è utile per statistiche e comfort generale, ma non deve nascondere il locale peggiore.
