"""Bootstrap the bundled, reviewed CARD runtime in the plugin data directory."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

ROOT=Path(os.environ['PLUGIN_ROOT']).resolve()
DATA=Path(os.environ['PLUGIN_DATA']).resolve()


def main():
    if os.name!='nt':os.umask(0o077)
    raw=sys.stdin.buffer.read(256*1024+1)
    if len(raw)>256*1024:raise ValueError('hook input too large')
    event=json.loads(raw)
    if event.get('hook_event_name')=='SessionStart' and event.get('source')!='compact':
        print(json.dumps({'continue':True}));return
    runtime=ROOT/'runtime'
    sys.path.insert(0,str(runtime))
    from integrations.company_memory_mcp.card_client import MCPCardClient
    from integrations.codex_memory_session_context import ensure_binding
    from scripts.codex_card_hook_pilot import atomic,encoded,Pilot,load_adapter
    from integrations.company_memory_mcp.native_storage import NativeStorage
    state=DATA/'cards'
    binding=ensure_binding(event['session_id'],state)
    credential_file=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'.credentials.json'
    client=MCPCardClient({'endpoint':'https://memory.ai4.sale/api/mcp','credential_file':str(credential_file)},binding['task_id'])
    cached_path=state/hashlib.sha256(event['session_id'].encode()).hexdigest()[:32]/'native-consumer.json'
    cached=json.loads(cached_path.read_bytes()) if cached_path.exists() else None
    account=None
    if event.get('hook_event_name')!='PreToolUse' or cached is None:
        try:account=client.call('company_memory_account',{})
        except Exception:
            if cached is None:raise
    if account is None and cached:
        consumer=Path(cached['consumer'])
        if DATA/'consumers' not in consumer.parents:raise ValueError('invalid cached runtime')
        config=json.loads((consumer/'memory-client.json').read_bytes())
        pilot=Pilot(consumer,state,load_adapter(consumer),[Path(event['cwd']).resolve()])
        client=MCPCardClient(config,binding['task_id'])
        coordinator=NativeStorage(pilot,client,event['session_id'])
        note=coordinator.coordinate(cached.get('policy'),event)
        result=pilot.hook(event)
        if note:
            output=result.setdefault('hookSpecificOutput',{'hookEventName':event['hook_event_name']})
            output['additionalContext']=output.get('additionalContext','')+'\n'+note
        print(json.dumps(result,ensure_ascii=True));return
    primary=account.get('memory_id')
    routes=[r for r in account.get('card_protocol',{}).get('routes',[]) if r['memory_id']==primary]
    if len(routes)!=1:
        print(json.dumps({'continue':True,'hookSpecificOutput':{'hookEventName':event['hook_event_name'],
            'additionalContext':'Company Memory automatic CARD delivery requires one explicitly selected writable memory zone. Check account and use the approved connection workflow; do not invent a destination or claim the lifecycle is active.'}}));return
    route=routes[0]
    policy=route.get('native_storage',{'mode':'local'})
    route={k:v for k,v in route.items() if k!='native_storage'}
    workspace=Path(event['cwd']).resolve()
    # Separate immutable runtime adapter configuration for this approved scope.
    version=hashlib.sha256((runtime/'scripts/codex_card_hook_pilot.py').read_bytes()+
        (runtime/'scripts/codex_mcp_card_adapter.py').read_bytes()+
        (runtime/'integrations/company_memory_mcp/card_client.py').read_bytes()+
        (runtime/'integrations/company_memory_mcp/native_storage.py').read_bytes()).hexdigest()
    identity=json.dumps([route,str(workspace),version],sort_keys=True).encode()
    consumer=DATA/'consumers'/hashlib.sha256(identity).hexdigest()[:24]
    config={**route,'state_dir':str(state),'scope_roots':[str(workspace),str(state)],
        'endpoint':'https://memory.ai4.sale/api/mcp','credential_file':str(credential_file)}
    consumer.mkdir(parents=True,exist_ok=True)
    cfg=consumer/'memory-client.json'
    if cfg.exists() and json.loads(cfg.read_bytes())!=config:raise ValueError('approved CARD scope changed')
    if not cfg.exists():atomic(cfg,encoded(config))
    # Copy exact public modules, never a private corpus or credential file.
    for relative in ('integrations','scripts'):
        destination=consumer/relative
        if not destination.exists():shutil.copytree(runtime/relative,destination)
    alias=consumer/'scripts/codex_remote_memory_hook.py'
    expected=(runtime/'scripts/codex_mcp_card_adapter.py').read_bytes()
    if alias.exists() and alias.read_bytes()!=expected:raise ValueError('CARD adapter version changed')
    if not alias.exists():atomic(alias,expected)
    activation={'schema_version':'company-memory-codex-pilot-activation.v1','enabled':True,'scope_roots':[str(workspace)]}
    activation_path=state/'activation.json'
    if activation_path.exists():
        previous=json.loads(activation_path.read_bytes())
        activation['scope_roots']=list(dict.fromkeys([*previous.get('scope_roots',[]),str(workspace)]))
    atomic(activation_path,encoded(activation))
    pilot=Pilot(consumer,state,load_adapter(consumer),[workspace])
    atomic(cached_path,encoded({'consumer':str(consumer),'policy':policy}))
    client=MCPCardClient(config,binding['task_id'])
    coordinator=NativeStorage(pilot,client,event['session_id'])
    note=coordinator.coordinate(policy,event)
    result=pilot.hook(event)
    if event.get('hook_event_name')=='UserPromptSubmit':note=coordinator.coordinate(policy,event)
    if note:
        output=result.setdefault('hookSpecificOutput',{'hookEventName':event['hook_event_name']})
        output['additionalContext']=output.get('additionalContext','')+'\n'+note
    print(json.dumps(result,ensure_ascii=True))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        # No credential/body diagnostics enter chat or stderr.
        print(json.dumps({'continue':True,'hookSpecificOutput':{'hookEventName':'UserPromptSubmit',
            'additionalContext':'Company Memory CARD runtime is not ready ('+type(exc).__name__+'). Do not claim automatic reading or saving succeeded. The installed runtime status must be restored.'}}))
