# Architettura

## Scelta

Questo progetto usa una custom integration Home Assistant invece di un package YAML.

La divisione è:

```text
Home Assistant = centralina climatica
ESPHome = PID locale valvola miscelatrice
```

## Perché integrazione e non package

Una integrazione permette:

- configurazione da UI;
- entità generate automaticamente;
- diagnostica più pulita;
- futura installazione HACS;
- logica Python testabile;
- evoluzione verso number/select/button senza moltiplicare YAML.

## Ciclo di controllo

```text
sensori ambiente
+ umidità
+ modalità stagionale
→ stato radiante
→ target mandata richiesto
→ limite punto rugiada
→ target mandata finale
→ ESPHome PID valvola
```

## Regola anti-condensa

```text
target_finale = max(target_richiesto, punto_rugiada + margine)
```

Il margine iniziale è 2.0°C.
