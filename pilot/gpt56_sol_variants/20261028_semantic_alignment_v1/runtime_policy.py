"""Owned paths and offline test/preparation guards; no credentials are inspected."""
import os
import sys
from pathlib import Path

OWNED = Path(__file__).resolve().parent
sys.dont_write_bytecode = True


def owned(path):
    path = Path(path).resolve()
    if not path.is_relative_to(OWNED):
        raise ValueError('Write outside variants prohibited: ' + str(path))
    return path


def configure_paths(root=OWNED):
    root = owned(root)
    tmp = root / 'runtime/tmp'
    tmp.mkdir(parents=True, exist_ok=True)
    hf = root / 'runtime/huggingface'
    os.environ.update(
        PYTHONDONTWRITEBYTECODE='1', HF_HOME=str(hf), HF_HUB_CACHE=str(hf / 'hub'),
        HF_MODULES_CACHE=str(hf / 'modules'), HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
        HF_HUB_DISABLE_TELEMETRY='1', HF_HUB_DISABLE_IMPLICIT_TOKEN='1',
        TMP=str(tmp), TEMP=str(tmp), TMPDIR=str(tmp), XDG_CACHE_HOME=str(root / 'runtime/xdg'),
        MPLCONFIGDIR=str(root / 'runtime/matplotlib'), TORCH_HOME=str(root / 'runtime/torch'),
        LANGCHAIN_TRACING='false', LANGCHAIN_TRACING_V2='false', LANGSMITH_TRACING='false',
        ANONYMIZED_TELEMETRY='False')


def offline_guard(root=OWNED):
    """Install before imports in tests/preparation; HTTP MockTransport needs no sockets."""
    root = owned(root)

    def allowed(path):
        return (path is None or isinstance(path, int) or os.fsdecode(path).lower() == 'nul'
                or Path(os.fsdecode(path)).resolve().is_relative_to(root))

    def audit(event, args):
        if event in ('socket.connect', 'socket.getaddrinfo'):
            raise RuntimeError('Offline validation: network prohibited')
        if event == 'open':
            path, mode, flags = args
            if not isinstance(path, int):
                p = Path(os.fsdecode(path))
                if p.name.lower() in ('.env', 'token', 'stored_tokens', 'credentials') or p.suffix.lower() == '.env':
                    raise RuntimeError('Offline validation: credential access prohibited')
                if p.suffix.lower() == '.safetensors' or p.name.lower().startswith('pytorch_model'):
                    raise RuntimeError('Offline validation: model weights access prohibited')
            writing = ((isinstance(mode, str) and any(c in mode for c in 'wax+')) or
                       (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
            if writing and not allowed(path):
                raise RuntimeError('Write outside owned scope: ' + str(path))
        elif event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.utime'):
            if not allowed(args[0]):
                raise RuntimeError('Mutation outside owned scope: ' + str(args[0]))
        elif event in ('os.rename', 'os.link', 'os.symlink'):
            if not all(allowed(p) for p in args[:2]):
                raise RuntimeError('Mutation outside owned scope')

    sys.addaudithook(audit)
    configure_paths(root)
