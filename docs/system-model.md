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

## Stato attuale impianto

La PDC entra in chiamata dal primo termostato che richiede climatizzazione.

Il termostato che chiama:

1. apre le testine della propria zona;
2. abilita il circuito radiante della stanza/zona;
3. fa partire la pompa di ricircolo posizionata appena sopra la valvola miscelatrice.

Attualmente i termostati vengono lasciati con target difficili da raggiungere, così il pavimento può lavorare quasi in continuo.

## Storico funzionamento

Negli anni precedenti il pavimento lavorava con mandata fissa regolata manualmente tra 18°C e 19°C dall'integrazione della PDC.

Questa scelta era necessaria perché non erano ancora installati i deumidificatori idronici.

## Nuova architettura con deumidificatori

I deumidificatori idronici consigliano acqua a circa 16°C.

Per questo è stata installata una valvola miscelatrice sul circuito pavimento:

```text
PDC / deumidificatori: circa 16°C
valvola miscelatrice: miscela acqua fredda e ritorno
pavimento radiante: target variabile circa 18-20°C
```

La valvola miscelatrice serve quindi a separare due esigenze diverse:

- deumidificatori: acqua più fredda;
- pavimento: acqua più alta e sicura contro condensa.

## Principio di controllo

La temperatura più alta tra le stanze guida la richiesta di raffrescamento.

La stanza più vicina alla rugiada guida la sicurezza.

La media è utile per statistiche e comfort generale, ma non deve nascondere il locale peggiore.

## Ruolo della futura centralina

La centralina non deve sostituire subito tutta la logica esistente.

Prima deve osservare e calcolare:

- stanza più calda;
- stanza più umida;
- stanza più vicina alla rugiada;
- zona deumidifica interessata;
- target mandata pavimento consigliato;
- eventuale azione locale suggerita su testina/termostato.

Solo dopo potrà comandare direttamente target, deumidifica, testine o termostati.
