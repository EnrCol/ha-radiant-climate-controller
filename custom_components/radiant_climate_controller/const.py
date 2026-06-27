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

ACTION_IDLE = "mantenimento"
ACTION_PRECOOL = "anticipo_raffrescamento"
ACTION_DEHUMIDIFY = "deumidificare_zona"
ACTION_LOCAL_PROTECTION = "protezione_locale_stanza"
ACTION_GLOBAL_PROTECTION = "protezione_globale_mandata"
ACTION_ACS_BLOCK = "blocco_acs"
ACTION_DOOR_STANDBY = "standby_porte"
ACTION_DISABLED = "non_estate"

DEFAULT_SEASON_ENTITY = "input_select.modalita_stagionale"
DEFAULT_TEMPERATURE_ENTITIES = "sensor.temperatura_cucina, sensor.temperatura_soggiorno, sensor.temperatura_bagno, sensor.temperatura_studio, sensor.temperatura_camera, sensor.temperatura_camera_ricky"
DEFAULT_HUMIDITY_ENTITIES = "sensor.umidita_cucina, sensor.umidita_soggiorno, sensor.umidita_bagno, sensor.umidita_studio, sensor.umidita_camera, sensor.umidita_camera_ricky"

ENTITY_DEW_POINT_MARGIN = "input_number.rugiada_temperatura_delta_sicurezza"
ENTITY_DEW_POINT_MAX_HOUSE = "sensor.punto_rugiada_massimo_casa"
ENTITY_STANDBY_RUGIADA = "binary_sensor.standby_rugiada"
ENTITY_STANDBY_PORTE = "binary_sensor.standby_porte"
ENTITY_STANDBY_ATTIVO = "binary_sensor.standby_attivo"
ENTITY_ACS_BLOCK = "binary_sensor.acs_blocco_valvola_miscelatrice"

DEFAULT_THRESHOLD_NORMAL = 25.2
DEFAULT_THRESHOLD_BOOST = 25.7
DEFAULT_THRESHOLD_RECOVERY = 26.2

DEFAULT_PRECOOL_NORMAL_TEMP = 24.8
DEFAULT_PRECOOL_BOOST_TEMP = 25.3
DEFAULT_PRECOOL_RECOVERY_TEMP = 25.8

DEFAULT_TREND_NORMAL = 0.15
DEFAULT_TREND_BOOST = 0.20
DEFAULT_TREND_RECOVERY = 0.25

DEFAULT_TARGET_MAINTENANCE = 19.2
DEFAULT_TARGET_NORMAL = 19.0
DEFAULT_TARGET_BOOST = 18.5
DEFAULT_TARGET_RECOVERY = 18.0
DEFAULT_DEW_POINT_MARGIN = 2.5
