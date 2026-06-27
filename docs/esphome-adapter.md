# ESPHome adapter

La custom integration espone:

```text
sensor.centralina_radiante_target_mandata_finale
```

Il nome esatto può cambiare in base al nome configurato nella config flow. Verificare l'entity_id creato in Home Assistant.

## Import in ESPHome

```yaml
sensor:
  - platform: homeassistant
    id: target_mandata_ha
    entity_id: sensor.centralina_radiante_target_mandata_finale
    internal: true
```

## Priorità nel calcolo target

```cpp
float target = target_da_curva;

if (id(target_mandata_ha).has_state()) {
  float ha_target = id(target_mandata_ha).state;
  if (!isnan(ha_target) && ha_target >= 17.0f && ha_target <= 23.0f) {
    target = ha_target;
  }
}
```

La curva locale ESPHome deve restare fallback.
