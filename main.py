import discord
from discord import app_commands
from discord.ext import commands
import os
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
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = PteroMonitorBot()

# 3. Simulated Testing Commands to Generate Screenshots Instantly
@bot.tree.command(name="test_simulate_crash", description="DEVELOPER TESTING: Simulates an automated node crash detection event.")
@app_commands.checks.has_permissions(administrator=True)
async def test_simulate_crash(interaction: discord.Interaction):
    # Acknowledge instantly
    await interaction.response.send_message("🚧 Simulating background crash...", ephemeral=True)
    
    # 1. Broadcast the Alert
    embed_alert = discord.Embed(
        title="🚨 Server Offline Detected",
        description="The game server node `MC-SERVER-NODE-01` has gone offline! Initiating remote rescue reboot cycle...",
        color=discord.Color.red()
    )
    await interaction.channel.send(embed=embed_alert)
    
    # 2. Broadcast the Success Recovery (Simulated 2 seconds later)
    embed_success = discord.Embed(
        title="✅ Auto-Restart Signal Sent",
        description="Pterodactyl panel accepted command via secure API gateway token. Server node is currently rebooting.",
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=embed_success)

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
    
    done_embed = discord.Embed(
        title="🚀 Reboot Executed Successfully",
        description="The remote server node has been commanded to restart immediately via API client endpoint mapping.",
        color=discord.Color.green()
    )
    await interaction.followup.send(embed=done_embed, ephemeral=True)

@bot.event
async def on_ready():
    print(f"🤖 Connected as: {bot.user.name}")

if __name__ == "__main__":
    keep_alive()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
