# Authentication and integration rules

## OAuth identity

Use Google, GitHub and Yandex provider flows through the selected backend integration. Do not assume all three expose identical OIDC claims. Validate the concrete provider flow, state/nonce/PKCE requirements and callback configuration. Provider secrets remain backend-only.

The absence of password registration does not remove the need for an internal user and linked provider identities. Do not automatically merge accounts solely because an unverified email string matches. Keep provider subject identity and account-linking rules explicit. Authorization is checked per backend operation and resource.

## Sessions and clients

For the web, use deliberate server-session and cookie settings, CSRF protection for state-changing operations, and a consistent same-origin/proxy policy. Logout and account changes invalidate relevant state and client caches. Do not put long-lived backend secrets in localStorage or bundles.

For Flutter/Tauri, use a system-browser authorization flow and a backend-controlled single-use return mechanism. Validate deep links and bind the exchange to the initiating session/device flow. Do not put confidential OAuth client secrets in distributed applications.

## Google Calendar

Request only the scopes required by the feature. Separate login consent from additional calendar consent. Handle revocation, expired tokens and duplicate event creation. Do not assume a successful OAuth login automatically grants calendar access.

## Telegram

Choose polling or webhook lifecycle explicitly. Validate webhook authenticity or the documented Mini App initData signature on the server, with freshness checks and replay considerations appropriate to the operation. Do not trust user fields supplied as unsigned query parameters.

Keep bot process dependencies isolated when they conflict with the main worker environment. Bound update processing and handle duplicate delivery. A Telegram identity link must be an explicit authenticated application flow, not a guess from a matching display name.

## Stripe development mode

Use test/sandbox credentials and objects for the hackathon payment demonstration. Do not switch to live mode or invent successful payment results. Verify webhook signatures on the raw received payload, use event/operation idempotency and derive entitlement from verified backend payment state, not a frontend redirect alone.

## Verification

Test callback URLs through the deployed origin and the client actually being demonstrated. Include a denied/revoked/expired flow where the change affects it. Keep token values out of screenshots, demo recordings, logs and evidence attachments.
