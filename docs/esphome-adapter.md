# ESPHome adapter

## Stato attuale

Nella serie `0.3.x` l integrazione non deve ancora comandare ESPHome.

Il target mandata consigliato e solo osservativo. Serve per verificare se la logica della centralina e stabile prima di usarla come comando reale.

## Obiettivo

ESPHome restera responsabile del controllo locale della valvola miscelatrice e del PID.

Home Assistant fornira:

```text
target mandata consigliato
consenso a usare il target
motivo del consenso o del blocco
```

ESPHome dovra sempre avere fallback locale.

## Entita previste v0.4

La prossima fase prevede una entita binaria:

```text
binary_sensor.centralina_radiante_target_mandata_comandabile
```

Sara `on` solo se il target puo essere usato in sicurezza.

Condizioni previste:

```text
modalita Estate
ACS non attiva
standby porte non attivo
standby rugiada non attivo
nessuna protezione globale attiva
target disponibile
target nel range sicuro
```

Possibile sensore aggiuntivo:

```text
sensor.centralina_radiante_motivo_target_non_comandabile
```

## Import ESPHome previsto

Esempio futuro:

```yaml
sensor:
  - platform: homeassistant
    id: target_mandata_ha
    entity_id: sensor.centralina_radiante_target_mandata_consigliato
    internal: true

binary_sensor:
  - platform: homeassistant
    id: target_mandata_ha_comandabile
    entity_id: binary_sensor.centralina_radiante_target_mandata_comandabile
    internal: true
```

Gli entity_id reali possono cambiare in base al nome configurato nella config flow. Verificare sempre gli entity_id creati da Home Assistant.

## Priorita nel calcolo target ESPHome

ESPHome dovra mantenere una curva locale come fallback.

Esempio logico:

```cpp
float target = target_da_curva;

if (
  id(target_mandata_ha_comandabile).state &&
  id(target_mandata_ha).has_state()
) {
  float ha_target = id(target_mandata_ha).state;

  if (!isnan(ha_target) && ha_target >= 17.0f && ha_target <= 23.0f) {
    target = ha_target;
  }
}
```

## Sicurezze che devono restare locali

Anche quando Home Assistant iniziera a fornire il target, ESPHome deve mantenere protezioni locali minime:

- range target valido;
- fallback se HA non risponde;
- fallback se sensore target e unavailable;
- blocco ACS se gia gestito localmente;
- manual override della valvola;
- limite fisico sulla percentuale valvola.

## Semantica valvola

Nel tuo impianto:

```text
Estate:
100% = piu acqua fredda da PDC/deumidificatori
0% = piu ritorno/ricircolo caldo

Inverno:
100% = piu acqua calda
0% = piu ritorno/ricircolo freddo
```

Questa semantica deve restare documentata nel codice ESPHome e non va nascosta nella sola integrazione Home Assistant.

## Roadmap ESPHome

### v0.4

Aggiunta consenso comando in Home Assistant.

### v0.5

Adattatore ESPHome documentato e testato in sola lettura/log.

### v0.6

Uso reale del target HA sul PID, con fallback attivo.

### v1.0

Centralina attiva stabile: Home Assistant decide il target, ESPHome esegue localmente in sicurezza.