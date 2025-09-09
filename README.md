# Toonami Aftermath EPG Generator for Jellyfin

This project provides a custom XMLTV guide generator for streaming **Toonami Aftermath** (East, Pacific, and Movies) directly in **Jellyfin** using static M3U streams and a dynamic EPG.

It's designed to run easily on Linux-based media servers (like Rock64, Raspberry Pi, etc.) and includes setup for **cron automation**, **channel artwork**, **GIF support**, and **EPG metadata** (title, block, year, rating, episode).

> 🙌 **Contributions are welcome!** If you'd like to improve this project, feel free to open a PR. Let’s keep retro TV alive in Jellyfin!

---

## 🛠 Features

- ✅ Pulls live Toonami Aftermath schedule from the official API
- ✅ Outputs Jellyfin-compatible XMLTV with:
  - Titles and episode names
  - Descriptions with block, year, rating, and episode info
  - Channel icons (animated GIFs supported!)
- ✅ Supports:
  - Toonami East stream
  - Pacific stream (180-minute delay)
  - Movies stream
- ✅ Hourly updates via cron
- ✅ Works with static `.m3u8` tuners

---

## 📁 Project Structure

```
toonami-jellyfin-epg/
├── ta_epg_api.py              # Main Python EPG generator script
├── examples/
│   └── cron-hourly.ta-epg     # Sample cron job for hourly updates
├── LICENSE                    # MIT license
└── README.md                  # This file!
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

### 3. Generate the guide manually

```bash
sudo /usr/local/bin/ta_epg_api.py
```

✅ This creates: `/var/lib/jellyfin/data/ToonamiAftermathGuide.xml`

---

## 🧠 Setup in Jellyfin

### Add M3U Tuner:

Dashboard → Live TV → Tuner Devices → Add M3U Tuner

Example URL:

```
https://raw.githubusercontent.com/kbmystery7/TAM3U8/main/TAM3U8.m3u8
```

Or use your own `.m3u8` pointing to:
- `ta.east`
- `ta.pacific`
- `ta.movies`

### Add XMLTV EPG:

Dashboard → Live TV → TV Guide Data Providers → Add XMLTV

```
Path: /var/lib/jellyfin/data/ToonamiAftermathGuide.xml
```

Channel IDs must match:
- `ta.east`
- `ta.pacific`
- `ta.movies`

Then restart Jellyfin:

```bash
sudo systemctl restart jellyfin
```

---

## ⏲️ Automate with Cron

```bash
sudo tee /etc/cron.d/ta-epg >/dev/null <<EOF
# Update Toonami Aftermath EPG hourly
7 * * * * root /usr/local/bin/ta_epg_api.py >/var/log/ta_epg.log 2>&1
EOF

sudo systemctl reload cron || sudo service cron reload
```

---

## 🐧 Rock64 / Raspberry Pi GitHub Setup (Optional)

1. Generate an SSH key:

```bash
ssh-keygen -t ed54619 -C "example@gmail.com"
cat ~/.ssh/id_ed54619.pub
```

2. Add to GitHub → Settings → SSH Keys

3. Test it:

```bash
ssh -T git@github.com
```

---

## 🙏 Credits

- 👨‍💻 Created by **Jose Bautista** on a Rock64
- 🔍 API reverse-engineered with `curl` and `Python`
- 📺 Inspired by the **Toonami Aftermath** community
- ❤️ Shoutout to Reddit’s r/RetroTVRevival for inspiration
- 🐍 Built with love, Python, gifs, and terminal hustle

---

## 📄 License

MIT License — free to use, modify, share.
