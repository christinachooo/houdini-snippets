import json
import logging
import os
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

PREFS_PATH = os.getenv(
    'HOUDINI_SNIPPETS_PREFS', os.path.expanduser('~/houdini-snippets.json')
)


@dataclass
class Settings:
    snippet_path: str = os.path.normpath(os.path.expanduser('~/houdini-snippets'))
    add_network_box: bool = False
    randomize_network_box_colors: bool = False


def save_settings(settings: Settings) -> None:
    logger.info(f'Saving Settings: {PREFS_PATH}, {settings}')
    settings_dict = asdict(settings)

    with open(PREFS_PATH, 'w') as f:
        json.dump(settings_dict, f, indent=4)


def load_settings() -> Settings:
    logger.info(f'Loading Settings: {PREFS_PATH}')
    try:
        with open(PREFS_PATH, 'r') as f:
            settings_dict = json.load(f)
    except (OSError, json.JSONDecodeError):
        settings_dict = {}

    settings = Settings(**settings_dict)
    return settings
