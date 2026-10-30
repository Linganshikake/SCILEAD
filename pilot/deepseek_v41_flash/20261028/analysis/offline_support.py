"""Small offline IO boundary. No experiment runtime or model imports."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import types

sys.dont_write_bytecode = True
ANALYSIS = Path(r'D:\C++\SCILEAD\pilot\deepseek_v41_flash\20261028\analysis').resolve()
ROOT = ANALYSIS.parents[3]
PILOT = ROOT/'pilot'
REPO = ROOT/'emnlp2024-leaderboard-generation'
GOLD = Path(r'C:\Users\Administrator\Desktop\KG\SCILEAD_DATA\data\tdm_annotations.json')
BOARDS = GOLD.with_name('leaderboards.json')
HELPERS = PILOT/'full43_cs/leaderboard_evaluation'
_installed = False


def within(path, root=ANALYSIS):
    try:
        Path(path).resolve().relative_to(root.resolve())
        return True
    except (ValueError, TypeError):
        return False


def require_output(path):
    p = Path(path).resolve()
    if not within(p) or p == ANALYSIS:
        raise ValueError(f'Output must be strictly below {ANALYSIS}: {p}')
    return p


def boundary():
    global _installed
    if _installed:
        return
    def guard(event, args):
        if event in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn', '_winapi.CreateProcess'):
            raise RuntimeError('Child processes forbidden in offline evaluation')
        if event.startswith('socket.') and event not in ('socket.__new__',):
            raise RuntimeError('Network forbidden: offline evaluation')
        if event == 'open':
            path, mode, flags = args
            if isinstance(path, (str, bytes, os.PathLike)):
                name = Path(os.fsdecode(path)).name.lower()
                if name == '.env' or name.endswith('.env') or name.startswith('.env.') or name in ('credentials', 'credentials.json'):
                    raise RuntimeError('Credential files forbidden')
                writing = (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
                if writing and not within(os.fsdecode(path)):
                    raise RuntimeError(f'Write outside analysis forbidden: {path}')
        if event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.utime', 'os.truncate'):
            if not within(args[0]):
                raise RuntimeError(f'Mutation outside analysis forbidden: {args[0]}')
        if event in ('os.rename', 'os.link', 'os.symlink'):
            if not all(within(p) for p in args[:2]):
                raise RuntimeError('Mutation outside analysis forbidden')
        if event == 'import' and args[0].split('.')[0] in ('model_init', 'transformers', 'langchain', 'openai', 'httpx', 'dotenv', 'variant_runtime'):
            raise RuntimeError('Model/transport imports forbidden')
    sys.addaudithook(guard)
    _installed = True


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f'Duplicate JSON key: {key}')
        value[key] = item
    return value


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object)


def save(path, value):
    p = require_output(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_name(p.name+'.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    temp.replace(p)


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def verify(hashes):
    changed = [str(p) for p, h in hashes.items() if not Path(p).is_file() or sha(p) != h]
    if changed:
        raise ValueError(f'Input/source changed during evaluation: {changed}')
    return {'files_checked': len(hashes), 'changed': changed}


def bind_official():
    """Only read_json is used by official evaluators; avoid utils' model imports."""
    boundary()
    util = types.ModuleType('utils')
    util.read_json = read
    sys.modules['utils'] = util
    for name in ('tdm_eval', 'leaderboard_eval'):
        spec = importlib.util.spec_from_file_location(name, REPO/(name+'.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)


def fresh_directory(path):
    p = require_output(path)
    if p.exists() and any(p.iterdir()):
        raise ValueError(f'Use a new/empty output directory to avoid stale results: {p}')
    p.mkdir(parents=True, exist_ok=True)
    return p
