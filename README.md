# Toonami Aftermath EPG Generator for Jellyfin

This project provides a custom XMLTV guide generator for streaming **Toonami Aftermath** (East, Pacific, and Movies) directly in **Jellyfin** using static M3U streams and a dynamic EPG. It includes the Python script, cron example, and setup instructions for running it on a Linux-based media server (e.g. Rock64, Raspberry Pi, etc.).

---

## 🛠 Features

- Pulls live schedule data from Toonami Aftermath API
- Outputs a Jellyfin-compatible XMLTV file with:
  - Titles, episode names, and air times
  - Descriptions with block name, season/episode, year
  - Channel icons (including animated GIFs)
- Supports:
  - East stream
  - Pacific stream (with delay)
  - Movies stream

---

## 📁 Files

```
toonami-jellyfin-epg/
├── ta_epg_api.py              # Main Python script to generate EPG
├── examples/
│   └── cron-hourly.ta-epg     # Sample cron job for hourly EPG updates
├── LICENSE                    # MIT license
└── README.md                  # You're here
```

---

## 🚀 Installation

### 1. Clone the repo

```bash
git clone https://github.com/Josefbautista94/toonami-aftermath-jellyfin.git
cd toonami-aftermath-jellyfin
```

### 2. Copy the script to your system

```bash
sudo install -m 0755 ta_epg_api.py /usr/local/bin/ta_epg_api.py
```

### 3. Run the script manually to test

```bash
sudo /usr/local/bin/ta_epg_api.py
```

This generates:  
`/var/lib/jellyfin/data/ToonamiAftermathGuide.xml`

---

## 🧠 Set up Jellyfin

### Add M3U tuner

1. Go to **Dashboard → Live TV → Tuner Devices**
2. Add M3U tuner with one of these:
   - Toonami East: `https://raw.githubusercontent.com/kbmystery7/TAM3U8/main/TAM3U8.m3u8`  
   - Or your own custom `.m3u` if hosting locally

### Add XMLTV EPG

1. Still under **Live TV → TV Guide Data Providers**
2. Add XMLTV:
   - Path: `/var/lib/jellyfin/data/ToonamiAftermathGuide.xml`
3. Match the **channel ID** with M3U `tvg-id` (`ta.east`, `ta.pacific`, `ta.movies`)

### Restart Jellyfin

```bash
sudo systemctl restart jellyfin
```

---

## ⏲️ Automate with Cron

Run the script every hour to keep EPG fresh:

```bash
sudo tee /etc/cron.d/ta-epg >/dev/null <<EOF
# Update Toonami Aftermath EPG hourly
7 * * * * root /usr/local/bin/ta_epg_api.py >/var/log/ta_epg.log 2>&1
EOF

sudo systemctl reload cron || sudo service cron reload
```

---

## 🐧 SSH + GitHub Setup (for Rock64)

To push this repo from your Rock64:

```bash
ssh-keygen -t ed25519 -C "Josef.bautista22@gmail.com"
cat ~/.ssh/id_ed25519.pub
```

Add the SSH key to GitHub under **Settings → SSH and GPG Keys**.

Test connection:

```bash
ssh -T git@github.com
```

---

## 🙌 Credits

- Developed by **Jose Bautista** on Rock64
- Inspired by the Toonami Aftermath community
- Reverse-engineered schedule API using Python
- Shoutout to Redditors and tinkerers keeping retro TV alive

---

## 📄 License

This project is open-source and available under the **MIT License**.
