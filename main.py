import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import aiohttp
from flask import Flask
from threading import Thread

# 1. Background Web Server required for Render Free Tier tracking pings
app = Flask('')

@app.route('/')
def home():
    return "PteroMonitor Engine Operational."

def run_web_server():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# 2. Discord Bot Core Engine Configuration
class PteroMonitorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = PteroMonitorBot()

# 3. Secure Pterodactyl API Client Function
async def control_pterodactyl_server(signal):
    """Sends action signals (start, stop, restart) directly to the Ptero Panel API"""
    panel_url = os.getenv("PTERO_PANEL_URL")   
    server_id = os.getenv("PTERO_SERVER_ID")   
    api_key = os.getenv("PTERO_API_KEY")       

    if not all([panel_url, server_id, api_key]):
        print("⚠️ Pterodactyl environmental configuration variables missing.")
        return False

    endpoint = f"{panel_url.rstrip('/')}/api/client/servers/{server_id}/power"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {"signal": signal}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(endpoint, json=payload, headers=headers) as response:
                # Direct HTTP verification avoiding keyword syntax conflicts
                if response.status == 204 or response.status == 200:
                    return True
                print(f"❌ Ptero API returned error status code: {response.status}")
                return False
        except Exception as e:
            print(f"❌ Network connection to Pterodactyl panel failed: {e}")
            return False

# 4. Automated 5-Minute Node Monitoring Loop
@tasks.loop(minutes=5)
async def check_node_health():
    panel_url = os.getenv("PTERO_PANEL_URL")
    server_id = os.getenv("PTERO_SERVER_ID")
    api_key = os.getenv("PTERO_API_KEY")
    alert_channel_id = os.getenv("ALERT_CHANNEL_ID") 

    if not all([panel_url, server_id, api_key, alert_channel_id]):
        return

    channel = bot.get_channel(int(alert_channel_id))
    if not channel:
        return

    endpoint = f"{panel_url.rstrip('/')}/api/client/servers/{server_id}/resources"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(endpoint, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    current_state = data['attributes']['current_state']
                    
                    if current_state in ["offline", "stopped"]:
                        embed = discord.Embed(
                            title="🚨 Server Offline Detected",
                            description="The game server node has gone offline! Initiating remote rescue reboot cycle...",
                            color=discord.Color.red()
                        )
                        await channel.send(embed=embed)
                        
                        success = await control_pterodactyl_server("restart")
                        if success:
                            success_embed = discord.Embed(
                                title="✅ Auto-Restart Signal Sent",
                                description="Pterodactyl panel accepted command via secure API gateway token. Server node is currently rebooting.",
                                color=discord.Color.green()
                            )
                            await channel.send(success_embed)
                else:
                    print(f"Health check scan failed with status: {response.status}")
        except Exception as e:
            print(f"Health loop network failure: {e}")

@bot.event
async def on_ready():
    print(f"🤖 Connected as: {bot.user.name}")
    if not check_node_health.is_running():
        check_node_health.start()

# 5. Interactive Staff Command Center Controls
@bot.tree.command(name="server_restart", description="Manually issues a secure remote reboot command to Pterodactyl.")
@app_commands.checks.has_permissions(administrator=True)
async def manual_restart(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    embed = discord.Embed(
        title="⚙️ Processing Request",
        description="Contacting Pterodactyl Panel secure nodes...",
        color=discord.Color.orange()
    )
    await interaction.followup.send(embed=embed, ephemeral=True)
    
    success = await control_pterodactyl_server("restart")
    if success:
        done_embed = discord.Embed(
            title="🚀 Reboot Executed Successfully",
            description="The remote server node has been commanded to restart immediately via secure API client endpoint mapping.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=done_embed, ephemeral=True)
    else:
        fail_embed = discord.Embed(
            title="❌ Command Execution Failure",
            description="Failed to verify credentials with Pterodactyl panel nodes. Check console logs.",
            color=discord.Color.red()
        )
        await interaction.followup.send(fail_embed, ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ System Error: DISCORD_TOKEN environment property missing.")
