"""Room model for the first Enrico plant profile."""

ROOMS = {
    "cucina": {
        "name": "Cucina",
        "zone": "giorno",
        "temperature": "sensor.temperatura_cucina",
        "humidity": "sensor.umidita_cucina",
        "dew_point": "sensor.cucina_punto_di_rugiada",
        "climate": "climate.termostato_cucina",
        "safety_boolean": "input_boolean.sicurezza_rugiada_cucina",
    },
    "soggiorno": {
        "name": "Soggiorno",
        "zone": "giorno",
        "temperature": "sensor.temperatura_soggiorno",
        "humidity": "sensor.umidita_soggiorno",
        "dew_point": "sensor.soggiorno_punto_di_rugiada",
        "climate": "climate.termostato_soggiorno",
        "safety_boolean": "input_boolean.sicurezza_rugiada_soggiorno",
    },
    "bagno": {
        "name": "Bagno",
        "zone": "notte",
        "temperature": "sensor.temperatura_bagno",
        "humidity": "sensor.umidita_bagno",
        "dew_point": "sensor.bagno_punto_di_rugiada",
        "climate": "climate.termostato_bagno",
        "safety_boolean": "input_boolean.sicurezza_rugiada_bagno",
    },
    "studio": {
        "name": "Studio",
        "zone": "notte",
        "temperature": "sensor.temperatura_studio",
        "humidity": "sensor.umidita_studio",
        "dew_point": "sensor.studio_punto_di_rugiada",
        "climate": "climate.termostato_studio",
        "safety_boolean": "input_boolean.sicurezza_rugiada_studio",
    },
    "camera": {
        "name": "Camera",
        "zone": "notte",
        "temperature": "sensor.temperatura_camera",
        "humidity": "sensor.umidita_camera",
        "dew_point": "sensor.camera_punto_di_rugiada",
        "climate": "climate.termostato_camera",
        "safety_boolean": "input_boolean.sicurezza_rugiada_camera",
    },
    "camera_ricky": {
        "name": "Camera Ricky",
        "zone": "notte",
        "temperature": "sensor.temperatura_camera_ricky",
        "humidity": "sensor.umidita_camera_ricky",
        "dew_point": "sensor.camera_ricky_punto_di_rugiada",
        "climate": "climate.termostato_camera_ricky",
        "safety_boolean": "input_boolean.sicurezza_rugiada_camera_ricky",
    },
}

ZONE_DEHUMIDIFIERS = {
    "giorno": {
        "name": "Giorno",
        "request": "binary_sensor.richiesta_deumidificazione_giorno",
        "consent": "switch.consenso_deumidificatore_giorno",
        "average_temperature": "sensor.temperatura_media_zona_giorno",
        "average_humidity": "sensor.umidita_media_zona_giorno",
        "humidity_threshold": "sensor.soglia_umidita_zona_giorno",
    },
    "notte": {
        "name": "Notte",
        "request": "binary_sensor.richiesta_deumidificazione_notte",
        "consent": "switch.consenso_deumidificatore_notte",
        "average_temperature": "sensor.temperatura_media_zona_notte",
        "average_humidity": "sensor.umidita_media_zona_notte",
        "humidity_threshold": "sensor.soglia_umidita_zona_notte",
    },
}
