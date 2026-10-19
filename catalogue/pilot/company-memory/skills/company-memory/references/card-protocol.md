# Company Memory task CARD protocol

Company Memory runs as part of the work, without separate user commands to read
or save. An approved connection defines the scope; it is not permission to copy
an entire conversation or to exceed the client's rights.

## Browser and Cloud Work: server CARD

Choose one delivery owner for the task. If the host supplies CARD.md and native
lifecycle instructions, keep that local runtime and its Stop delivery. Otherwise,
use the remote lifecycle below, automatically, without a separate save request.
Never create both a local and a remote CARD for the same task.

1. Call company_memory_account. When approval is needed, request connect once
   and show the consent link. After approval, call company_memory_task_begin
   with a concise description of the actual task. It retrieves authorized exact
   sources and issues the task identity. If several writable destinations exist,
   use the user's selected memory and zone; do not guess. Read-only mode returns
   context without storing a CARD or allowing publication.
2. Keep the returned task_handle. On interruption/compaction use
   company_memory_task_resume with that exact handle. Do not invent task IDs,
   select the latest account task or join unrelated chats by topic.
3. As useful work progresses, call company_memory_card_update with the current
   revision and operation_key. Supply changed fields, a complete useful Markdown
   body, and a factual summary. The server preserves all other OKF fields and
   computes hashes and bytes. Record the request, result, evidence, limitations
   and vfp.status/statement before the final answer. Text evidence can be supplied
   as text_artifacts [{name, text}]. Keep each request below 48 KiB including JSON;
   a stored CARD can be larger through separate field updates. Never pass a
   sandbox download link as if it were uploaded file bytes.
4. Only for an actually obtained outcome call company_memory_task_finish with
   the exact revision and finalize_key. The server uses the existing checker
   and publication queue. Resume/retry the same key after an uncertain response;
   do not start a replacement task or change the payload to evade uncertainty.
5. Use company_memory_status for the returned job and fresh search/fetch under
   the server-issued task ID before claiming accepted visible publication.
   Pending work stays a draft. Keep the substantive answer, not bookkeeping.

This is model-triggered automation. A server snapshot does not attest that the
host completed its turn, and remote MCP does not install host hooks. Respect an
explicit instruction not to retain material: use authorized read tools without
creating a server CARD. A writable grant does not authorize republishing private
source material to a broader audience.

## Native start and resume

Before a substantive task, use the host's existing task/CARD runtime. Read its
CARD.md and INSTRUCTIONS.md. Use the runtime's task identity, never replace it
with an identity invented by the model. Retrieve relevant approved sources with
that identity and fetch the exact sources before relying on them. A new chat
does fresh retrieval; it must not assume another chat's context is present.

After compaction, reread CARD and its instructions instead of reconstructing the
task from guesses. Carry forward previous decisions and unknown fields.

## Full CARD, not a short note

Maintain the full OKF draft throughout the task. Required vocabulary follows the
existing Company Memory CARD runtime: type, title, description, resource, tags,
timestamp, generated, verified, status, concept_id, entity, sensitivity,
knowledge_status, epistemic_class, confidence, significance, valid_from, valid_to,
sources, source_refs, source_hashes, producer_id, critic_id, policy_id,
authority_mode, supersedes, relations, runtime, parameters, computation, executor,
attester, vfp and the runtime-owned routing block (_pilot).

Do not flatten this to title/body/summary or silently discard unfamiliar fields.
Keep status=draft, knowledge_status=draft and verified=[] while the agent edits.
The checker owns accepted status and verification; the agent cannot award them.

Before each final answer update title, description, request, actual result,
evidence, limitations and _pilot.summary. Select only evidence needed to verify
this result in _pilot.artifact_files; an optional work inventory is not an upload
manifest. Preserve the working files.

Classify the actual current VFP:

- not_requested: statement and body contain `VFP не запрашивался и не получен`.
- not_obtained: a result was requested but was not achieved.
- pending: work is incomplete or its evidence is not yet established.
- obtained: the concrete requested result was achieved, with evidence and limits.

Historical notes do not override the current factual classification. Never invent
a successful result, a useful lesson, evidence, consent or a receipt.

## Completion and publication

Only obtained permits the native completion seal. Use the installed runtime's
mark-done operation after the last edit. It binds the current session/turn, CARD
bytes and selected evidence hashes. Later edits invalidate that seal. Stop then
snapshots and delivers the exact CARD and evidence through the existing checker.
Unfinished cards remain drafts. A seal or upload is not accepted publication.

Do not submit the same result a second time through MCP when native Stop owns
delivery. Read-only clients may retrieve context but cannot publish. Respect an
explicit opt-out from retention. Do not ask for a fresh save request for every
completed result within already approved read+submit scope.

Queued, checking, reconciling and index_pending are not saved. Reconcile the same
operation after uncertainty; keep its key and bytes unchanged. Accepted visible
publication requires its receipt and fresh search/fetch readback. Keep the user's
substantive answer, useful links and limitations; do not replace it with a memory
acknowledgement or expose internal bookkeeping.

## Transport capability boundary

The package includes the existing CARD runtime and lifecycle hooks. Native hosts
must load and trust the hooks and provide Python3, PyYAML and filelock. A remote
MCP connection alone cannot install hooks on another host. Confirm the actual
host integration before claiming automatic task entry or completion.

Use `company_memory_card_upload` and `company_memory_card_download` for complete
CARD bytes and selected evidence, then `company_memory_card_finalize` through
the existing checker. The legacy submit tool remains a bounded note interface.
Do not replace full CARD publication with a short note. Read-only access never
permits artifact upload or publication.

Artifacts are data only. Executables, scripts, generic archives and active
formats are rejected server-side, including recognized executable bytes with a
misleading filename. Do not rename a rejected file to bypass that policy. Use a
plain-text description or non-executable evidence instead. Stored artifacts have
POSIX0600 permissions and reside on noexec storage. This restriction does not
apply to the reviewed plugin runtime distributed by the publisher.

This protocol reuses the existing CARD runtime, storage, checker and router.
A deterministic hook/transport fixture does not prove model-level autonomous
adoption. Report that distinction accurately when testing a host.
