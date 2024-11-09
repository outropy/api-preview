from typing import Any, Dict, List, cast

from outropy.types.pytree import KeyPath, MappingKey


def merge_lists(path: KeyPath, dest: List[Any], src: List[Any]) -> None:
    dest.extend(src)


def merge_dict_key(path: KeyPath, dest: Dict[str, Any], value: Any) -> None:
    last_part: MappingKey = cast(MappingKey, path[-1])  # type: ignore
    old_val = dest.get(last_part.key)
    # print("DICT MERGY MERGE", path, old_val == value)

    # super smart merging tech
    if old_val != value:
        # print("Conflict resolution for", path, len(str(old_val)), "vs", len(str(value)))
        if len(str(old_val)) > len(str(value)):
            # print("\t old val won")
            value = old_val
        # else:
        #     print("\t new val won")
    # print("\tOLD VAL:", len(str(old_val)), str(old_val)[:40])
    # print("\tNEW VAL:", len(str(value)), str(value)[:40])
    dest[last_part.key] = value


def merge_with_path(path: KeyPath, dest: Dict[str, Any], raw_source: Any) -> None:
    sources: List[Dict[str, Any]]
    if isinstance(raw_source, list):
        sources = raw_source
    else:
        sources = [raw_source]

    for source in sources:
        for k, v in source.items():
            entry_path = path + (MappingKey(key=k),)
            if v is None:
                continue
            if k in dest:
                if isinstance(v, dict):
                    merge_with_path(entry_path, dest[k], v)
                elif isinstance(v, list):
                    merge_lists(entry_path, dest[k], v)
                    dest[k].extend(v)
                else:
                    merge_dict_key(entry_path, dest, v)
            else:
                dest[k] = v


def object_merge(dest: Dict[str, Any], raw_source: Any) -> None:
    merge_with_path((), dest, raw_source)
