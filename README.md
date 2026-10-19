# Company Memory pilot catalogue

This package installs the AI4SALE Pilot catalogue without access to the private platform repository. It contains the plugin manifest, public OAuth configuration and usage instructions. It contains no backend code, passwords, private keys or access tokens.

## Install in Codex

1. With the Codex CLI installed, add this catalogue:

   `codex plugin marketplace add AI4sale/company-memory-plugin`

2. Open Codex after the catalogue has been added.

3. Open the Codex plugin catalogue, select **AI4SALE Pilot**, then **Company Memory** and choose Install/Connect.
4. Complete browser sign-in. Create a workspace or select **I have a connection code** to join an existing workspace.
5. Open the connection approval link returned by the plugin. Choose the memory, allowed zones and requested permissions, then select **Connect this client**.

No JSON editing or token copying is required. Installing the plugin and signing in do not create a memory or grant access. Each client gets its own ID. Multiple clients and accounts can use the same shared memory.

If an unapproved request expires, explicitly ask the plugin to Connect again. The same signed-in client can renew its pending request; owner approval is still required. A revoked client cannot use this to restore access.

## Pilot boundaries

This is a pilot catalogue package, not approval or listing in the public OpenAI directory. Backend service: memory.ai4.sale. The account portal handles workspace plans separately. Do not use real card charges for acceptance testing. Native OAuth, workspace creation, invitation acceptance, reviewed publication, cross-client retrieval and selective revocation were exercised on clawd01. Public-directory review and the final launch acceptance remain pending.

Support: info@ai4.sale

Supplemental material: [native pilot evidence walkthrough](review/README.md).

## Automatic task lifecycle

Native Codex uses the bundled full CARD runtime after normal hook trust. Python 3, PyYAML and filelock must be available on the client. The browser/cloud MCP path maintains the same full CARD on the server. Both use the existing publication checker and scoped permissions; do not deliver one task through both paths. Read-only connections do not save CARDs. Native and browser model-driven acceptance is still in progress; tool availability alone is not proof of automatic completion.
