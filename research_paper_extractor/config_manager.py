"""
Config file manager using INI format for user preferences.
Uses RawConfigParser to avoid conflicts with % in date format strings.
"""

import configparser
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

CONFIG_FILE = Path.home() / '.arxiv_downloader.ini'

DEFAULTS = {
    'general': {
        'download_dir': './downloads',
        'max_results': '10',
        'sort_by': 'relevance',
        'request_delay': '1.0',
    },
    'display': {
        'show_abstract_preview': 'true',
        'abstract_preview_length': '200',
        'date_format': '%Y-%m-%d',
        'theme': 'cyan', # Options: cyan, green, blue, yellow, white
    },
    'watchlist': {
        'lookback_days': '7',
        'max_results_per_query': '10',
    },
    'notifications': {
        'webhook_url': '',
    },
}


def _get_parser() -> configparser.RawConfigParser:
    """Return a RawConfigParser pre-loaded with defaults."""
    parser = configparser.RawConfigParser()
    for section, values in DEFAULTS.items():
        parser[section] = values
    return parser


def load_config() -> configparser.RawConfigParser:
    """
    Load user config from disk, merging with defaults.

    Returns:
        ConfigParser with user settings
    """
    parser = _get_parser()
    if CONFIG_FILE.exists():
        try:
            parser.read(str(CONFIG_FILE))
        except configparser.Error as e:
            logger.warning(f'Could not parse config file: {e}')
    return parser


def save_config(parser: configparser.ConfigParser) -> None:
    """Persist config to disk."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            parser.write(f)
    except IOError as e:
        logger.error(f'Could not save config: {e}')


def get(section: str, key: str, fallback: Any = None) -> str:
    """
    Get a single config value.

    Args:
        section: Config section name
        key: Key within section
        fallback: Value to return if not found

    Returns:
        Config value as string
    """
    parser = load_config()
    return parser.get(section, key, fallback=fallback)


def set_value(section: str, key: str, value: str) -> None:
    """
    Set and persist a single config value.

    Args:
        section: Config section name
        key: Key within section
        value: New value
    """
    parser = load_config()
    if not parser.has_section(section):
        parser.add_section(section)
    parser.set(section, key, str(value))
    save_config(parser)


def reset_config() -> None:
    """Reset config to defaults (deletes config file)."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        logger.info('Config file removed; defaults will be used.')


def show_config() -> str:
    """Return a human-readable representation of the current config."""
    parser = load_config()
    lines = [f'Config file: {CONFIG_FILE}', '=' * 50]
    for section in parser.sections():
        lines.append(f'\n[{section}]')
        for key, val in parser.items(section):
            # Mask defaults marker
            is_default = DEFAULTS.get(section, {}).get(key) == val
            default_mark = '  (default)' if is_default else ''
            lines.append(f'  {key} = {val}{default_mark}')
    if not parser.sections():
        lines.append('(using all defaults)')
    return '\n'.join(lines)


def get_download_dir_from_config() -> Optional[str]:
    """Get download directory from config."""
    val = get('general', 'download_dir')
    return val if val else None


def get_max_results_from_config() -> int:
    """Get max results from config."""
    try:
        return int(get('general', 'max_results', fallback='10'))
    except (ValueError, TypeError):
        return 10
