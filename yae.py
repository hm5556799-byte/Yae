import discord
from discord.ext import commands
from discord import app_commands
from pymongo import MongoClient

# --- CONFIG ---
import os

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "yae_bot"
COLLECTION_NAME = "points"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# --- DATABASE SETUP ---
cluster = MongoClient(mongodb+srv://harshopbolte99:spaceship@1@moon.5map6bw.mongodb.net/?retryWrites=true&w=majority&appName=Moon)
db = cluster[DB_NAME]
collection = db[COLLECTION_NAME]

# --- HELPER FUNCTIONS ---
def get_points(user_id: int) -> int:
    user = collection.find_one({"_id": user_id})
    return user["points"] if user else 0

def set_points(user_id: int, points: int):
    collection.update_one({"_id": user_id}, {"$set": {"points": points}}, upsert=True)

# --- COMMANDS ---

@tree.command(name="addpoints", description="Add points to a user")
@app_commands.describe(user="User mention or ID", amount="Number of points to add")
async def addpoints(interaction: discord.Interaction, user: discord.User, amount: int):
    current = get_points(user.id)
    new_points = current + amount
    set_points(user.id, new_points)
    await interaction.response.send_message(
        f"✅ Added {amount} points to **{user.name}**. Total: **{new_points}**"
    )

@tree.command(name="leaderboard", description="Show the top 10 users")
async def leaderboard(interaction: discord.Interaction):
    top = collection.find().sort("points", -1).limit(10)
    rows = []
    rank = 1
    async for user_data in top:
        user = await bot.fetch_user(user_data["_id"])
        rows.append(f"{rank}. {user.name} | {user_data['points']}")
        rank += 1
    
    if not rows:
        await interaction.response.send_message("🏆 Leaderboard is empty.")
    else:
        leaderboard_text = "Rank | User | Points\n" + "\n".join(rows)
        await interaction.response.send_message(f"```\n{leaderboard_text}\n```")

@tree.command(name="resetpoints", description="Reset all users' points to 0")
async def resetpoints(interaction: discord.Interaction):
    collection.update_many({}, {"$set": {"points": 0}})
    await interaction.response.send_message("🔄 All points have been reset to 0.")

# --- SYNC COMMANDS ---
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

# --- RUN ---
bot.run(BOT_TOKEN)
