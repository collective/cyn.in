HIT_RATE_TIME_INTERVAL = 7 * 24 * 3600    # one week, in seconds

MIN_RATING_VALUE = 1
MAX_RATING_VALUE = 5
NEUTRAL_RATING_VALUE = 3

from ZODBStorage import ZODBStorage

STORAGE_CLASS = ZODBStorage
STORAGE_ARGS = {}

PROJECTNAME = "ATRatings"
SKINS_DIR = 'skins'

GLOBALS = globals()

CLEAR_REFS_ON_UNINSTALL = 0
