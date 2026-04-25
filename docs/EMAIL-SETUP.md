# Email Infrastructure Guide

## Overview
ClaraCare handles both inbound (support/contact) and outbound (alerts/digests) email using a combination of Cloudflare and Brevo (SMTP).

## Inbound (Receiving)
- **Domain**: `claracare.me`
- **Provider**: Cloudflare Email Routing
- **Address**: `support@claracare.me` -> Forwards to developer email

## Outbound (Sending)
Used for:
- Urgent distress alerts to family members
- Weekly wellness digests
- PDF Report delivery

### Configuration
We use **Brevo (formerly Sendinblue)** SMTP Relay.

**Required DNS Records** (already configured on Cloudflare):
- **SPF**: Authorizes Brevo to send for `claracare.me`
- **DKIM**: digital signature for deliverability
- **Brevo Code**: Domain ownership verification

### Environment Variables
Add these to `backend/.env`:
```bash
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=your_brevo_smtp_login
SMTP_PASSWORD=your_brevo_smtp_key
FROM_EMAIL=alerts@claracare.me
```
