# Strategia punto rugiada

## Obiettivo

Nel raffrescamento radiante la sicurezza condensa non deve essere gestita solo alzando sempre la mandata globale.

La centralina deve distinguere tra:

- rischio diffuso su più stanze;
- rischio localizzato su una sola stanza;
- rischio in zona giorno;
- rischio in zona notte.

## Strategia preferita

### 1. Avvicinamento alla rugiada

Se una stanza si avvicina alla rugiada ma non è ancora in rischio grave:

1. aumentare richiesta deumidificazione della zona corretta;
2. mantenere target mandata se ancora sicuro;
3. segnalare la stanza critica.

### 2. Rischio localizzato

Se una sola stanza è in rischio condensa, la prima azione preferita può essere chiudere la testina radiante della stanza interessata tramite il relativo termostato/attuatore.

Questo evita di penalizzare tutta la casa alzando subito la mandata globale.

### 3. Rischio di zona

Se più stanze della stessa zona sono a rischio:

- forzare o aumentare la deumidificazione della zona;
- valutare chiusura delle testine più critiche;
- alzare il target mandata solo se il rischio resta.

### 4. Rischio diffuso

Se il rischio rugiada è presente in più zone o non ci sono testine controllabili:

```text
target_finale = max(target_richiesto, punto_rugiada_massimo + margine)
```

## Nota progettuale

Alzare la mandata globale è la protezione più semplice, ma non sempre la più intelligente.

La centralina evoluta deve preferire azioni locali quando il problema è locale.
