# Company Memory: review walkthrough

Use the same shared knowledge across conversations and independently approved
clients. This guide accompanies the video and gives the exact review prompts,
expected tools and observable results.

## Setup

Install Company Memory, connect through OAuth, and choose the existing memory
and General zone. For the supplied review workspace, select **Pilot shared
memory** and approve **Read + Submit**. Use the reviewer account supplied in the
private review form. No credentials are included here.

Open the client's tool activity when checking the result. A fluent answer alone
does not prove that the expected tool ran or that publication succeeded.

## Video chapters

- 00:00 Company Memory by AI 4 SALE
- 00:12 Your guided tour
- 00:26 01 / The interface
- 00:36 02 / Read and write
- 00:47 03 / Memories and zones
- 00:58 04 / Invite a colleague
- 01:07 05 / Connect a client
- 01:18 06 / Update once
- 01:28 07 / Use it everywhere
- 01:38 08 / Your knowledge travels
- 01:50 Complete guide on the website
- 02:03 Review walkthrough / Setup
- 02:16 P1 / Connection
- 02:28 P2 / Search and read
- 02:42 P3 / Submit and check status
- 02:56 P4 / Cross-conversation memory
- 03:08 P5 / Session and reconnection
- 03:23 N1 / No tool needed
- 03:34 N2 / No workspace access
- 03:46 N3 / No workspace access
- 03:58 Walkthrough complete

## Functional checks

### P1: Use the explicitly approved existing Memory

**Ask:** Connect to Company Memory and show the existing Memory and zones I approved.

**Expected tools:** company_memory_connect, company_memory_account

**Check:** Ordinary consent selects an existing Memory and explicit zones/actions. No new Memory, silent permission expansion or private setup. Account output omits token/session diagnostics.

### P2: Find and read a synthetic accepted source

**Ask:** Find the reviewer setup note and open its current accepted source.

**Expected tools:** company_memory_search, company_memory_fetch

**Check:** Own same-task search returns only admitted synthetic sources; fetch returned exact reference, current version/SHA and provenance. No other-zone content.

The prepared source is **Company Memory reviewer setup note**. Its sample facts are project Aurora, owner Nia and blue labels for the October sample milestone.

### P3: Submit one selected result for independent review

**Ask:** Save this selected synthetic conclusion for independent review in my approved General zone.

**Expected tools:** company_memory_search, company_memory_submit_for_review, company_memory_status

**Check:** First retrieve own fresh same-task same-zone KA-v3 receipt; explicitly select zone. Preserve request key and exact text. Queue/index_pending is not accepted or saved. Independent checker outcome is truthful.

Select this text before asking: “Project Aurora uses blue labels for the October sample milestone; the fictional owner is Nia.” Wait for the actual outcome. If rejected or still queued, report that state and do not present it as published.

### P4: Read an accepted result in a new conversation

**Ask:** In this new conversation, retrieve the conclusion accepted in the previous test.

**Expected tools:** company_memory_search, company_memory_fetch

**Check:** Fresh own-task search/fetch finds the exact independently accepted current source without manual previous-chat paste; same source SHA/provenance as accepted publication. No full-chat capture.

### P5: Refresh or explicitly reconnect to the same memory

**Ask:** Reconnect this approved client and read the same reviewer source.

**Expected tools:** company_memory_account, company_memory_connect, company_memory_search, company_memory_fetch

**Check:** Silent token refresh preserves the current approved scope. A new OAuth authorization can create a new connection: explicitly select and approve the same Memory/zones before reading. Shared sources retain their SHA. Use a separate browser profile for a different account. Do not claim 90-day client continuity from server configuration alone.

## No-tool checks

### N1: Self-contained arithmetic does not need shared memory

**Ask:** What is 17 multiplied by 24?

**Expected tools:** None.

**Check:** Answer 408 directly. Do not invoke Company Memory, request a connection, retrieve workspace sources or save the exchange.

### N2: Translate supplied text without accessing a workspace

**Ask:** Translate this sentence into French: The meeting starts at nine.

**Expected tools:** None.

**Check:** Translate the supplied sentence directly. The request needs no company knowledge. Do not invoke Company Memory or save the sentence.

### N3: General knowledge question does not trigger Company Memory

**Ask:** Why does the Moon have phases? Explain it in two sentences.

**Expected tools:** None.

**Check:** Give a general explanation without accessing, connecting to or writing a Company Memory workspace. No workspace-specific information was requested.

## Evidence boundary

The video provides an instructional walkthrough of every submitted scenario,
using actual portal captures and explanatory diagrams. It does not claim a new
live execution of all eight cases in ChatGPT or Codex. Run the cases in the
target client and inspect its tool activity to establish that result.

Official requirement: [OpenAI submission review information](https://developers.openai.com/plugins/deploy/submission#complete-review-information).
Full product guide: https://portal-stage.ai4.sale/support/company-memory
