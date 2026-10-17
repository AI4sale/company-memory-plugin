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

This is a pilot catalogue package, not approval or listing in the public OpenAI directory. Backend service: portal-stage.ai4.sale. The account portal handles workspace plans separately. Do not use real card charges for acceptance testing. The end-to-end pilot acceptance remains in progress.

Support: info@ai4.sale
