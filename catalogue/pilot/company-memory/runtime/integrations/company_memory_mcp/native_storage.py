"""Server-selected native CARD checkpoints; local files are a durable cache.

No second completion mechanism: Pilot/Stop still owns publication. A pending
checkpoint keeps exact bytes and request identity before any network write.
"""
import hashlib
import json
from pathlib import Path
import urllib.error
import yaml

from filelock import FileLock
from scripts.codex_card_hook_pilot import atomic, encoded, parse_card
from .card_client import CardTransportError


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class NativeStorage:
    def __init__(self, pilot, client, session):
        self.pilot,self.client,self.session=pilot,client,session
        self.folder=pilot.directory(session)
        self.folder.mkdir(parents=True,exist_ok=True)
        self.path=self.folder/'server-storage.json'
        self.card=self.folder/'CARD.md'

    def request(self, **kw):
        return self.client.call('company_memory_native_card',
            {'task_id':self.client.task_id,**self.client.target(),**kw})

    def save(self,state):
        atomic(self.path,encoded(state))

    def restore(self,head,state):
        if self.card.exists() or self.card.is_symlink():raise ValueError('restore would overwrite CARD')
        temp=self.folder/'server-restore.md'
        self.client.download_artifact(head['card_ref'],temp,expected_sha256=head['sha256'],task_id=self.client.task_id)
        raw=temp.read_bytes();_,_,meta,body=parse_card(raw)
        if meta['_pilot']['task_id']!=self.client.task_id:raise ValueError('restored task mismatch')
        evidence=[]
        for i,item in enumerate(head.get('evidence',[])):
            suffix=Path(item['logical_name']).suffix
            target=self.folder/'recovered-evidence'/(str(i)+suffix)
            target.parent.mkdir(parents=True,exist_ok=True)
            self.client.download_artifact(item['artifact_ref'],target,expected_sha256=item['sha256'],task_id=self.client.task_id)
            evidence.append(str(target))
        if evidence:
            meta['_pilot']['artifact_files']=evidence
            raw=('---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---\n'+body+'\n').encode()
        with self.card.open('xb') as out:
            out.write(raw);out.flush();__import__('os').fsync(out.fileno())
        temp.unlink()
        state.update(revision=head['revision'],ack_card_sha=head['sha256'],restored=True)
        self.save(state)

    def deliver_pending(self,state):
        pending=state.get('pending')
        if not pending:return
        # Each exact request/byte snapshot survives an uncertain response.
        refs=[]
        for item in pending['files']:
            path=Path(item['path'])
            if sha(path.read_bytes())!=item['sha256']:raise ValueError('pending checkpoint changed')
            result=self.client.upload_artifact(path,task_id=self.client.task_id,
                target_hub=self.client.config['target_hub'],artifact_key='native-checkpoint:'+sha((item['name']+item['sha256']).encode()),
                logical_name=item['name'])
            refs.append(result['artifact']['artifact_ref'])
        args={'card_ref':refs[0],'evidence_refs':refs[1:],'expected_revision':pending['expected_revision'],
              'operation_key':pending['key']}
        # Persist receipt-bearing request too: upload retry receipts must not
        # accidentally change the idempotency payload.
        if 'request' not in pending:
            pending['request']=args;self.save(state)
        head=self.request(**pending['request'])
        if head['sha256']!=pending['files'][0]['sha256']:raise ValueError('server checkpoint conflict')
        state.update(revision=head['revision'],ack_card_sha=head['sha256'],ack_fingerprint=pending['fingerprint'],
                     status='synced',pending=None,error=None)
        self.save(state)

    def checkpoint(self,state):
        if not self.card.exists():return
        data=self.card.read_bytes();_,_,meta,_=parse_card(data)
        if meta['_pilot']['task_id']!=self.client.task_id:raise ValueError('CARD task mismatch')
        items=[('CARD.md',data)]
        selected=meta['_pilot'].get('artifact_files',[])
        if not isinstance(selected,list) or len(selected)>10:raise ValueError('invalid selected evidence')
        for i,value in enumerate(selected):
            p=Path(value)
            if not p.is_absolute() or p.is_symlink() or not p.is_file():raise ValueError('unavailable selected evidence')
            resolved=p.resolve()
            if not any(resolved==Path(r).resolve() or Path(r).resolve() in resolved.parents for r in self.client.config['scope_roots']):
                raise ValueError('evidence outside approved workspace')
            items.append((f'evidence-{i}{p.suffix}',p.read_bytes()))
        fingerprint=sha(encoded([(name,sha(raw)) for name,raw in items]))
        if state.get('ack_fingerprint')==fingerprint:return
        if 'revision' not in state:
            head=self.request()
            if head['exists'] and head['sha256']!=sha(data):
                raise ValueError('local and server CARD conflict; preserve both')
            state['revision']=head['revision']
        key=sha(encoded([self.client.task_id,state['revision'],fingerprint]))
        snapshots=self.folder/'server-outbox'/key
        files=[]
        for name,raw in items:
            path=snapshots/name;atomic(path,raw)
            files.append({'path':str(path),'name':name,'sha256':sha(raw)})
        state['pending']={'key':key,'expected_revision':state['revision'],'files':files,'fingerprint':fingerprint}
        state['status']='pending';self.save(state)
        self.deliver_pending(state)

    def coordinate(self,policy,event):
        with FileLock(str(self.folder/'server-storage.lock'),timeout=3,mode=0o600):
            state=json.loads(self.path.read_bytes()) if self.path.exists() else {}
            previous=state.get('mode','local')
            mode=policy.get('mode',previous) if policy else previous
            state.update(mode=mode,policy_revision=(policy or {}).get('revision',state.get('policy_revision')))
            self.save(state)
            if mode=='local' and previous=='local' and (self.card.exists() or not state.get('ack_card_sha')):return None
            try:
                if not self.card.exists():
                    if state.get('pending'):
                        # Offline work has priority over the last server ack.
                        raw=Path(state['pending']['files'][0]['path']).read_bytes()
                        atomic(self.card,raw)
                    else:
                        head=self.request()
                        if head['exists']:self.restore(head,state)
                        else:state['revision']=0;self.save(state)
                if mode=='server':
                    self.deliver_pending(state)
                    self.checkpoint(state)
                else:
                    state['status']='local_mode';self.save(state)
            except Exception as exc:
                # Preserve local bytes and exact pending operation; neither
                # silently replace a conflict nor report an unacked save.
                state.update(status='pending' if state.get('pending') else 'not_synced',
                             error=getattr(exc,'details',{}).get('reason_code',type(exc).__name__))
                self.save(state)
                if not self.card.exists():raise
            if event.get('hook_event_name') in ('UserPromptSubmit','SessionStart'):
                return ('CARD storage: '+mode+'. Local CARD is the working/offline cache. '
                        'Server checkpoint state: '+state.get('status','initial')+'. '
                        'Keep updating the existing CARD and using native mark-done/Stop. '
                        'Do not create a second remote-model task or publish twice. '
                        'Only acknowledged checkpoints are recoverable from the server.')
            return None
