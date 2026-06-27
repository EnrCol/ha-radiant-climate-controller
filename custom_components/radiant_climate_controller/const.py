"""Constants for Radiant Climate Controller."""

DOMAIN = "radiant_climate_controller"
DEFAULT_NAME = "Centralina Radiante"
DATA_COORDINATOR = "coordinator"

CONF_SEASON_ENTITY = "season_entity"
CONF_TEMPERATURE_ENTITIES = "temperature_entities"
CONF_HUMIDITY_ENTITIES = "humidity_entities"

DEFAULT_SCAN_INTERVAL_SECONDS = 30

STATE_MAINTENANCE = "mantenimento"
STATE_NORMAL = "normale"
STATE_BOOST = "spinto"
STATE_RECOVERY = "recupero"
STATE_UNKNOWN = "sconosciuto"

DEFAULT_SEASON_ENTITY = "input_select.modalita_stagionale"
DEFAULT_TEMPERATURE_ENTITIES = "climate.soggiorno, climate.cucina, climate.bagno, climate.studio, climate.camera, climate.camera_ricky, sensor.temperatura_soggiorno, sensor.soggiorno_temperature, sensor.temperatura_cucina, sensor.cucina_temperature, sensor.temperatura_bagno, sensor.bagno_temperature, sensor.temperatura_studio, sensor.studio_temperature, sensor.temperatura_camera, sensor.camera_temperature, sensor.temperatura_camera_ricky, sensor.camera_ricky_temperature"
DEFAULT_HUMIDITY_ENTITIES = "sensor.umidita_media_zona_giorno, sensor.umidita_media_zona_notte, sensor.umidita_soggiorno, sensor.soggiorno_humidity, sensor.umidita_cucina, sensor.cucina_humidity, sensor.umidita_bagno, sensor.bagno_humidity, sensor.umidita_studio, sensor.studio_humidity, sensor.umidita_camera, sensor.camera_humidity, sensor.umidita_camera_ricky, sensor.camera_ricky_humidity"

DEFAULT_THRESHOLD_NORMAL = 25.2
DEFAULT_THRESHOLD_BOOST = 25.7
DEFAULT_THRESHOLD_RECOVERY = 26.2

DEFAULT_TARGET_MAINTENANCE = 19.2
DEFAULT_TARGET_NORMAL = 19.0
DEFAULT_TARGET_BOOST = 18.5
DEFAULT_TARGET_RECOVERY = 18.0
DEFAULT_DEW_POINT_MARGIN = 2.0
