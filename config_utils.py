# config_utils.py
import os
import json
from typing import Dict, List, Tuple
from version import CONFIG_VERSION
from logger_utils import get_logger

log = get_logger(__name__)


def update_configuration(
    config_path: str,
    default_data: Dict,
    current_version: int,
    is_dict: bool = True
):
    """
    Lädt/aktualisiert eine Config-Datei. Falls nicht vorhanden oder invalide:
    mit default_data initialisieren. Hebt Daten auf neue Version an.
    """
    data_updated = False
    config_data = None

    if os.path.exists(config_path):
        log.debug("Loading configuration: %s", config_path)
        try:
            with open(config_path, 'r', encoding="utf-8") as config_file:
                config_data = json.load(config_file)

            if 'data' not in config_data or not isinstance(config_data.get('version', 0), int):
                log.warning("Invalid config schema in %s; resetting to defaults.", config_path)
                config_data = {"version": 0, "data": []}

            old_version = config_data.get('version', 0)
            if old_version < current_version:
                log.info("Upgrading config %s from v%s to v%s", config_path, old_version, current_version)
                if is_dict:
                    # Mergen anhand 'name'
                    existing_items = {item['name']: item for item in config_data['data'] if isinstance(item, dict) and 'name' in item}
                    for item in default_data['data']:
                        existing_items[item['name']] = item
                    config_data['data'] = list(existing_items.values())
                else:
                    existing_data_set = set(config_data['data']) if isinstance(config_data['data'], list) else set()
                    default_data_set = set(default_data['data'])
                    config_data['data'] = list(existing_data_set.union(default_data_set))

                config_data['version'] = current_version
                data_updated = True
            else:
                log.debug("Config %s already at version %s", config_path, old_version)

        except json.JSONDecodeError:
            log.warning("JSON decode error in %s; rewriting with defaults.", config_path)
            config_data = default_data
            data_updated = True
        except Exception as e:
            log.error("Failed reading %s: %s; using defaults.", config_path, e)
            config_data = default_data
            data_updated = True
    else:
        log.info("Config not found; initializing defaults: %s", config_path)
        config_data = default_data
        data_updated = True

    if data_updated:
        try:
            with open(config_path, 'w', encoding="utf-8") as config_file:
                json.dump(config_data, config_file, indent=4)
            log.info("Wrote configuration %s (version=%s, items=%s)",
                     config_path, config_data.get('version'), len(config_data.get('data', [])))
        except Exception as e:
            log.error("Failed writing %s: %s", config_path, e)

    # Safety: falls irgendwas schiefging
    data = config_data.get('data', []) if isinstance(config_data, dict) else []
    log.debug("Returning %d items from %s", len(data), config_path)
    return data


def load_configurations(doc_main_dir: str) -> Tuple[List[str], Dict[str, str], List[str], List[str]]:
    """
    Lädt/aktualisiert alle relevanten Konfigurationen (Stores, Tags, DAZ-Folders).
    Gibt (store_names, store_prefixes, tag_items, daz_folder_items) zurück.
    """
    config_version = CONFIG_VERSION
    config_path = os.path.join(doc_main_dir, 'Config')
    os.makedirs(config_path, exist_ok=True)
    log.info("Loading configurations from %s (target version=%s)", config_path, config_version)

    default_store_data = {
        "version": config_version,
        "data": [
            {"name": "DAZ 3D", "prefix": "IM"},
            {"name": "Renderosity", "prefix": "RO"},
            {"name": "Renderhub", "prefix": "RH"},
            {"name": "Renderotica", "prefix": "RE"},
            {"name": "CGBytes", "prefix": "CB"},
            {"name": "CGTrader", "prefix": "CG"},
            {"name": "DeviantArt", "prefix": "DA"},
            {"name": "ShareCG", "prefix": "SH"},
            {"name": "Sketchfab", "prefix": "SF"},
            {"name": "Free3D", "prefix": "F3D"},
            {"name": "Turbosquid", "prefix": "TS"},
            {"name": "3DExport", "prefix": "3DX"},
            {"name": "Patreon", "prefix": "PR"},
            {"name": "Forender", "prefix": "FR"},
            {"name": "LOCAL USER", "prefix": "IM"}
        ]
    }

    default_tags = {
        "version": config_version,
        "data": [
            "Bryce",
            "CarraraLegacy",
            "Carrara7",
            "Carrara7_2",
            "Carrara8",
            "Carrara8_5",
            "DAZStudioLegacy",
            "DAZStudio3",
            "DAZStudio4",
            "DAZStudio4_5",
            "DSON_Poser",
            "General",
            "Hexagon",
            "InstallManager",
            "LightWave",
            "Mac32",
            "Mac64",
            "Photoshop",
            "Plugin",
            "PoserLegacy",
            "Poser9",
            "PrivateBuild",
            "PublicBuild",
            "Software",
            "Vue",
            "Win32",
            "Win64"
        ]
    }

    default_daz_folders = {
        "version": config_version,
        "data": [
            "aniBlocks",
            "data",
            "Environments",
            "General",
            "Light Presets",
            "People",
            "Props",
            "Render Presets",
            "Render Settings",
            "Runtime",
            "Scene Builder",
            "Scenes",
            "Scripts",
            "Shader Presets",
            "Shaders"
        ]
    }

    stores_path = os.path.join(config_path, 'store_data.json')
    tags_path = os.path.join(config_path, 'product_tags.json')
    folders_path = os.path.join(config_path, 'daz_folders.json')

    store_items = update_configuration(stores_path, default_store_data, config_version, True)
    log.debug("Loaded %d store items", len(store_items))
    store_names = [item['name'] for item in store_items if isinstance(item, dict) and 'name' in item]
    store_prefixes = {item['name']: item.get('prefix', '') for item in store_items
                      if isinstance(item, dict) and 'name' in item}

    tag_items = update_configuration(tags_path, default_tags, config_version, False)
    daz_folder_items = update_configuration(folders_path, default_daz_folders, config_version, False)

    tag_items.sort()
    daz_folder_items.sort()

    log.info("Configurations loaded: stores=%d, tags=%d, daz_folders=%d",
             len(store_names), len(tag_items), len(daz_folder_items))

    return store_names, store_prefixes, tag_items, daz_folder_items
