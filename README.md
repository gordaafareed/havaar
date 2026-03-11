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
- The authors of this software take no responsibility for how it is used or any consequences that result.

**Use it to stay in touch with people you know and trust. Nothing more.**

---

## how it works
```
Sheereen
  → dials a twilio number (regular phone call, no internet needed)
  → hears messages Farhad has recorded for her since she last called
  → beep
  → leaves a voice message

Farhad
  → opens the dashboard
  → listens to Sheereen's messages
  → records a message for Sheereen which will be played for her next time she calls
```

Completely asynchronous. Sheereen only needs a phone.

---

## requirements

- Python 3.9+
- A Twilio account and phone number
- One of the three deployment options below

---

## getting a twilio number

1. Go to [twilio.com](https://twilio.com) and create an account
2. Go to **Phone Numbers → Manage → Buy a Number**
3. Search for a number in any country — US numbers work fine
4. Buy it (~$1/month)
5. You'll need three things from your Twilio dashboard:
   - **Account SID** — found on the main dashboard
   - **Auth Token** — found on the main dashboard (click to reveal)
   - **Phone Number** — the number you just bought, in E.164 format e.g. `+12015550123`

You'll set the webhook URL after you get your server running (step below).

---

## setup

Clone the repo and copy the example env file:
```bash
git clone https://github.com/your-username/havaar.git
cd havaar
cp .env.example .env
```

Edit `.env` with your credentials:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
DASHBOARD_PASSWORD=choose-a-strong-password
```

---

## deployment options

Choose based on your technical level and how reliable you need it to be.

---

### tier 1 — laptop (easiest)

Best for: personal use, occasional availability, testing.

Limitations: the server only runs while your laptop is on. The public URL changes every restart — you'll need to update the Twilio webhook each time.

**Prerequisites:** 

install cloudflared
```bash
# mac (apple silicon)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.tgz -o cloudflared.tgz
tar -xzf cloudflared.tgz && sudo mv cloudflared /usr/local/bin/ && rm cloudflared.tgz

# mac (intel)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz -o cloudflared.tgz
tar -xzf cloudflared.tgz && sudo mv cloudflared /usr/local/bin/ && rm cloudflared.tgz

# linux
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared
```

**Run:**
```bash
./scripts/start.sh

# Alternatively, if you have Docker:
docker-compose up
```

The script will:
- Create a Python virtual environment
- Install dependencies
- Start a Cloudflare tunnel
- Print your public URL and webhook URL
- Start the server

**After each restart**, copy the new webhook URL printed in the terminal and update it in Twilio:
- Twilio Console → Phone Numbers → your number → Voice Configuration
- Set **A call comes in** → Webhook → paste the URL → save

---

### tier 2 — vps (recommended)

Best for: reliable 24/7 availability. The server runs even when your laptop is off. Fixed URL that never changes.

**Getting a VPS:**

1. Go to [hetzner.com](https://hetzner.com) (cheapest) or [digitalocean.com](https://digitalocean.com) or [vultr.com](https://vultr.com)
2. Create the cheapest instance available — ~$4-6/month
3. Choose **Ubuntu 22.04**
4. Add your SSH key during setup
5. Note the server's IP address

**Deploy:**
```bash
./scripts/deploy.sh root@your-server-ip

# Alternatively, if your VPS has Docker:
docker-compose up
```

The script will:
- Copy all files to the server
- Install dependencies
- Start a systemd service
- Print your webhook URL

**Set the webhook in Twilio** (one time, never changes):
- Twilio Console → Phone Numbers → your number → Voice Configuration
- Set **A call comes in** → Webhook → `http://your-server-ip:5050/twilio/incoming` → save

**Useful commands:**
```bash
# check if running
ssh root@your-server-ip 'systemctl status havaar'

# view live logs
ssh root@your-server-ip 'journalctl -u havaar -f'

# restart
ssh root@your-server-ip 'systemctl restart havaar'

# update to latest version
rsync -az --exclude '.venv' --exclude 'recordings' --exclude '.env' ./ root@your-server-ip:/opt/havaar/
ssh root@your-server-ip 'systemctl restart havaar'
```

---

## using the dashboard

Open `http://localhost:5050` in your browser (or your server IP).

**First time setup:**
1. Log in with your `DASHBOARD_PASSWORD`


**When someone calls:**
- They appear in the left sidebar
- Click their number to open the conversation
- Press play to listen to their message
- Optionally add a label (e.g. "Sheereen") to identify them
- Record a reply — it will play on their next call before they leave a new message

Unread calls show a red dot.

---

## security notes

- Change `DASHBOARD_PASSWORD` to something strong before deploying
- If running on a VPS, consider putting it behind a firewall
- Recordings are stored locally in the `recordings/` folder

---

## contributing

PRs welcome

---

## license

MIT — see [LICENSE](LICENSE).
