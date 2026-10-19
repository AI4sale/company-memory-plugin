"""Native CARD transport over the already approved public OAuth connection.

Credentials stay in the client's existing local store. No login, account
creation, permission approval, raw chat capture, or second model process.
"""
import base64
import hashlib
import json
import mimetypes
from pathlib import Path
import time
import urllib.error
import urllib.request


class CardTransportError(RuntimeError):
    def __init__(self,code,*,retryable=False):
        super().__init__(code)
        self.details={'reason_code':code,'retryable':retryable}


class MCPCardClient:
    def __init__(self,config,task_id):
        self.config,self.task_id=config,task_id
        self.timeout=30

    def bind_codex_session(self,session_id,state_root=None):
        from integrations.codex_memory_session_context import ensure_binding
        if ensure_binding(session_id,state_root)['task_id']!=self.task_id:
            raise CardTransportError('runtime_task_mismatch')
        return self

    def call(self,name,args):
        remaining=getattr(self,'deadline',float('inf'))-time.monotonic()
        if remaining<=0:raise CardTransportError('checkpoint_budget_exhausted',retryable=True)
        endpoint=self.config['endpoint']
        if endpoint!='https://memory.ai4.sale/api/mcp':
            raise CardTransportError('configured_resource_mismatch')
        # Reload each time: Codex owns silent OAuth refresh and may rotate its
        # token between calls. This adapter never changes native credentials.
        path=Path(self.config['credential_file'])
        if path.is_symlink():raise CardTransportError('unsafe_credential_store')
        credentials=json.loads(path.read_text(encoding='utf-8'))
        matches=[v for v in credentials.values() if isinstance(v,dict) and
            v.get('server_name')=='company-memory' and v.get('server_url')==endpoint]
        if len(matches)!=1:raise CardTransportError('native_oauth_connection_unavailable')
        request=urllib.request.Request(endpoint,data=json.dumps({'jsonrpc':'2.0','id':1,
            'method':'tools/call','params':{'name':name,'arguments':args}}).encode(),headers={
            'Content-Type':'application/json','Accept':'application/json, text/event-stream',
            'Authorization':'Bearer '+matches[0]['access_token'],'MCP-Protocol-Version':'2025-03-26'})
        try:
            with urllib.request.urlopen(request,timeout=min(self.timeout,30,remaining)) as response:
                raw=response.read(1024*1024+1)
            if len(raw)>1024*1024:raise CardTransportError('response_too_large')
            result=json.loads(raw)['result']
            value=result['structuredContent']
            if result.get('isError') or value.get('status')=='error':
                raise CardTransportError(value.get('code','memory_request_failed'))
            return value
        except urllib.error.HTTPError as exc:
            raise CardTransportError('oauth_required' if exc.code==401 else 'memory_http_error',
                retryable=exc.code in (429,502,503,504)) from None
        except (urllib.error.URLError,TimeoutError,ConnectionError):
            raise CardTransportError('connection_unavailable',retryable=True) from None

    def target(self):
        return {'memory_id':self.config['memory_id'],'zone_id':self.config['zone_id']}

    def upload_artifact(self,path,*,task_id,target_hub,artifact_key,logical_name=None,media_type=None):
        if task_id!=self.task_id or target_hub!=self.config['target_hub']:
            raise CardTransportError('artifact_scope_mismatch')
        raw=Path(path).read_bytes();sha=hashlib.sha256(raw).hexdigest()
        for offset in range(0,max(1,len(raw)),24576):
            chunk=raw[offset:offset+24576]
            result=self.call('company_memory_card_upload',{'task_id':self.task_id,**self.target(),
                'artifact_key':artifact_key,'sha256':sha,'logical_name':logical_name or Path(path).name,
                'media_type':media_type or mimetypes.guess_type(logical_name or str(path))[0] or 'application/octet-stream',
                'size_bytes':len(raw),'offset':offset,'final':offset+len(chunk)==len(raw),
                'content_b64':base64.b64encode(chunk).decode()})
            if result['status']=='duplicate':break
            if offset+len(chunk)<len(raw) and result.get('next_offset')!=offset+len(chunk):
                raise CardTransportError('artifact_offset_mismatch')
        artifact=result.get('artifact') or {}
        if artifact.get('artifact_digest')!='sha256:'+sha or artifact.get('size_bytes')!=len(raw):
            raise CardTransportError('artifact_receipt_mismatch')
        return result

    def download_artifact(self,reference,destination,*,expected_sha256,task_id,chunk_bytes=32768):
        if task_id!=self.task_id:raise CardTransportError('runtime_task_mismatch')
        raw=bytearray()
        while True:
            part=self.call('company_memory_card_download',{'task_id':task_id,**self.target(),
                'artifact_ref':reference,'offset':len(raw),'max_bytes':chunk_bytes})
            raw.extend(base64.b64decode(part['content_b64'],validate=True))
            if part['eof']:break
            if part['next_offset']!=len(raw) or not part['content_b64']:raise CardTransportError('artifact_offset_mismatch')
        if hashlib.sha256(raw).hexdigest()!=expected_sha256.removeprefix('sha256:'):
            raise CardTransportError('artifact_digest_mismatch')
        Path(destination).write_bytes(raw)
        return {'artifact_digest':'sha256:'+hashlib.sha256(raw).hexdigest()}

    def finalize(self,request,*,format,request_id):
        if format!='codex-bundle' or request['task_id']!=self.task_id:
            raise CardTransportError('completion_scope_mismatch')
        artifacts=[a for a in request['artifacts'] if a['role']=='evidence']
        cards=[a for a in artifacts if a['logical_name']=='CARD.md']
        if len(cards)!=1:raise CardTransportError('exact_card_required')
        result=self.call('company_memory_card_finalize',{'task_id':self.task_id,**self.target(),
            'card_ref':cards[0]['artifact_ref'],'evidence_refs':[a['artifact_ref'] for a in artifacts if a is not cards[0]],
            'request_key':request_id,'executor_access_receipt_id':request['executor_access_receipt_id'],
            'turn_id':request['turn_id']})
        deadline=time.monotonic()+min(self.timeout,60)
        while result['state'] not in ('accepted','returned','probation','quarantined','failed','cancelled'):
            if time.monotonic()>=deadline:raise CardTransportError('card_job_pending',retryable=True)
            time.sleep(2)
            result=self.call('company_memory_status',{'job_id':result['job_id'],**self.target()})
        if result['state']!='accepted' or result['publication_state']!='visible':
            raise CardTransportError('card_not_published')
        # The existing product worker has independently retrieved and read the
        # exact canonical result before visible settlement. Expose those native
        # receipts only on this account's authorized job, never fabricate them.
        proof=result.get('result',{})
        for field in ('memory_receipt_id','retrieve_receipt_id','get_receipt_id'):
            if not proof.get(field):raise CardTransportError('card_readback_receipt_missing')
        return {**{k:request[k] for k in ('task_id','turn_id','executor_id')},
            'submission_id':request_id,'status':'pass','publication_state':'active',
            **{k:proof[k] for k in ('memory_receipt_id','retrieve_receipt_id','get_receipt_id')}}
