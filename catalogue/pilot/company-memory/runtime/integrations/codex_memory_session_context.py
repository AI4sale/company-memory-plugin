"""Trusted Codex runtime identity envelope, separate from editable memory content."""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import json
import os
from pathlib import Path
import re
import uuid

from filelock import FileLock

BINDING_SCHEMA = 'company-memory-codex-session.v1'
ACTIVATION_SCHEMA = 'company-memory-codex-pilot-activation.v1'
_context = ContextVar('company_memory_codex_session', default=None)


def _root(state_root=None):
    return Path(state_root or os.environ.get('CODEX_COMPANY_MEMORY_STATE_DIR')
                or Path.home() / '.codex' / 'company-memory-card-pilot')


def _folder(session_id, state_root=None):
    if not isinstance(session_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,233}', session_id):
        raise ValueError('invalid Codex runtime session_id')
    return _root(state_root) / hashlib.sha256(session_id.encode()).hexdigest()[:32]


def ensure_binding(session_id, state_root=None):
    """Create once under a lock; reject an inconsistent registry instead of repairing it."""
    folder = _folder(session_id, state_root)
    path = folder / 'binding.json'
    lock = folder / 'binding.lock'
    if any(p.is_symlink() for p in (folder.parent, folder, path, lock)):
        raise ValueError('unsafe Codex session binding path')
    folder.mkdir(parents=True, exist_ok=True)
    expected = {'schema_version': BINDING_SCHEMA, 'session_id': session_id,
                'task_id': 'codex:' + session_id}
    with FileLock(str(lock), timeout=5):
        if path.exists():
            try:
                value = json.loads(path.read_text(encoding='utf-8'))
                valid = (isinstance(value, dict) and all(value.get(k) == v for k, v in expected.items())
                         and isinstance(value.get('workspace_root'), str)
                         and Path(value['workspace_root']).is_absolute())
            except (OSError, ValueError):
                valid = False
            if not valid:
                raise ValueError('Codex session binding mismatch or invalid registry')
            return value
        value = {**expected, 'workspace_root': str(Path.cwd().resolve())}
        temporary = path.with_name('binding.' + uuid.uuid4().hex + '.tmp')
        try:
            with temporary.open('x', encoding='utf-8') as stream:
                json.dump(value, stream, sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
        return value


def _scoped(roots):
    cwd = Path.cwd().resolve()
    return any(Path(r).is_absolute() and (cwd == Path(r).resolve() or Path(r).resolve() in cwd.parents)
               for r in roots if isinstance(r, str))


def runtime_context(session_id=None, state_root=None):
    """Only trusted explicit runtime inputs or an activated, scoped ambient runtime bind."""
    if session_id is not None:
        return ensure_binding(session_id, state_root)
    active = _context.get()
    if active is not None:
        return ensure_binding(*active)
    session_id = os.environ.get('CODEX_THREAD_ID')
    if not session_id:
        return None
    folder = _folder(session_id, state_root)
    activation = folder.parent / 'activation.json'
    if activation.exists():
        if activation.is_symlink():
            raise ValueError('unsafe Codex pilot activation path')
        config = json.loads(activation.read_text(encoding='utf-8'))
        if (not isinstance(config, dict) or config.get('schema_version') != ACTIVATION_SCHEMA or config.get('enabled') is not True
                or not isinstance(config.get('scope_roots'), list) or not _scoped(config['scope_roots'])):
            return None
    else:
        return None
    return ensure_binding(session_id, state_root)


def resolve_task_id(requested=None, session_id=None, state_root=None):
    binding = runtime_context(session_id, state_root)
    return binding['task_id'] if binding else requested


@contextmanager
def session_context(session_id, state_root=None):
    binding = ensure_binding(session_id, state_root)
    token = _context.set((session_id, state_root))
    try:
        yield binding
    finally:
        _context.reset(token)
