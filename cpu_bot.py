import asyncio
import os
import discord
from discord.ext import commands
from peewee import Model, CharField, IntegerField, SqliteDatabase

# Get token from docker environment
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
# Get Channel ID from docker environment, else allow all
CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID")

# Create a Discord bot with intents and command support
intents = discord.Intents.default()
intents.typing = False
intents.message_content = True
intents.presences = False
bot = commands.Bot(command_prefix="/", intents=intents)

# Define a SQLite database
db = SqliteDatabase("cpu_scores.db")


# Define a model for the database table
class CPUScore(Model):
    user_id = IntegerField()
    cpu_name = CharField()
    benchmark_type = CharField(
        default="Multi-core"
    )  # Default value is 'Multi-core'
    cinebench_score = IntegerField()
    cinebench_version = CharField(
        default="2024"
    )  # Default value is '2024', the currently newest
    comment = CharField(null=True)

    class Meta:
        database = db


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.command()
async def start(ctx):
    # Check if the command is executed in the dedicated channel
    if ctx.channel.id != int(CHANNEL_ID):
        await ctx.send("Please use this command in the dedicated channel.")
        return

    # Handle the /start command to initiate a new entry
    await ctx.send("Starting a new entry. Please enter your CPU name:")
    await ctx.send("Example: AMD Ryzen 7 5700X or Intel Core i9-11900H")
    user_id = ctx.author.id

    def check(msg):
        return msg.author.id == user_id and msg.channel.id == int(CHANNEL_ID)

    try:
        # Wait for the user to respond with their CPU name
        cpu_name_msg = await bot.wait_for("message", check=check, timeout=300)
        cpu_name = cpu_name_msg.content

        await ctx.send(
            "Please specify the benchmark type (Multi-core or Single-core):"
        )

        # Wait for the user to specify the benchmark type
        benchmark_type_msg = await bot.wait_for(
            "message", check=check, timeout=300
        )
        benchmark_type = benchmark_type_msg.content

        if benchmark_type.lower() not in ("multi-core", "single-core"):
            await ctx.send(
                'Invalid benchmark type. Please use "Multi-core" or "Single-core."'
            )
            return

        await ctx.send("Please enter your Cinebench score:")
        cinebench_score_msg = await bot.wait_for(
            "message", check=check, timeout=300
        )

        try:
            cinebench_score = int(cinebench_score_msg.content)
        except ValueError:
            await ctx.send("Invalid input. Cinebench score must be a number.")
            return

        await ctx.send(
            'Please enter an optional comment (or type "skip" to skip):'
        )
        comment_msg = await bot.wait_for("message", check=check, timeout=300)
        comment = (
            comment_msg.content
            if comment_msg.content.lower() != "skip"
            else None
        )

        await ctx.send(
            'Please enter the Cinebench version (e.g., "R23" or "2024", or type "skip" for default):'
        )
        cinebench_version_msg = await bot.wait_for(
            "message", check=check, timeout=300
        )
        cinebench_version = (
            cinebench_version_msg.content.capitalize()
            if cinebench_version_msg.content != "skip"
            else None
        )

        if cinebench_version.lower() not in ["r23", "2024", "skip"]:
            await ctx.send(
                'Invalid input for Cinebench version. Please enter "R23," "2024," or "skip" for default which is "2024".'
            )
            return

        # Create a new record in the database
        CPUScore.create(
            user_id=user_id,
            cpu_name=cpu_name,
            cinebench_score=cinebench_score,
            comment=comment,
            cinebench_version=cinebench_version,
            benchmark_type=benchmark_type,
        )

        await ctx.send("Data saved successfully!")

    except asyncio.TimeoutError:
        await ctx.send("Entry timed out. Please start a new entry with /start.")


@bot.command()
async def top(
    ctx, benchmark_type: str = "multi-core", cinebench_version: str = "all"
):
    # Check if the command is executed in the dedicated channel
    if ctx.channel.id != int(CHANNEL_ID):
        await ctx.send("Please use this command in the dedicated channel.")
        return

    # Validate the benchmark_type parameter
    if benchmark_type.lower() not in ("multi-core", "single-core"):
        await ctx.send(
            "Invalid benchmark type. Please specify 'multi-core' or 'single-core'."
        )
        return

    # Validate the cinebench_version parameter
    if cinebench_version.lower() not in ("r20", "r23", "all"):
        await ctx.send(
            "Invalid Cinebench version. Please specify 'R20', 'R23', or 'all'."
        )
        return

    # Build the query based on benchmark type and cinebench version
    query = CPUScore.select().where(
        CPUScore.benchmark_type == benchmark_type.lower()
    )

    # If the cinebench_version is not "all", filter the query by the specified version
    if cinebench_version.lower() != "all":
        query = query.where(
            CPUScore.cinebench_version == cinebench_version.upper()
        )

    # Retrieve the top 10 CPU scores based on the specified parameters
    top_scores = query.order_by(CPUScore.cinebench_score.desc()).limit(10)

    if not top_scores:
        await ctx.send(
            f"No {benchmark_type.capitalize()} CPU scores found for {cinebench_version.capitalize()} version in the database."
        )
        return

    # Create a message to display the top scores
    top_message = f"Top 10 {benchmark_type.capitalize()} CPU Scores ({cinebench_version.capitalize()} version):\n"
    for index, score in enumerate(top_scores, start=1):
        if score.comment:
            top_message += f"{index}. {score.cpu_name}, Score: {score.cinebench_score} in {score.cinebench_version}, {score.comment}\n"
        else:
            top_message += f"{index}. {score.cpu_name}, Score: {score.cinebench_score} in {score.cinebench_version}\n"
    await ctx.send(top_message)


if __name__ == "__main__":
    # Initialize the database and start the bot
    db.connect()
    db.create_tables([CPUScore])
    bot.run(TOKEN)
