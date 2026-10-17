---
name: company-memory
description: Connect this client to a shared Company Memory workspace, retrieve authorized sources and save selected results through the existing publication workflow.
---

Use the connected Company Memory MCP tools with the user's OAuth identity.
Never request a password or token in chat or ask the user to edit a config.

1. On first use, finish the host's normal browser OAuth connection. Call
   company_memory_account. If there is no accessible workspace, direct the user
   to https://portal-stage.ai4.sale/connect to choose **Create workspace**
   or **I have an invitation code**. An invitation joins existing shared memory;
   installing this plugin or signing in does not create a separate memory.
2. Let the user choose an authorized memory, zones and capabilities. Use
   company_memory_connect once for the normal consent flow and present the returned
   approval link to the user. Wait for their approval; do not grant it on their
   behalf or keep opening login/approval pages. Each client has its own
   ID; multiple clients and accounts may share the same memory. Do not grant
   access to a different workspace as a workaround for a permission denial.
3. Search with your own stable task_id; fetch exact returned references under
   the same task. Cite the sources supporting your answer. Never crawl private
   corpora or credentials to bypass the tools' authority.
4. Save only selected material the user asked to preserve. Obtain a fresh
   same-task, same-zone retrieval receipt, then call
   company_memory_submit_for_review with that receipt, the authorized memory
   and zone, and a stable request_key. Preserve text and key on retries.
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
