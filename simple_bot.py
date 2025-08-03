"""
Simple Discord Verification Bot
Handles user verification by managing roles through commands.
"""

import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv
from web import keep_alive

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ENTRY_ROLE_ID = int(os.getenv('ENTRY_ROLE_ID'))
VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID'))
MEN_ROLE_ID = int(os.getenv('MEN_ROLE_ID'))
WOMEN_ROLE_ID = int(os.getenv('WOMEN_ROLE_ID'))
JAIL_ROLE_ID = int(os.getenv('JAIL_ROLE_ID'))
USER_ID = int(os.getenv('USER_ID'))
MUTE_ROLE_ID = int(os.getenv('MUTE_ROLE_ID'))

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='+', intents=intents, help_command=None)

# Anti-spam tracking
spam_tracker = {}  # {user_id: [timestamps]}
SPAM_THRESHOLD = 3  # Number of failed attempts
SPAM_WINDOW = 30  # Time window in seconds

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    logger.info(f'Commands loaded: {[cmd.name for cmd in bot.commands]}')

@bot.event
async def on_message(message):
    """Monitor messages for spam detection."""
    # Ignore bot messages
    if message.author.bot:
        return
    
    # Check if message starts with command prefix
    if message.content.startswith('+'):
        # List of admin-only commands
        admin_commands = ['men', 'wom', 'hebs', 'unhebs', 'zekir', 'yisclear', 'status', 'unmute']
        
        # Extract command name from message
        command_parts = message.content[1:].split()
        if command_parts:
            command_name = command_parts[0].lower()
            
            # Check if it's an admin command and user is not admin
            if command_name in admin_commands and not message.author.guild_permissions.administrator:
                user_id = message.author.id
                current_time = message.created_at.timestamp()
                
                # Initialize spam tracker for user if not exists
                if user_id not in spam_tracker:
                    spam_tracker[user_id] = []
                
                # Clean old timestamps outside the spam window
                spam_tracker[user_id] = [
                    timestamp for timestamp in spam_tracker[user_id] 
                    if current_time - timestamp < SPAM_WINDOW
                ]
                
                # Add current attempt
                spam_tracker[user_id].append(current_time)
                
                # Check if user exceeded spam threshold
                if len(spam_tracker[user_id]) >= SPAM_THRESHOLD:
                    try:
                        guild = message.guild
                        mute_role = discord.utils.get(guild.roles, id=MUTE_ROLE_ID)
                        
                        if mute_role and mute_role not in message.author.roles:
                            await message.author.add_roles(mute_role, reason=f"Auto-muted for spamming admin commands")
                            
                            # Send warning message
                            embed = discord.Embed(
                                title="🔇 Utilisateur Mute",
                                description=f"{message.author.mention} a été mute automatiquement !",
                                color=discord.Color.red()
                            )
                            embed.add_field(name="Raison", value="Spam des commandes d'administrateur", inline=False)
                            embed.add_field(name="Durée", value="Jusqu'à ce qu'un administrateur vous démute", inline=False)
                            embed.add_field(name="⚠️ Avertissement", value="Ne spammez pas les commandes réservées aux administrateurs !", inline=False)
                            
                            await message.channel.send(embed=embed)
                            
                            logger.info(f"User {message.author} auto-muted for spamming admin commands")
                            
                            # Clear spam tracker for this user
                            spam_tracker[user_id] = []
                            
                            return
                            
                    except Exception as e:
                        logger.error(f"Error auto-muting user {message.author}: {e}")
    
    # Process commands normally
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.MissingPermissions):
        # Only send error message for admins or if not already handled by spam detection
        if ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
        # For non-admins, the spam detection in on_message handles it
    
    elif isinstance(error, commands.CommandNotFound):
        # Ignore unknown commands to avoid spam
        pass
    
    else:
        # Log other errors
        logger.error(f"Command error: {error}")
        await ctx.send("❌ Une erreur s'est produite.")



@bot.command(name='status')
@commands.has_permissions(administrator=True)
async def status(ctx, member: discord.Member):
    """Check verification status of a user."""
    try:
        guild = ctx.guild
        
        # Get roles
        entry_role = discord.utils.get(guild.roles, id=ENTRY_ROLE_ID)
        verified_role = discord.utils.get(guild.roles, id=VERIFIED_ROLE_ID)
        
        has_entry = entry_role in member.roles if entry_role else False
        has_verified = verified_role in member.roles if verified_role else False
        
        # Determine status
        if has_verified:
            status_text = "✅ Vérifié"
            color = discord.Color.green()
        elif has_entry:
            status_text = "⏳ En attente de vérification"
            color = discord.Color.orange()
        else:
            status_text = "❓ Statut inconnu"
            color = discord.Color.red()
        
        embed = discord.Embed(
            title="Statut Utilisateur",
            description=f"Statut pour {member.mention}: {status_text}",
            color=color
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        await ctx.send("❌ Une erreur s'est produite.")

@bot.command(name='men')
@commands.has_permissions(administrator=True)
async def verify_men(ctx, member: discord.Member = None):
    """Verify a user as male by removing entry role and adding men role."""
    try:
        guild = ctx.guild
        
        # If no member mentioned, check if replying to a message
        if member is None:
            if ctx.message.reference and ctx.message.reference.message_id:
                try:
                    referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                    member = referenced_message.author
                except:
                    await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à son message avec +men")
                    return
            else:
                await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à son message avec +men")
                return
        
        # Get roles
        entry_role = discord.utils.get(guild.roles, id=ENTRY_ROLE_ID)
        men_role = discord.utils.get(guild.roles, id=MEN_ROLE_ID)
        
        if not entry_role or not men_role:
            await ctx.send("❌ Rôles introuvables. Vérifiez la configuration.")
            return
        
        # Check if user has entry role
        if entry_role not in member.roles:
            await ctx.send(f"❌ {member.mention} n'a pas le rôle d'arrivant.")
            return
        
        # Check if already has men role
        if men_role in member.roles:
            await ctx.send(f"❌ {member.mention} a déjà le rôle homme.")
            return
        
        # Remove entry role and add men role
        await member.remove_roles(entry_role, reason=f"Verified as male by {ctx.author}")
        await member.add_roles(men_role, reason=f"Verified as male by {ctx.author}")
        
        # Success message
        embed = discord.Embed(
            title="✅ Utilisateur Vérifié (Homme)",
            description=f"{member.mention} a été vérifié comme homme !",
            color=discord.Color.blue()
        )
        embed.add_field(name="Vérifié par", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        
        logger.info(f"User {member} verified as male by {ctx.author}")
        
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de gérer les rôles.")
    except Exception as e:
        logger.error(f"Error verifying user as male: {e}")
        await ctx.send("❌ Une erreur s'est produite.")

@bot.command(name='wom')
@commands.has_permissions(administrator=True)
async def verify_women(ctx, member: discord.Member = None):
    """Verify a user as female by removing entry role and adding women role."""
    try:
        guild = ctx.guild
        
        # If no member mentioned, check if replying to a message
        if member is None:
            if ctx.message.reference and ctx.message.reference.message_id:
                try:
                    referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                    member = referenced_message.author
                except:
                    await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à son message avec +wom")
                    return
            else:
                await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à son message avec +wom")
                return
        
        # Get roles
        entry_role = discord.utils.get(guild.roles, id=ENTRY_ROLE_ID)
        women_role = discord.utils.get(guild.roles, id=WOMEN_ROLE_ID)
        
        if not entry_role or not women_role:
            await ctx.send("❌ Rôles introuvables. Vérifiez la configuration.")
            return
        
        # Check if user has entry role
        if entry_role not in member.roles:
            await ctx.send(f"❌ {member.mention} n'a pas le rôle d'arrivant.")
            return
        
        # Check if already has women role
        if women_role in member.roles:
            await ctx.send(f"❌ {member.mention} a déjà le rôle femme.")
            return
        
        # Remove entry role and add women role
        await member.remove_roles(entry_role, reason=f"Verified as female by {ctx.author}")
        await member.add_roles(women_role, reason=f"Verified as female by {ctx.author}")
        
        # Success message
        embed = discord.Embed(
            title="✅ Utilisateur Vérifié (Femme)",
            description=f"{member.mention} a été vérifiée comme femme !",
            color=discord.Color.pink()
        )
        embed.add_field(name="Vérifié par", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        
        logger.info(f"User {member} verified as female by {ctx.author}")
        
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de gérer les rôles.")
    except Exception as e:
        logger.error(f"Error verifying user as female: {e}")
        await ctx.send("❌ Une erreur s'est produite.")

@bot.command(name='hebs')
@commands.has_permissions(administrator=True)
async def jail_user(ctx, member: discord.Member = None, *, reason: str = "Aucune raison fournie"):
    """Put a user in jail by removing their roles and adding jail role."""
    try:
        guild = ctx.guild
        
        # If no member mentioned, check if replying to a message
        if member is None:
            if ctx.message.reference and ctx.message.reference.message_id:
                try:
                    referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                    member = referenced_message.author
                except:
                    await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à son message avec +hebs")
                    return
            else:
                await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à son message avec +hebs")
                return
        
        # Get jail role
        jail_role = discord.utils.get(guild.roles, id=JAIL_ROLE_ID)
        
        if not jail_role:
            await ctx.send("❌ Rôle de prison introuvable. Vérifiez la configuration.")
            return
        
        # Check if already in jail
        if jail_role in member.roles:
            await ctx.send(f"❌ {member.mention} est déjà en prison.")
            return
        
        # Save current roles (except @everyone, bot roles, and entry role) to a file for restoration
        roles_to_save = [role.id for role in member.roles if role.name != "@everyone" and not role.managed and role.id != ENTRY_ROLE_ID]
        
        # Store user's original roles in a simple text file
        import json
        try:
            with open('jailed_users.json', 'r') as f:
                jailed_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            jailed_data = {}
        
        jailed_data[str(member.id)] = roles_to_save
        
        with open('jailed_users.json', 'w') as f:
            json.dump(jailed_data, f)
        
        # Remove all roles and add jail role
        roles_to_remove = [role for role in member.roles if role.name != "@everyone" and not role.managed]
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove, reason=f"Jailed by {ctx.author}: {reason}")
        await member.add_roles(jail_role, reason=f"Jailed by {ctx.author}: {reason}")
        
        # Success message
        embed = discord.Embed(
            title="🔒 Utilisateur Emprisonné",
            description=f"{member.mention} a été mis en prison !",
            color=discord.Color.red()
        )
        embed.add_field(name="Emprisonné par", value=ctx.author.mention, inline=True)
        embed.add_field(name="Raison", value=reason, inline=True)
        await ctx.send(embed=embed)
        
        logger.info(f"User {member} jailed by {ctx.author} for: {reason}")
        
        # Try to send DM to jailed user
        try:
            dm_embed = discord.Embed(
                title="🔒 Vous avez été emprisonné",
                description=f"Vous avez été mis en prison dans **{guild.name}**.",
                color=discord.Color.red()
            )
            dm_embed.add_field(name="Raison", value=reason, inline=False)
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            logger.info(f"Could not send DM to {member} - DMs disabled")
        
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de gérer les rôles.")
    except Exception as e:
        logger.error(f"Error jailing user: {e}")
        await ctx.send("❌ Une erreur s'est produite.")

@bot.command(name='unhebs')
@commands.has_permissions(administrator=True)
async def unjail_user(ctx, member: discord.Member = None):
    """Remove a user from jail and restore their original roles."""
    try:
        guild = ctx.guild
        
        # If no member mentioned, check if replying to a message
        if member is None:
            if ctx.message.reference and ctx.message.reference.message_id:
                try:
                    referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                    member = referenced_message.author
                except:
                    await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à son message avec +unhebs")
                    return
            else:
                await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à son message avec +unhebs")
                return
        
        # Get jail role
        jail_role = discord.utils.get(guild.roles, id=JAIL_ROLE_ID)
        
        if not jail_role:
            await ctx.send("❌ Rôle de prison introuvable. Vérifiez la configuration.")
            return
        
        # Check if user is in jail
        if jail_role not in member.roles:
            await ctx.send(f"❌ {member.mention} n'est pas en prison.")
            return
        
        # Load saved roles from file
        import json
        try:
            with open('jailed_users.json', 'r') as f:
                jailed_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            jailed_data = {}
        
        user_id = str(member.id)
        
        # Remove jail role first
        await member.remove_roles(jail_role, reason=f"Unjailed by {ctx.author}")
        
        # Restore original roles if they were saved
        if user_id in jailed_data:
            original_role_ids = jailed_data[user_id]
            roles_to_add = []
            
            for role_id in original_role_ids:
                role = discord.utils.get(guild.roles, id=role_id)
                if role:
                    roles_to_add.append(role)
            
            if roles_to_add:
                await member.add_roles(*roles_to_add, reason=f"Restored original roles - Unjailed by {ctx.author}")
            
            # Remove user from jailed data
            del jailed_data[user_id]
            with open('jailed_users.json', 'w') as f:
                json.dump(jailed_data, f)
                
            restored_roles = ", ".join([role.name for role in roles_to_add])
        else:
            # No saved roles found - user gets no additional roles (just removed from jail)
            restored_roles = "Aucun (aucun rôle sauvegardé trouvé)"
        
        # Success message
        embed = discord.Embed(
            title="🔓 Utilisateur Libéré",
            description=f"{member.mention} a été libéré de prison !",
            color=discord.Color.green()
        )
        embed.add_field(name="Libéré par", value=ctx.author.mention, inline=True)
        embed.add_field(name="Rôles restaurés", value=restored_roles, inline=True)
        await ctx.send(embed=embed)
        
        logger.info(f"User {member} unjailed by {ctx.author}, restored roles: {restored_roles}")
        
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de gérer les rôles.")
    except Exception as e:
        logger.error(f"Error unjailing user: {e}")
        await ctx.send("❌ Une erreur s'est produite.")

@bot.command(name='yisclear')
@commands.has_permissions(administrator=True)
async def clear_messages(ctx, limit: int = 100):
    """Clear messages from specific user and bot across all channels."""
    try:
        total_deleted = 0
        channels_processed = 0
        
        def check_message(message):
            # Delete messages from the specified user or from the bot
            return message.author.id == USER_ID or message.author.id == bot.user.id
        
        # Process all text channels in the guild
        for channel in ctx.guild.text_channels:
            try:
                # Check if bot has permission to manage messages in this channel
                if not channel.permissions_for(ctx.guild.me).manage_messages:
                    continue
                    
                # Delete messages matching the criteria
                deleted = await channel.purge(limit=limit, check=check_message)
                total_deleted += len(deleted)
                
                if len(deleted) > 0:
                    channels_processed += 1
                    logger.info(f"Deleted {len(deleted)} messages in channel #{channel.name}")
                    
            except discord.Forbidden:
                logger.warning(f"No permission to delete messages in #{channel.name}")
                continue
            except Exception as e:
                logger.error(f"Error in channel #{channel.name}: {e}")
                continue
        
        # Send confirmation message
        if total_deleted > 0:
            confirmation = await ctx.send(f"🧹 {total_deleted} de vos messages et du bot supprimés dans {channels_processed} salon(s) !")
        else:
            confirmation = await ctx.send("🧹 Aucun message trouvé à supprimer.")
        
        # Delete the confirmation message after 5 seconds
        await confirmation.delete(delay=5)
        
        logger.info(f"User {ctx.author} cleared {total_deleted} messages across {channels_processed} channels")
        
    except Exception as e:
        logger.error(f"Error clearing messages: {e}")
        await ctx.send("❌ Une erreur s'est produite lors de la suppression.")

@bot.command(name='unmute')
@commands.has_permissions(administrator=True)
async def unmute_user(ctx, member: discord.Member = None):
    """Unmute a user by removing the mute role."""
    try:
        guild = ctx.guild
        
        # If no member mentioned, check if replying to a message
        if member is None:
            if ctx.message.reference and ctx.message.reference.message_id:
                try:
                    referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                    member = referenced_message.author
                except:
                    await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à son message avec +unmute")
                    return
            else:
                await ctx.send("❌ Veuillez mentionner un utilisateur ou répondre à son message avec +unmute")
                return
        
        # Get mute role
        mute_role = discord.utils.get(guild.roles, id=MUTE_ROLE_ID)
        
        if not mute_role:
            await ctx.send("❌ Rôle de mute introuvable. Vérifiez la configuration.")
            return
        
        # Check if user is muted
        if mute_role not in member.roles:
            await ctx.send(f"❌ {member.mention} n'est pas mute.")
            return
        
        # Remove mute role
        await member.remove_roles(mute_role, reason=f"Unmuted by {ctx.author}")
        
        # Success message
        embed = discord.Embed(
            title="🔊 Utilisateur Démute",
            description=f"{member.mention} a été démute !",
            color=discord.Color.green()
        )
        embed.add_field(name="Démute par", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        
        logger.info(f"User {member} unmuted by {ctx.author}")
        
        # Clear spam tracker for this user
        if member.id in spam_tracker:
            spam_tracker[member.id] = []
        
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de gérer les rôles.")
    except Exception as e:
        logger.error(f"Error unmuting user: {e}")
        await ctx.send("❌ Une erreur s'est produite.")

@bot.command(name='zekir')
@commands.has_permissions(administrator=True)
async def zekir_cmd(ctx):
    """Zekir command."""
    await ctx.send("mdr salut c'est zekir je suis puceau")

@bot.command(name='omar')
async def omar_cmd(ctx):
    """Omar command with video."""
    try:
        # Send the video file without text
        video_file = discord.File("zekir_video.mov", filename="omar_video.mov")
        await ctx.send(file=video_file)
        
        logger.info(f"User {ctx.author} used omar command with video")
        
    except FileNotFoundError:
        await ctx.send("❌ Vidéo introuvable.")
        logger.error("zekir_video.mov file not found")
    except Exception as e:
        await ctx.send("❌ Erreur lors de l'envoi de la vidéo.")
        logger.error(f"Error sending video: {e}")

@bot.command(name='help')
async def help_cmd(ctx):
    """Show available commands."""
    embed = discord.Embed(
        title="🤖 Commandes du Bot de Vérification",
        color=discord.Color.blue()
    )
    embed.add_field(name="+men @utilisateur", value="Vérifier un utilisateur comme homme (mention ou réponse)", inline=False)
    embed.add_field(name="+wom @utilisateur", value="Vérifier un utilisateur comme femme (mention ou réponse)", inline=False)
    embed.add_field(name="+hebs @utilisateur [raison]", value="Mettre un utilisateur en prison (mention ou réponse)", inline=False)
    embed.add_field(name="+unhebs @utilisateur", value="Libérer un utilisateur de prison (mention ou réponse)", inline=False)
    embed.add_field(name="+zekir", value="Message de Zekir", inline=False)
    embed.add_field(name="+unmute @utilisateur", value="Démuter un utilisateur (mention ou réponse)", inline=False)
    embed.add_field(name="+omar", value="Envoie une vidéo spéciale", inline=False)
    embed.add_field(name="+yisclear [nombre]", value="Supprimer vos messages et ceux du bot dans tous les salons (défaut: 100)", inline=False)
    embed.add_field(name="+status @utilisateur", value="Vérifier le statut d'un utilisateur", inline=False)
    embed.add_field(name="+help", value="Afficher cette aide", inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    keep_alive()
    bot.run(DISCORD_TOKEN)