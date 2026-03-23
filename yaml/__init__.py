from __future__ import annotations

import json
from typing import Any


def safe_load(text: str) -> Any:
    lines = text.splitlines()
    if not any(':' in line for line in lines):
        return text
    result: dict[str, Any] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith('#'):
            i += 1
            continue
        if ': |' in line:
            key = line.split(':', 1)[0].strip()
            i += 1
            block = []
            while i < len(lines) and (lines[i].startswith('  ') or not lines[i].strip()):
                block.append(lines[i][2:] if lines[i].startswith('  ') else '')
                i += 1
            result[key] = '\n'.join(block).rstrip() + '\n'
            continue
        key, raw = line.split(':', 1)
        key = key.strip()
        raw = raw.strip()
        if raw == '':
            if i + 1 < len(lines) and lines[i + 1].lstrip().startswith('- '):
                items = []
                i += 1
                while i < len(lines) and lines[i].lstrip().startswith('- '):
                    item_line = lines[i].lstrip()[2:]
                    if ': ' in item_line:
                        obj = {}
                        subkey, subval = item_line.split(':', 1)
                        obj[subkey.strip()] = _parse_scalar(subval.strip())
                        i += 1
                        while i < len(lines) and lines[i].startswith('    '):
                            k, v = lines[i].strip().split(':', 1)
                            obj[k.strip()] = _parse_scalar(v.strip())
                            i += 1
                        items.append(obj)
                        continue
                    items.append(_parse_scalar(item_line))
                    i += 1
                result[key] = items
                continue
            result[key] = {}
            i += 1
            continue
        result[key] = _parse_scalar(raw)
        i += 1
    return result


def _parse_scalar(value: str) -> Any:
    if value.startswith('[') and value.endswith(']'):
        return [item.strip() for item in value[1:-1].split(',') if item.strip()]
    if value.lower() in {'true', 'false'}:
        return value.lower() == 'true'
    if value.isdigit():
        return int(value)
    return value.strip('"')
