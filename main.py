import os
import logging
import requests
import dns.resolver
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging Configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 1. Start & Help Interface
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🕵️‍♂️ **OSIANT ADVANCED OSINT BOT**\n\n"
        "Aap niche diye gaye public tools use kar sakte hain:\n\n"
        "🌐 **Network & Web OSINT:**\n"
        "• `/ip <IP>` - IP Location, ISP aur Coordinates\n"
        "• `/dns <Domain>` - DNS Records (A, MX, TXT, NS)\n"
        "• `/headers <URL>` - Website Security Headers Scan\n\n"
        "👤 **Identity & Telecom OSINT:**\n"
        "• `/user <Username>` - Public Social Media Platforms Par Username Search\n"
        "• `/phone <Number>` - Country, Carrier, Timezone (+CountryCode Zaroori)\n\n"
        "💡 *Examples:*\n"
        " `/ip 8.8.8.8`\n"
        " `/phone +919876543210`\n"
        " `/dns example.com`"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# 2. IP Intelligence Tool
async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: `/ip 8.8.8.8`", parse_mode="Markdown")
        return

    ip = context.args[0]
    await update.message.reply_text(f"🔍 Fetching Public Info for IP: `{ip}`...", parse_mode="Markdown")

    try:
        res = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=5).json()
        if res.get("status") == "success":
            info = (
                f"🌐 **IP Address:** `{res.get('query')}`\n"
                f"🏳️ **Country:** {res.get('country')} ({res.get('countryCode')})\n"
                f"🏙️ **City/Region:** {res.get('city')}, {res.get('regionName')}\n"
                f"📮 **ZIP Code:** {res.get('zip')}\n"
                f"🏢 **ISP:** {res.get('isp')}\n"
                f"📡 **Organization:** {res.get('org')}\n"
                f"📍 **Coordinates:** {res.get('lat')}, {res.get('lon')}\n"
                f"⏰ **Timezone:** {res.get('timezone')}\n"
                f"🔒 **Proxy/VPN/Hosting:** {'Haan' if res.get('proxy') or res.get('hosting') else 'Nahi'}"
            )
        else:
            info = f"❌ Error: {res.get('message', 'Invalid IP')}"
    except Exception as e:
        info = f"⚠️ Request Error: {e}"

    await update.message.reply_text(info, parse_mode="Markdown")

# 3. Username Reconnaissance Tool
async def user_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: `/user username`", parse_mode="Markdown")
        return

    username = context.args[0]
    await update.message.reply_text(f"🔎 Checking username `{username}` across public platforms...", parse_mode="Markdown")

    platforms = {
        "GitHub": f"https://github.com/{username}",
        "Telegram": f"https://t.me/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Pinterest": f"https://www.pinterest.com/{username}",
        "DockerHub": f"https://hub.docker.com/u/{username}",
        "Medium": f"https://medium.com/@{username}",
        "Pastebin": f"https://pastebin.com/u/{username}",
        "Vimeo": f"https://vimeo.com/{username}",
        "SoundCloud": f"https://soundcloud.com/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}"
    }

    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for name, url in platforms.items():
        try:
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200:
                results.append(f"✅ **{name}:** [Found]({url})")
            else:
                results.append(f"❌ **{name}:** Not Found")
        except:
            results.append(f"⚠️ **{name}:** Timeout")

    msg = f"👤 **Username Search Report:** `{username}`\n\n" + "\n".join(results)
    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

# 4. Telecom Public Info Tool
async def phone_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: `/phone +919876543210` (Country code zaroori hai)", parse_mode="Markdown")
        return

    number_str = context.args[0]
    try:
        parsed_num = phonenumbers.parse(number_str)
        if not phonenumbers.is_valid_number(parsed_num):
            await update.message.reply_text("❌ Invalid Phone Number format.")
            return

        country_name = geocoder.description_for_number(parsed_num, "en")
        carrier_name = carrier.name_for_number(parsed_num, "en")
        timezones = timezone.time_zones_for_number(parsed_num)

        info = (
            f"📱 **Phone:** `{number_str}`\n"
            f"🏳️ **Country:** {country_name if country_name else 'Unknown'}\n"
            f"📡 **Original Carrier:** {carrier_name if carrier_name else 'Unknown'}\n"
            f"⏰ **Timezones:** {', '.join(timezones)}"
        )
    except Exception as e:
        info = f"⚠️ Parsing Error: {e}"

    await update.message.reply_text(info, parse_mode="Markdown")

# 5. DNS Resolution Tool
async def dns_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: `/dns example.com`", parse_mode="Markdown")
        return

    domain = context.args[0].replace("https://", "").replace("http://", "").split("/")[0]
    await update.message.reply_text(f"🌐 Fetching DNS Records for `{domain}`...", parse_mode="Markdown")

    record_types = ['A', 'MX', 'NS', 'TXT']
    results = []

    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records = [str(r) for r in answers]
            results.append(f"🔹 **{rtype}:**\n`" + "\n".join(records) + "`")
        except Exception:
            results.append(f"🔹 **{rtype}:** No public records found.")

    msg = f"📑 **DNS Report:** `{domain}`\n\n" + "\n\n".join(results)
    await update.message.reply_text(msg, parse_mode="Markdown")

# 6. HTTP Security Headers Scanner
async def headers_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: `/headers example.com`", parse_mode="Markdown")
        return

    url = context.args[0]
    if not url.startswith("http"):
        url = "http://" + url

    try:
        res = requests.get(url, timeout=5)
        headers = res.headers
        server = headers.get("Server", "Hidden/Unknown")
        content_type = headers.get("Content-Type", "Unknown")

        msg = (
            f"🖥️ **HTTP Headers Overview:** `{url}`\n\n"
            f"• **Status Code:** `{res.status_code}`\n"
            f"• **Server:** `{server}`\n"
            f"• **Content Type:** `{content_type}`\n"
        )
    except Exception as e:
        msg = f"⚠️ Connection Error: {e}"

    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN Environment Variable missing!")
        return

    app = Application.builder().token(token).build()

    # Register Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("ip", ip_lookup))
    app.add_handler(CommandHandler("user", user_check))
    app.add_handler(CommandHandler("phone", phone_info))
    app.add_handler(CommandHandler("dns", dns_lookup))
    app.add_handler(CommandHandler("headers", headers_scan))

    print("🚀 Osiant Advanced Bot Active Ho Gaya Hai...")
    app.run_polling()

if __name__ == '__main__':
    main()
  
