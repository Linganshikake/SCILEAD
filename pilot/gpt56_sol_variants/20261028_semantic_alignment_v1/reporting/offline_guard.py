"""Audit-hook enforcement for this reporting-only offline process."""
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


class Guard:
    def __init__(self):
        self.write_paths = set()
        self.blocked = []

    def deny(self, event):
        self.blocked.append(event)
        raise PermissionError('offline reporting guard blocked ' + event)

    def target(self, value):
        if isinstance(value, (str, bytes, os.PathLike)):
            return Path(os.fsdecode(value)).resolve()
        return None

    def write(self, value, event):
        path = self.target(value)
        if path is None or not path.is_relative_to(HERE):
            self.deny(event + ':outside_reporting')
        self.write_paths.add(str(path))

    def __call__(self, event, args):
        if event.startswith(('socket.', 'subprocess.', 'ctypes.dlopen')) or event in ('os.system', 'os.exec', 'os.posix_spawn', 'os.spawn'):
            self.deny(event)
        if event == 'import' and args[0].split('.')[0] in {'httpx', 'requests', 'openai', 'transformers', 'torch', 'dotenv', 'variant_runtime'}:
            self.deny('import:' + args[0])
        if event == 'open':
            path = self.target(args[0])
            if path and (path.name == '.env' or path.name.startswith('.env.') or any(part in {'.aws', '.ssh'} for part in path.parts)):
                self.deny('credential_read')
            mode, flags = args[1], args[2]
            if (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
                self.write(args[0], event)
        elif event in ('os.remove', 'os.rmdir', 'os.mkdir', 'os.chmod', 'os.utime', 'os.truncate'):
            self.write(args[0], event)
        elif event in ('os.rename', 'os.link', 'os.symlink'):
            self.write(args[0], event)
            self.write(args[1], event)


def activate():
    guard = Guard()
    sys.addaudithook(guard)
    return guard
