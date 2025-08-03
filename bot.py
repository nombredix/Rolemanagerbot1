"""
Discord Verification Bot
Handles user verification by managing roles through commands.
"""

import discord
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class VerificationBot(commands.Bot):
    """Main bot class for handling verification commands."""
    
    def __init__(self, config):
        """Initialize the bot with necessary intents and configuration."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.config = config
        
    async def on_ready(self):
        """Event triggered when bot is ready."""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Log available text commands
        text_commands = [cmd.name for cmd in self.commands]
        logger.info(f'Available text commands: {text_commands}')
    
    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ User not found. Please mention a valid user.")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("❌ Required role not found. Please check bot configuration.")
        else:
            logger.error(f'Command error: {error}')
            await ctx.send("❌ An error occurred while processing the command.")

    @commands.command(name='verify')
    @commands.has_permissions(manage_roles=True)
    async def verify_user(self, ctx, member: discord.Member):
        """
        Verify a user by removing entry role and adding verified role.
        
        Args:
            ctx: Command context
            member: Discord member to verify
        """
        try:
            guild = ctx.guild
            
            # Get roles from configuration
            entry_role = discord.utils.get(guild.roles, id=self.config.ENTRY_ROLE_ID)
            verified_role = discord.utils.get(guild.roles, id=self.config.VERIFIED_ROLE_ID)
            
            if not entry_role:
                await ctx.send("❌ Entry role not found. Please check bot configuration.")
                return
                
            if not verified_role:
                await ctx.send("❌ Verified role not found. Please check bot configuration.")
                return
            
            # Check if user has entry role
            if entry_role not in member.roles:
                await ctx.send(f"❌ {member.mention} doesn't have the entry role.")
                return
            
            # Check if user already has verified role
            if verified_role in member.roles:
                await ctx.send(f"❌ {member.mention} is already verified.")
                return
            
            # Remove entry role and add verified role
            await member.remove_roles(entry_role, reason=f"Manual verification by {ctx.author}")
            await member.add_roles(verified_role, reason=f"Manual verification by {ctx.author}")
            
            # Send success message
            embed = discord.Embed(
                title="✅ User Verified",
                description=f"{member.mention} has been successfully verified!",
                color=discord.Color.green()
            )
            embed.add_field(name="Verified by", value=ctx.author.mention, inline=True)
            embed.add_field(name="Entry role removed", value=entry_role.name, inline=True)
            embed.add_field(name="Verified role added", value=verified_role.name, inline=True)
            
            await ctx.send(embed=embed)
            
            # Log the verification
            logger.info(f"User {member} verified by {ctx.author} in guild {guild.name}")
            
            # Send DM to verified user (optional)
            try:
                dm_embed = discord.Embed(
                    title="🎉 You've been verified!",
                    description=f"You have been manually verified in **{guild.name}** and now have access to all channels.",
                    color=discord.Color.green()
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                logger.info(f"Could not send DM to {member} - DMs disabled")
                
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage roles. Please check my permissions.")
        except Exception as e:
            logger.error(f"Error verifying user {member}: {e}")
            await ctx.send("❌ An error occurred while verifying the user.")

    @commands.command(name='unverify')
    @commands.has_permissions(manage_roles=True)
    async def unverify_user(self, ctx, member: discord.Member):
        """
        Unverify a user by removing verified role and adding entry role back.
        
        Args:
            ctx: Command context
            member: Discord member to unverify
        """
        try:
            guild = ctx.guild
            
            # Get roles from configuration
            entry_role = discord.utils.get(guild.roles, id=self.config.ENTRY_ROLE_ID)
            verified_role = discord.utils.get(guild.roles, id=self.config.VERIFIED_ROLE_ID)
            
            if not entry_role:
                await ctx.send("❌ Entry role not found. Please check bot configuration.")
                return
                
            if not verified_role:
                await ctx.send("❌ Verified role not found. Please check bot configuration.")
                return
            
            # Check if user has verified role
            if verified_role not in member.roles:
                await ctx.send(f"❌ {member.mention} is not verified.")
                return
            
            # Remove verified role and add entry role
            await member.remove_roles(verified_role, reason=f"Manual unverification by {ctx.author}")
            await member.add_roles(entry_role, reason=f"Manual unverification by {ctx.author}")
            
            # Send success message
            embed = discord.Embed(
                title="🔄 User Unverified",
                description=f"{member.mention} has been unverified.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Unverified by", value=ctx.author.mention, inline=True)
            embed.add_field(name="Verified role removed", value=verified_role.name, inline=True)
            embed.add_field(name="Entry role added", value=entry_role.name, inline=True)
            
            await ctx.send(embed=embed)
            
            # Log the unverification
            logger.info(f"User {member} unverified by {ctx.author} in guild {guild.name}")
                
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage roles. Please check my permissions.")
        except Exception as e:
            logger.error(f"Error unverifying user {member}: {e}")
            await ctx.send("❌ An error occurred while unverifying the user.")

    @commands.command(name='status')
    @commands.has_permissions(manage_roles=True)
    async def check_status(self, ctx, member: discord.Member):
        """
        Check the verification status of a user.
        
        Args:
            ctx: Command context
            member: Discord member to check
        """
        try:
            guild = ctx.guild
            
            # Get roles from configuration
            entry_role = discord.utils.get(guild.roles, id=self.config.ENTRY_ROLE_ID)
            verified_role = discord.utils.get(guild.roles, id=self.config.VERIFIED_ROLE_ID)
            
            has_entry = entry_role in member.roles if entry_role else False
            has_verified = verified_role in member.roles if verified_role else False
            
            # Determine status
            if has_verified:
                status = "✅ Verified"
                color = discord.Color.green()
            elif has_entry:
                status = "⏳ Pending Verification"
                color = discord.Color.orange()
            else:
                status = "❓ Unknown Status"
                color = discord.Color.red()
            
            embed = discord.Embed(
                title="User Status",
                description=f"Status for {member.mention}",
                color=color
            )
            embed.add_field(name="Current Status", value=status, inline=False)
            embed.add_field(name="Has Entry Role", value="Yes" if has_entry else "No", inline=True)
            embed.add_field(name="Has Verified Role", value="Yes" if has_verified else "No", inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error checking status for {member}: {e}")
            await ctx.send("❌ An error occurred while checking user status.")

    @commands.command(name='bothelp')
    async def bot_help(self, ctx):
        """Display help information."""
        embed = discord.Embed(
            title="🤖 Verification Bot Commands",
            description="Manual user verification system",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="!verify @user",
            value="Verify a user (removes entry role, adds verified role)",
            inline=False
        )
        embed.add_field(
            name="!unverify @user",
            value="Remove verification from a user",
            inline=False
        )
        embed.add_field(
            name="!status @user",
            value="Check verification status of a user",
            inline=False
        )
        embed.add_field(
            name="!bothelp",
            value="Show this help message",
            inline=False
        )
        
        embed.set_footer(text="Note: All commands require 'Manage Roles' permission")
        
        await ctx.send(embed=embed)