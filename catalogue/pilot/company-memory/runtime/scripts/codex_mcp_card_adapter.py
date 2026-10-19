"""Adapter for the existing CARD runtime; installed as codex_remote_memory_hook.py.

The installer places a non-secret memory-client.json next to scripts/. Native
Codex owns OAuth credentials and refresh. This file owns neither identity nor
CARD state: both continue to come from codex_memory_session_context/Pilot.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from filelock import FileLock

from integrations import codex_memory_session_context as sessions
from integrations.company_memory_mcp.card_client import MCPCardClient

ROOT=Path(__file__).resolve().parent.parent
CONFIG=json.loads((ROOT/'memory-client.json').read_text(encoding='utf-8'))
STATE=Path(CONFIG['state_dir'])
EXECUTOR_ID='native-codex-client'
DEFAULT_ENTITY=CONFIG['entity']
DEFAULT_TARGET_HUB=CONFIG['target_hub']
DEFAULT_THEMATIC_HUB=DEFAULT_TARGET_HUB
DEFAULT_SOURCE_REF='CARD.md'
START_SCHEMA='company-memory-native-start.v1'
DISPOSITION_SCHEMA='company-memory-native-disposition.v1'
BUNDLE_SCHEMA='ais-os-codex-remote-memory-bundle.v1'
FINALIZE_SCHEMA='ais-os-codex-remote-memory-finalize.v1'


def _iso_now():return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')


def _stable(value,label):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,239}',value):
        raise ValueError('invalid '+label)
    return value


def _task_id(session):return sessions.ensure_binding(session,STATE)['task_id']


def _validated_client(task):return MCPCardClient(CONFIG,_stable(task,'task_id'))


def _append_record(value):
    STATE.mkdir(parents=True,exist_ok=True)
    with FileLock(str(STATE/'access.lock'),timeout=5):
        with (STATE/'access.jsonl').open('a',encoding='utf-8') as stream:
            stream.write(json.dumps(value,ensure_ascii=False)+'\n');stream.flush()
            __import__('os').fsync(stream.fileno())


def _latest(schema,*,session_id,turn_id):
    path=STATE/'access.jsonl'
    if not path.exists():return None
    # Ledger contains receipts, not prompts or retrieved source contents.
    match=None
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            value=json.loads(line)
            if (value.get('schema_version'),value.get('session_id'),value.get('turn_id'))==(schema,session_id,turn_id):match=value
    return match


def _hook_user_prompt(event):
    session,turn=event['session_id'],event['turn_id'];task=_task_id(session)
    client=_validated_client(task)
    found=client.call('company_memory_search',{'task_id':task,'memory_id':CONFIG['memory_id'],
        'zone_ids':[CONFIG['zone_id']],'query':str(event.get('prompt') or 'Current project context')[:1024]})
    receipt=found['access_receipt']['response_event_id']
    _append_record({'schema_version':START_SCHEMA,'occurred_at':_iso_now(),'session_id':session,
        'turn_id':turn,'task_id':task,'response_event_id':receipt})
    context=[]
    for item in found.get('items',[])[:2]:
        exact=client.call('company_memory_fetch',{'task_id':task,'memory_id':CONFIG['memory_id'],
            'zone_ids':[CONFIG['zone_id']],'source_ref':item['source_ref']})
        context.append({'title':exact.get('title'),'source_sha256':exact.get('source_sha256'),
            'content':exact.get('content','')[:2000]})
    return {'continue':True,'hookSpecificOutput':{'hookEventName':'UserPromptSubmit','additionalContext':''},
            'memoryContext':json.dumps(context,ensure_ascii=False)}


def _normalized_candidate(value):
    fields=('concept_id','type','epistemic_class','title','description','body','summary','tags',
            'sensitivity','thematic_hub_id','local_source_ref','external_source_refs')
    candidate={k:value[k] for k in fields}
    paths=[]
    for item in value.get('artifact_files',[]):
        path=Path(item)
        if not path.is_absolute() or path.is_symlink() or not path.is_file():
            raise ValueError('selected evidence must be an existing absolute regular file')
        resolved=path.resolve()
        if not any(resolved==Path(root).resolve() or Path(root).resolve() in resolved.parents for root in CONFIG['scope_roots']):
            raise ValueError('selected evidence outside approved workspace')
        paths.append(resolved)
    return candidate,paths


def _artifact_metadata(response,*,logical_name,role):
    value=response['artifact']
    if value['logical_name']!=logical_name:raise ValueError('artifact name mismatch')
    return {'artifact_ref':value['artifact_ref'],'artifact_digest':value['artifact_digest'],
            'logical_name':logical_name,'role':role}
