---
name: company-memory
description: Use automatically before substantive tasks and before delivering their results. Retrieve approved shared context and maintain the full task CARD through the existing independent publication workflow, without separate search or save commands.
---

Use the connected Company Memory MCP tools with the user's OAuth identity.
Never request a password or token in chat or ask the user to edit a config.

This is the automatic task-memory lifecycle. Do not wait for the user to say
"search memory" or "save this". Read `references/card-protocol.md` before the
first work task. Keep the user's substantive answer intact; memory bookkeeping
does not replace it. A read-only grant permits retrieval, not publication.

Choose the lifecycle before proceeding: if this host supplies a local CARD and
native hook instructions, follow them and use native Stop delivery. In ChatGPT
web, Cloud Work or another MCP-only client, use task_begin, task_resume,
card_update and task_finish as described in references/card-protocol.md. This
remote path creates the full CARD on the server and supplies the task ID; it
does not require local files, Python, base64 encoding or a made-up task ID.
The numbered steps below describe shared consent/readback rules and the native
transport fallback. Never duplicate delivery between the two modes.

1. On first use, finish the host's normal browser OAuth connection. Call
   company_memory_account. If there is no accessible workspace, direct the user
   to https://memory.ai4.sale/connect to choose **Create workspace**
   or **I have an invitation code**. An invitation joins existing shared memory;
   installing this plugin or signing in does not create a separate memory.
2. Let the user choose an authorized memory, zones and capabilities. Use
   company_memory_connect once for the normal consent flow and present the returned
   approval link to the user. Wait for their approval; do not grant it on their
   behalf or keep opening login/approval pages. Each client has its own
   ID; multiple clients and accounts may share the same memory. Do not grant
   access to a different workspace as a workaround for a permission denial.
3. Before reasoning about a substantive task, search with the runtime-bound task_id;
   fetch exact returned references under
   the same task. Cite the sources supporting your answer. Never crawl private
   corpora or credentials to bypass the tools' authority.
4. Update the complete task CARD before answering. For a completed, evidenced
   result, preserve it automatically within the approved writable memory and zone;
   no separate save request is required. If the installed CARD runtime delivers
   it, seal it through that runtime and let Stop deliver; never double-submit.
   The bundled hooks run the existing CARD protocol after normal host trust.
   Check account.card_protocol for the actual enabled transport. When delivering
   through MCP directly, upload the complete CARD.md and selected evidence with
   company_memory_card_upload; keep all OKF fields. Finalize obtained VFP with
   company_memory_card_finalize, the fresh same-task same-zone receipt and a
   stable request_key. Preserve artifact receipts and key on retries. The legacy
   submit_for_review note tool is not a substitute for full CARD delivery.
   A pending or unsuccessful result stays a draft. Never invent a successful VFP
   or mark your own content independently verified. Honour an explicit request
   not to retain material. Do not pretend MCP-only transport installs CARD hooks.
5. Read company_memory_status. Queued, checking and index_pending are not
   accepted publication. Confirm acceptance and exact source readback before
   saying the result is saved. Reconcile an uncertain submission before retrying.
6. The account portal manages invitations and individual client revocation.
   Revoking one client does not delete the shared memory. Removing the plugin
   does not erase shared sources. Correction/deletion needs explicit user intent
   and the currently authorized server tools.

Keep catalogue onboarding on /connect. Do not direct plugin users to checkout,
upgrade or billing pages.

Do not capture whole conversations automatically. This pilot package does not
authorize payments, imply public directory approval or claim paid activation.
