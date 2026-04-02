from recnys.utils.platform import Platform

from .model import EntryKey, KeyCategory


def get_default_dest(key: EntryKey, platform: Platform) -> str:
    match key.category:
        case KeyCategory.DIRECTORY:
            match platform:
                case Platform.WINDOWS:
                    return str(Path.home() / "AppData/Roaming" / key.src)
                case Platform.LINUX:
                    return str(Path.home() / ".config" / key.src)
        case KeyCategory.STATIC_FILE | KeyCategory.DYNAMIC_FILE:

    if "/" in key:
        match platform:
            case Platform.WINDOWS:
                return Path.home() / "AppData/Roaming" / key
            case Platform.LINUX:
                return Path.home() / ".config" / key

    return Path.home() / key
