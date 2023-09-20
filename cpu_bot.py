import discord
import sqlite3
from peewee import Model, CharField, IntegerField, SqliteDatabase

# Replace 'YOUR_BOT_TOKEN' with your actual bot token.
TOKEN = 'MTE1Mzk5NTEzNTM3MDEzMzU4Ng.Gz8Pvm.Ebk2xSH3efJ5wJWzCJVE3ThkxlPcrqxzUHA1UY'

# Replace 'YOUR_CHANNEL_ID' with the ID of your dedicated channel.
CHANNEL_ID = '1096570710639525920'

# Create a Discord client with intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)

# Define a SQLite database
db = SqliteDatabase('cpu_scores.db')

# Define a model for the database table
class CPUScore(Model):
    user_id = IntegerField()
    cpu_name = CharField()
    cinebench_score = IntegerField()
    comment = CharField(null=True)
    cinebench_version = CharField(default='Newest')  # Default value is 'Newest'
    benchmark_type = CharField(default='Multi-core')  # Default value is 'Multi-core'

    class Meta:
        database = db

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the message is in the dedicated channel
    if message.channel.id != int(CHANNEL_ID):
        return
    await message.channel.send(f'Received message from {message.author}: {message.content}')
    if message.content.startswith('benchmark'):
        # Handle the /start command to initiate a new entry
        await message.channel.send('Starting a new entry. Please enter your CPU name:')

        await message.channel.send('Please enter your CPU name:')
        cpu_name = await client.wait_for('message', check=lambda m: m.author == message.author)

        await message.channel.send('Please specify the benchmark type (Multi-core or Single-core), or type "skip" for default (Multi-core):')
        benchmark_type = await client.wait_for('message', check=lambda m: m.author == message.author)
        benchmark_type = benchmark_type.content.capitalize()  # Convert to title case

        if benchmark_type not in ['Multi-core', 'Single-core', 'Skip']:
            await message.channel.send('Invalid input for benchmark type. Please enter "Multi-core," "Single-core," or "skip" for default.')
            return

        await message.channel.send('Please enter your Cinebench score:')
        try:
            cinebench_score = await client.wait_for('message', check=lambda m: m.author == message.author, timeout=30)
            cinebench_score = int(cinebench_score.content)
        except ValueError:
            await message.channel.send('Invalid input. Cinebench score must be a number.')
            return
        except asyncio.TimeoutError:
            await message.channel.send('Timeout. Please try again.')
            return

        await message.channel.send('Please enter an optional comment (or type "skip" to skip):')
        comment = await client.wait_for('message', check=lambda m: m.author == message.author)

        await message.channel.send('Please enter the Cinebench version (e.g., "Newest" or "Older", or type "skip" for default):')
        cinebench_version = await client.wait_for('message', check=lambda m: m.author == message.author)
        cinebench_version = cinebench_version.content.capitalize()  # Convert to title case

        if cinebench_version not in ['Newest', 'Older', 'Skip']:
            await message.channel.send('Invalid input for Cinebench version. Please enter "Newest," "Older," or "skip" for default.')
            return

        # Create a new record in the database
        CPUScore.create(user_id=message.author.id, cpu_name=cpu_name.content, cinebench_score=cinebench_score, comment=comment.content if comment.content.lower() != 'skip' else None, cinebench_version=cinebench_version, benchmark_type=benchmark_type)
        await message.channel.send('Data saved successfully!')

if __name__ == '__main__':
    # Initialize the database and start the bot
    db.connect()
    db.create_tables([CPUScore])
    client.run(TOKEN)