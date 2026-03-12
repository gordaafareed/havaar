# havaar

A communication bridge for one-way phone call environments.
Built for situations where internet is cut but outbound mobile calls are still possible.

---

## ⚠ important — read before using

**This tool does not guarantee safety, anonymity, or security for anyone using it.**

- Calls made through this system pass through Twilio's infrastructure. Twilio is a US company and complies with legal requests. Call records, phone numbers, and audio may be accessible to third parties under legal compulsion.
- Phone numbers are visible to the server operator. If you run this, you are responsible for protecting that data.
- This tool is intended for personal use between people who trust each other. It is not designed for large-scale anonymous communication.
- Running this does not make you or callers anonymous.
- If you are in a dangerous situation, assess your risk carefully before using any digital tool.
- The author of this software take no responsibility for how it is used or any consequences that result.

**Use it to stay in touch with people you know and trust. Nothing more.**


---

## features

- **two-way async voice messaging** — operator replies play automatically on the caller's next call
- **broadcast channel** — operator records one message that all callers hear when they press 2
- **panic button** — caller presses 9 → 99 to silently send an emergency alert to the operator
- **telegram notifications** — operator receives a notification with the audio file on every new message (optional)


---

## how it works

```
Sheereen
  → dials a twilio number (regular phone call, no internet needed)
  → hears any messages Farhad has recorded for her since she last called
  → navigates the menu: leave a message, hear announcements, or send a panic alert
  → leaves a voice message

Farhad
  → opens the dashboard
  → listens to Sheereen's messages
  → records a reply — it will play for Sheereen next time she calls
  → receives a Telegram notification with the audio when a new message arrives

  or

  → records a broadcast so anyone calling the number can hear it
```


---


## requirements

- Python 3.9+
- ffmpeg (for audio conversion)
- A Twilio account and phone number (paid, not trial)
- One of the three deployment options below
- Optional: a Telegram bot for notifications

---

## getting a twilio number

1. Go to [twilio.com](https://twilio.com) and create a **personal** account (not business)
2. Upgrade to pay-as-you-go — add a credit card ($20 minimum top-up)
3. Go to **Phone Numbers → Manage → Buy a Number**
4. Buy a number (~$1/month + usage)
5. You'll need three things from your Twilio dashboard:
   - **Account SID** — found on the main dashboard
   - **Auth Token** — found on the main dashboard (click to reveal)
   - **Phone Number** — in E.164 format e.g. `+12015550123`

You'll set the webhook URL after you get your server running.

---

## setup

Clone the repo and copy the example env file:
```bash
git clone https://github.com/gordaafareed/havaar.git
cd havaar
cp .env.example .env
```

Edit `.env` with your credentials:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
DASHBOARD_PASSWORD=choose-a-strong-password

# optional — telegram notifications
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
```

---


## telegram notifications (optional)

To receive Telegram notifications with audio on every new message:

1. Open Telegram and message `@BotFather`
2. Send `/newbot` and follow the steps to create a bot
3. Copy the bot token
4. Search for your new bot and send it a message (any message)
5. Open `https://api.telegram.org/botYOUR_TOKEN/getUpdates` in a browser
6. Copy the `chat.id` value from the response
7. Add both to your `.env`:
```
TELEGRAM_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

When a caller leaves a message you'll receive a Telegram notification with the caller ID and a playable voice message.

---

## panic button

Callers can send a silent emergency alert by pressing **9** during the main menu, then **99** to confirm.

---

## broadcast channel

The operator can record a message that all callers hear when they press 2.

In the dashboard sidebar:
1. Click **record** under the broadcast section
2. Preview the recording
3. Add a title/note
4. Click **publish**

To take it down, click **take down**.

---

## deployment options

### tier 1 — laptop (easiest)

Best for: personal use, occasional availability, testing.

Limitations: server only runs while your laptop is on. The public URL changes every restart.

**Prerequisites:** install cloudflared and ffmpeg
```bash
# ffmpeg (mac)
brew install ffmpeg

# cloudflared (mac apple silicon)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.tgz -o cloudflared.tgz
tar -xzf cloudflared.tgz && sudo mv cloudflared /usr/local/bin/ && rm cloudflared.tgz

# cloudflared (mac intel)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz -o cloudflared.tgz
tar -xzf cloudflared.tgz && sudo mv cloudflared /usr/local/bin/ && rm cloudflared.tgz

# cloudflared (linux)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared
```

**Run:**
```bash
./scripts/start.sh
```

The script will start a Cloudflare tunnel, print your public URL, and start the server.

**After each restart**, copy the new webhook URL and update it in Twilio:
- Twilio Console → Phone Numbers → your number → Voice Configuration
- Set **A call comes in** → Webhook → paste the URL → save

---

### tier 2 — vps (recommended)

Best for: reliable 24/7 availability. Fixed URL that never changes.

**Getting a VPS:**
1. Go to [hetzner.com](https://hetzner.com), [digitalocean.com](https://digitalocean.com), or [vultr.com](https://vultr.com)
2. Create the cheapest instance (~$4-6/month), choose **Ubuntu 22.04**
3. Add your SSH key, note the server IP

**Deploy:**
```bash
./scripts/deploy.sh root@your-server-ip
```

**Set the Twilio webhook** (one time only):
- Twilio Console → Phone Numbers → your number → Voice Configuration
- Set **A call comes in** → Webhook → `http://your-server-ip:5050/twilio/incoming` → save

**Useful commands:**
```bash
# check status
ssh root@your-server-ip 'systemctl status havaar'

# view live logs
ssh root@your-server-ip 'journalctl -u havaar -f'

# restart
ssh root@your-server-ip 'systemctl restart havaar'

# update
rsync -az --exclude '.venv' --exclude 'recordings' --exclude '.env' ./ root@your-server-ip:/opt/havaar/
ssh root@your-server-ip 'systemctl restart havaar'
```

---

## using the dashboard

Open `http://localhost:5050` (or your server IP if using vps) in your browser.


---

## security notes

- If running on a VPS, consider putting it behind a firewall or reverse proxy with HTTPS
- Recordings are stored locally in `recordings/`
- Telegram notifications include the caller's phone number

---

## contributing

PRs welcome.

---

## license

MIT — see [LICENSE](LICENSE).