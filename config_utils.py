import os
import json
from typing import Dict, List, Tuple
from version import CONFIG_VERSION

def update_configuration(config_path: str, default_data: Dict, current_version: int, is_dict: bool = True):
    data_updated = False
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            try:
                config_data = json.load(config_file)
                if 'data' not in config_data or not isinstance(config_data.get('version', 0), int):
                    config_data = {"version": 0, "data": []}
                if config_data.get('version', 0) < current_version:
                    if is_dict:
                        existing_items = {item['name']: item for item in config_data['data']}
                        for item in default_data['data']:
                            existing_items[item['name']] = item
                        config_data['data'] = list(existing_items.values())
                    else:
                        existing_data_set = set(config_data['data']) if isinstance(config_data['data'], list) else set()
                        default_data_set = set(default_data['data'])
                        config_data['data'] = list(existing_data_set.union(default_data_set))
                    config_data['version'] = current_version
                    data_updated = True
            except json.JSONDecodeError:
                config_data = default_data
                data_updated = True
    else:
        config_data = default_data
        data_updated = True

    if data_updated:
        with open(config_path, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)
    return config_data['data']


def load_configurations(doc_main_dir: str) -> Tuple[List[str], Dict[str, str], List[str], List[str]]:
    config_version = CONFIG_VERSION
    config_path = os.path.join(doc_main_dir, 'Config')
    os.makedirs(config_path, exist_ok=True)

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

    store_items = update_configuration(os.path.join(config_path, 'store_data.json'), default_store_data, config_version, True)
    store_names = [item['name'] for item in store_items]
    store_prefixes = {item['name']: item.get('prefix', '') for item in store_items}

    tag_items = update_configuration(os.path.join(config_path, 'product_tags.json'), default_tags, config_version, False)
    daz_folder_items = update_configuration(os.path.join(config_path, 'daz_folders.json'), default_daz_folders, config_version, False)

    tag_items.sort()
    daz_folder_items.sort()

    return store_names, store_prefixes, tag_items, daz_folder_items
