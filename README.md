# PteroNodeMonitor

OMNIPTERO NODE MONITOR & AUTOMATED RECOVERY ENGINE - RECOVERY GUIDE

This enterprise application monitors Pterodactyl game nodes and automated reboots.

ENVIRONMENTAL CONFIGURATION PARAMS REQUIRED (HOSTING SYSTEM WORKSPACE):
1. DISCORD_TOKEN = Your premium Discord developer application authorization token string.
2. PTERO_PANEL_URL = The external URL of your web panel (e.g., https://yourdomain.com).
3. PTERO_SERVER_ID = The identifier string of your targeted server container room.
4. PTERO_API_KEY = Your unique client API access key generated in account settings.
5. ALERT_CHANNEL_ID = The numerical identification sequence of your discord logging room.

DEPLOYMENT INSTRUCTIONS:
- Run 'pip install -r requirements.txt' to pull standard modules.
- Ensure all 3 Privileged Gateway Intents (Presence, Members, Message Content) are switched ON in the Developer Portal.
- Run 'python main.py' to launch the core execution routine thread.
