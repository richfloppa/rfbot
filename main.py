import discord
from discord.ext import commands, tasks
import asyncio
import random
import requests
from threading import Thread
from keep_alive import keep_alive

intents = discord.Intents.all()
prefixes = ["r!", "R!"]

storage_directory = 'user_warnings'

bot = commands.Bot(command_prefix=prefixes, intents=intents)

activity_options = ["discord.gg/rfserver", "JOIN NOW", "PREFIX: R!", "R!bot_help"]
activity_index = 0

@bot.event
async def on_ready():
    print(f'{bot.user} is active now! Let him cook.')
    update_activity.start()

@tasks.loop(seconds=7)
async def update_activity():
    global activity_index
    activity = discord.Activity(type=discord.ActivityType.watching, name=activity_options[activity_index])
    await bot.change_presence(activity=activity)
    activity_index = (activity_index + 1) % len(activity_options)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int, member: discord.Member = None):
    """Clear a specified number of messages, optionally from a mentioned user."""
    def is_target(message):
        return member is None or message.author == member

    deleted_messages = await ctx.channel.purge(limit=amount + 1, check=is_target)
    await ctx.send(f'{len(deleted_messages) - 1} messages cleared from {member.display_name if member else "everyone"}.')
  
from discord.ext.commands import has_permissions

@bot.command()
@has_permissions(administrator=True)
async def glovemission(ctx, glove: str, glove_wanter: discord.Member, price: str):
    # Mesajı gönder
    await ctx.send("Glove mission created. <a:sucess:1175024579698233405>")

    # Kanal ID'sini tanımla (Örnek olarak "1120050683161354401")
    channel_id = 1120050683161354401

    # Belirtilen kanala mesajı gönder
    channel = bot.get_channel(channel_id)
    if channel is not None:
        message = f"Get {glove} for {glove_wanter.mention}\nAward: {price} <:robux:1187375949310853191>\n@everyone"
        await channel.send(message)
    else:
        await ctx.send("Channel not found. Please make sure the channel ID is correct.")

@glovemission.error
async def glovemission_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use that command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required arguments. Please use the command as follows: `R!glovemission <glove> @user <price>`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid arguments. Please use the command as follows: `R!glovemission <glove> @user <price>`")

@bot.command()
async def verifym(ctx, member: discord.Member, *, new_name: str):
    if not (ctx.author.guild_permissions.administrator or "Moderator" in [role.name for role in ctx.author.roles]):
        await ctx.send("**You don't have permission to use this command.** ❌")
        return

    if member is None:
        await ctx.send("**Please mention a user to verify.** ❌")
        return

    if not new_name:
        await ctx.send("**Please provide a new nickname for the user.** ❌")
        return  # Exit the command if the new_name is missing

    try:
        # Get or create a role named "Verified Member"
        role = discord.utils.get(ctx.guild.roles, name="Verified Member ✅")
        if role is None:
            role = await ctx.guild.create_role(name="Verified Member ✅")

        # Change the nickname of the specified member
        await member.edit(nick=new_name)

        # Assign the role to the member
        await member.add_roles(role)

        await ctx.send(f"**{member.display_name} has been successfully verified, and their name has been changed.** <a:sucess:1175024579698233405>")
    except Exception as e:
        if "HTTPException" in str(e) and "404 Not Found" in str(e):
            await ctx.send("**User not found.** ❌")
        else:
            await ctx.send(f"**An error occurred: {e}** ❌")

@bot.command()
async def mute(ctx, member: discord.Member, duration: str):
    # Küçük veya büyük harf farkını yok say
    duration = duration.lower()

    # Convert duration to seconds
    if duration.endswith("s"):
        time = int(duration[:-1])
    elif duration.endswith("m"):
        time = int(duration[:-1]) * 60
    elif duration.endswith("h"):
        time = int(duration[:-1]) * 3600
    elif duration.endswith("d"):
        time = int(duration[:-1]) * 86400  # 1 day has 86400 seconds
    else:
        await ctx.send("**Invalid time format. Use 's', 'm', 'h', or 'd' for seconds, minutes, hours, or days.** Example: ```R!mute @user 5m```")
        return

    # Mute rolünü tanımlayın (örnek olarak "Muted")
    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if role is not None:
        if role in member.roles:
            await ctx.send(f"**{member.display_name} is already muted.** ❌")
        else:
            await member.add_roles(role)
            # Unmute after the specified duration
            await asyncio.sleep(time)
            await member.remove_roles(role)
            await ctx.send(f"**{member.display_name} has been muted for {duration}.** <a:sucess:1175024579698233405>")
    else:
        await ctx.send("**Mute role not found. Create a role named 'Muted' first. And make sure the user can't talk.**")

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**Unexpected error, please use the command as:** `R!mute @mention <duration>`")
      
@bot.command()
async def unmute(ctx, member: discord.Member):
    # Mute rolünü tanımlayın (örnek olarak "Muted")
    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if role is not None:
        await member.remove_roles(role)
        await ctx.send(f"**Successfully unmuted** {member.display_name} <a:sucess:1175024579698233405>")
    else:
        await ctx.send("**Member is not muted.**")

@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**Unexpected error please use command as: R!mute @mention**")

@bot.command(name='role')
@commands.has_role('Moderator')
async def give_role(ctx, member: discord.Member, role: discord.Role):
    if role.permissions.administrator:
        await ctx.send("You cannot assign roles with administrator permissions.")
    else:
        await member.add_roles(role)
        await ctx.send(f"Role '{role.name}' has been given to {member.mention}")

@give_role.error
async def give_role_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You don't have the 'moderator' role to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `R!role <member> <role>`")

@bot.command()
async def bot_help(ctx):
    embed = discord.Embed(title='Command List', color=0x00ff00)  # You can change the color as needed

    # Set thumbnail for the embed
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1121779036360806433/1174600560763215972/20231114_203624_0000_1.png?ex=65682f04&is=6555ba04&hm=b44c6b6c1d4c8b09679ce9184')

    # Add command details
    embed.add_field(name='Command 1: Mute',
                    value='```r!mute @user duration```  Mutes the mentioned user for a specified duration (e.g., 3m)',
                    inline=False)

    embed.add_field(name='Command 2: Verify Username Change',
                    value='```r!verifym @user <new username>```  Verifies a username change for the mentioned user',
                    inline=False)

    embed.add_field(name='Command 3: Glove Mission',
                    value='```r!glovemission <glove> @user <price>``` Sends a glove mission request to the mentioned user with the specified glove and price',
                    inline=False)

    embed.add_field(name='Command 4: Unmute',
                    value='```r!unmute @user``` Unmutes the mentioned user',
                    inline=False)

    embed.add_field(name='Command 5: Role',
                    value='```r!role @user <role>```  Gives the specified role to the mentioned user (moderator role required)',
                    inline=False)
    embed.add_field(name='Command 7: Yes No Wheel',
                    
value='```r!yesnowheel``` - Spins a yes no wheel.',
                    inline=False)
    embed.add_field(name='Command 6: Spam',                   value='```r!spam @user {message} {number}``` Sends the specified number of spam messages to the mentioned user with a custom message',
                    inline=False)
    embed.add_field(name='Command 7: Chat Filter Permission',
                    
value='```r!nochatfilter @user``` Give a user no chat filter permission. (10 MINUTES ONLY)',
                    inline=False)
    embed.add_field(name='Command 8: Set nick',
                    
value='```r!setnick @user <new name>``` Set a new nickname for provided user.',
                    inline=False) 
    embed.add_field(name='Command 8: invite',
                    
value='```r!invite``` Get the bot invite link.',
                    inline=False) 
    embed.add_field(name='Command 8: clear messages',
                    
value='```r!clear <number>```',
                    inline=False) 
    # Send the embed
    await ctx.send(embed=embed)

AUTHORIZED_USER_ID = 563033118567563267  # Replace with the authorized user's ID

@bot.command(name='spam')
async def spam(ctx, user: discord.User, *, args: str):
    # Check if the command is used by the authorized user
    if ctx.author.id != AUTHORIZED_USER_ID:
        await ctx.send("This command is only available to the Bot owner. ❌")
        return

    # Split the arguments into message and number
    try:
        message, number = args.rsplit(' ', 1)
        number = int(number)
    except ValueError:
        await ctx.send("Invalid arguments. Please provide a message in quotes and a valid number.", embed=discord.Embed(color=discord.Color.red()))
        return

    # Check if the number is within a reasonable range
    if not (1 <= number <= 1000):  # Adjust the range as needed
        await ctx.send("Please provide a valid number between 1 and 1000.", embed=discord.Embed(color=discord.Color.red()))
        return

    # Get the custom emoji ID
    loading_emoji_id = 1186697776315240448  # Replace with your actual custom emoji ID

    # Send "In progress" message as an embed with the custom emoji
    in_progress_embed = discord.Embed(
        title="Spam in Progress",
        description=f"Sending {number} messages to {user.mention} <a:gatito_loading:{loading_emoji_id}>",
        color=discord.Color.blue()
    )
    in_progress_message = await ctx.send(embed=in_progress_embed)

    # Send the specified number of messages to the user via direct message with the custom message
    try:
        for i in range(number):
            await user.send(f"{message} ({i + 1}/{number})")
    except discord.Forbidden:
        await in_progress_message.delete()
        await ctx.send(f"Failed to send messages to {user.mention}. Make sure user's DMs are open.", embed=discord.Embed(color=discord.Color.red()))
        return
    except discord.errors.NotFound:
        await in_progress_message.delete()
        await ctx.send(f"User {user.mention} not found in the server.", embed=discord.Embed(color=discord.Color.red()))
        return

    # Edit the "In progress" message to indicate success
    success_embed = discord.Embed(
        title="Spam Complete",
        description=f"Successfully sent {number} messages to {user.mention} with the message: ```{message}```",
        color=discord.Color.green()
    )
    await in_progress_message.edit(embed=success_embed)

@bot.command(name='setnick')
async def set_nickname(ctx, member: discord.Member = None, *, new_nickname=None):
    # Check if a user is mentioned
    if member is None:
        # Create an embed with an error message for missing mention
        embed = discord.Embed(
            title='Incorrect Command Usage',
            description='The correct usage of the command is: `!setnick @user new_nickname`',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Check if the command invoker is the mentioned user or has the "manage_nicknames" permission
    if ctx.author == member or ctx.author.guild_permissions.manage_nicknames:
        try:
            await member.edit(nick=new_nickname)
            # Create an embed with a success message
            embed = discord.Embed(
                title='Nickname Change',
                description=f'Nickname for `{member.name}` has been set to **{new_nickname}**',
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            # Create an embed with an error message if the bot doesn't have permission
            embed = discord.Embed(
                title='Permission Error',
                description='I do not have permission to change the nickname.',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    else:
        # Create an embed with an error message if the invoker doesn't have permission
        embed = discord.Embed(
            title='Permission Denied',
            description='You do not have the required permissions to set someone else\'s nickname.',
     
          color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name="nochatfilter")
async def add_role(ctx):
    # Replace 'no_chat_filter' with the actual role name
    role_name = 'no chat filter'

    # Check if the "no chat filter" role exists
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if not ctx.message.mentions:
        await ctx.send("Please mention someone to use this command.")
        return

    user_mention = ctx.message.mentions[0]  # Get the first mentioned user

    if not role:
        await ctx.send(f"The `{role_name}` role does not exist. Please run the command again after the role is created. **Don't forget to add role on your chat filter system's whitelist.**")
        return

    if role in user_mention.roles:
        # If the user already has the role, start a countdown to remove it
        countdown = 600  # seconds
        message = await ctx.send(f"User already has the role. It will be removed in: {countdown}")

        while countdown > 0:
            countdown -= 1
            await asyncio.sleep(1)
            await message.edit(content=f"User already has the role. It will be removed in: {countdown}")

        await user_mention.remove_roles(role)

    else:
        # If the user doesn't have the role, add it and set a timer to remove it
        await user_mention.add_roles(role)
        await ctx.send(f"Role `{role_name}` added to {user_mention.mention}. They will have it for 10 minutes. Use the command again for count.")

        # Wait for 10 minutes and remove the role
        await asyncio.sleep(600)
        await user_mention.remove_roles(role)
        await ctx.send(f"`{role_name}` role removed from {user_mention.mention} after 10 minutes.")

@bot.command()
async def yesnowheel(ctx):
    wheel_messages = [
        "<a:Wheel_No1:1186751183109509251>", "<a:Wheel_No2:1186751246347014205>", "<a:Wheel_No3:1186751293012840519>",
        "<a:Wheel_No4:1186751348759339098>", "<a:Wheel_No5:1186751394921861140>", "<a:Wheel_No6:1186751446096564314>",
        "<a:Wheel_Yes1:1186750739922554951>", "<a:Wheel_Yes2:1186750834621567186>", "<a:Wheel_Yes3:1186750887541100706>",
        "<a:Wheel_Yes4:1186750960194830438>", "<a:Wheel_Yes5:1186751005413617745>", "<a:Wheel_Yes6:1186751061172699227>",
        "<a:Wheel_Yes7:1186751134828863639>", "<a:Wherl_No7:1186751499775246386>"
    ]

    message = await ctx.message.reply(random.choice(wheel_messages))

    await asyncio.sleep(4.1)  # Wait for 4.9 seconds

    # Edit the message based on content
    if "no" in message.content.lower():
        await message.edit(content="<:Wheel_No:1186737609431601162>")
    elif "yes" in message.content.lower():
        await message.edit(content="<:Wheel_Yes:1186737503479279687>")

event_winner = None  # Store the winner information
processing_event = False  # Flag to check if an event is already in progress

@bot.command(name='event')
async def event(ctx, duration, channel_mention):
    global processing_event, event_winner

    # Check if the event is already in progress
    if processing_event:
        return await ctx.send('**Event is already in progress. Wait for the current event to finish.** <a:alert2:1190683481374720010>')

    try:
        # Parse duration
        unit = duration[-1]
        amount = int(duration[:-1])

        if unit == 's':
            time_seconds = amount
        elif unit == 'm':
            time_seconds = amount * 60
        elif unit == 'h':
            time_seconds = amount * 60 * 60
        elif unit == 'd':
            time_seconds = amount * 60 * 60 * 24
        elif unit == 'w':
            time_seconds = amount * 60 * 60 * 24 * 7
        else:
            return await ctx.send('**Invalid duration format. Use** `s, m, h, d, or w`**.**')

        # Parse channel mention
        channel_id = int(channel_mention.strip('<>#'))

    except (ValueError, IndexError):
        return await ctx.send('**Invalid duration or channel mention format.** <a:alert2:1190683481374720010>')

    # Check if the command sender's ID is the allowed ID
    allowed_user_id = 563033118567563267
    if ctx.author.id != allowed_user_id:
        return await ctx.send('**You are not authorized to use this command.** <a:alert2:1190683481374720010>')

    channel = bot.get_channel(channel_id)

    if channel is None:
        return await ctx.send('Invalid channel ID. <a:alert2:1190683481374720010>')

    # Stop the task if it's already running
    if process_channel_messages.is_running():
        process_channel_messages.stop()

    processing_event = True  # Set the flag to indicate that the event is in progress
    event_winner = None  # Reset the winner information

    await ctx.send(f'**Event timer started. I will check the channel after** `{amount}{unit}`**.** <a:sucess:1175024579698233405>')

    # Schedule the task to run once after the specified duration
    await asyncio.sleep(time_seconds)
    await process_channel_messages(ctx, channel)

@tasks.loop(seconds=1)
async def process_channel_messages(ctx, channel):
    global event_winner, processing_event

    # Collect unique messages from the specified channel
    unique_messages = set()
    users_messages = {}

    async for message in channel.history(limit=None):
        if message.author.bot or message.content in unique_messages:
            continue

        unique_messages.add(message.content)

        user = f'{message.author.mention}'

        if user not in users_messages:
            users_messages[user] = 1
        else:
            users_messages[user] += 1

    # Check if there are any messages before trying to find the users with the most messages
    if users_messages:
        # Find the top three users with the most messages
        top_users = sorted(users_messages.items(), key=lambda x: x[1], reverse=True)[:3]

        # Store the winner information
        event_winner = top_users

        # Reset the flag to indicate that the event has finished
        processing_event = False

        # Send the results to the original command channel
        await ctx.send('**Event timer ended. Winners:**\n'
                       f'<:1_:1191665595075280906> {event_winner[0][0]} **with** `{event_winner[0][1]}` **messages.** <:Winner:1191699565850656820>\n'
                       f'<:2_:1191665584836976711> {event_winner[1][0]} **with** `{event_winner[1][1]}` **messages.**\n'
                       f'<:3_:1191665609604341780> {event_winner[2][0]} **with** `{event_winner[2][1]}` **messages.**\n'
                       '<a:811944902610518046:1190683894769528842>')

@bot.command(name='kick')
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    try:
        # Kick the user
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked. Reason: {reason}')
    except Exception as e:
        await send_error_embed(ctx, e)

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await send_error_embed(ctx, "You don't have the necessary permissions to kick members.")

@bot.command(name='ban')
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, duration: int = None, *, reason="No reason provided"):
    try:
        # Ban the user
        if duration:
            await member.ban(reason=reason, delete_message_days=0)
            await ctx.send(f'{member.mention} has been banned for {duration} days. Reason: {reason}')
            await asyncio.sleep(duration * 86400)
            await member.unban(reason="Ban duration expired.")
        else:
            await member.ban(reason=reason, delete_message_days=0)
            await ctx.send(f'{member.mention} has been permanently banned. Reason: {reason}')
    except Exception as e:
        await send_error_embed(ctx, e)

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await send_error_embed(ctx, "You don't have the necessary permissions to ban members.")

async def send_error_embed(ctx, error_message):
    embed = discord.Embed(
        title='Error',
        description=str(error_message),
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command()
async def spoiler(ctx, *, message):

    spoiler_message = '||' + '||'.join([f'{char}||' for char in message])  # Spoil every character individually
    await ctx.send(spoiler_message)
  
import os

@bot.event
async def on_disconnect():
    print("Bot disconnected. Reconnecting...")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Error in {event}: {args[0]}")
    if isinstance(args[0], discord.ConnectionClosed):
        print("Reconnecting...")
        await asyncio.sleep(5)  # Add a delay before attempting to reconnect
        await bot.login(token, bot=True)
        await bot.connect()

token = os.getenv("token")

if token is None:
    print("Error: Token not found in environment variables.")
else:
    bot.run(token)
