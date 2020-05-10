import discord
from discord.ext import commands
import typing
import data
import datetime
import Levenshtein as lev

# client = discord.Client()
bot = commands.Bot(command_prefix='?')

class Globals:
    pass

global_ = Globals()
global_.platform = data.Platform()
global_.branch = -1
global_.section = -1

@bot.event
async def on_ready() -> None:
    await bot.change_presence(activity=discord.Activity(name='command prefix ?', type=discord.ActivityType.watching))
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        await message.channel.send(f'Hi {message.author.mention}, my prefix is `?` and you can call `?help` in the future to get help!')
        # bot.get_channel(message.channel.id).send("Hello")
        # await message.author.send("Hello!")

    await bot.process_commands(message)


@bot.group()
async def branch(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid subcommand.')

@branch.command(name="fork")
async def fork(ctx, branch_id: int = -1, name: str = ""):
    if branch_id == -1:
        await ctx.send("Invalid branch id, appending new branch.")
    if name == "":
        current_datetime = str(datetime.datetime.now())
        current_datetime = current_datetime.replace("-", "")
        current_datetime = current_datetime.replace(":", "")
        current_datetime = current_datetime.replace(".", "")
        current_datetime = current_datetime.replace(" ", "_")
        name = f"new_branch_{len(global_.platform)}_{current_datetime}."
    await ctx.send(f"New branch `{name}` id `{global_.platform.fork(branch_id, name)}`.")

@branch.command(name="display")
async def display(ctx, branch_id: int = -1):
    if 0 <= branch_id <= 1:
        await ctx.send(f"Branch {branch_id} `{global_.platform[branch_id].name}` (protected) - {len(global_.platform[branch_id].sections)} sections.")
    elif branch_id == -1:
        first_line = f"Listing {len(global_.platform)} branches"
        line_limit_exceeded = ", limited to first 30" if len(global_.platform) > 30 else ''
        line = "-" * int((len(first_line) + len(line_limit_exceeded)) * 1.4)
        await ctx.send(first_line + line_limit_exceeded + f":\n{line}\n" + "\n".join([f"Branch {i} `{x.name}` - {len(x.sections)} sections" for i, x in zip(range(30), global_.platform)]) + ".")
    else:
        await ctx.send(f"Branch {branch_id} `{global_.platform[branch_id].name}` - {len(global_.platform[branch_id].sections)} sections.")

@branch.command(name="count")
async def count(ctx):
    await ctx.send(f"{len(global_.platform)} branches.")

@branch.command(name="select")
async def select(ctx, branch_id: int = -1):
    global_.branch = branch_id
    await ctx.send(f"Set branch selector to `{branch_id}`.")

@branch.command(name="selected")
async def selected(ctx):
    await ctx.send(f"Branch selector is `{global_.branch}`.")

@branch.command(name="delete")
async def delete(ctx, branch_id: int = -1):
    global_.branch[branch_id].delete()
    await ctx.send(f"Branch `{branch_id}` deleted.")


@bot.group(name="section")
async def section(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid subcommand.')

@section.command(name="add")
async def add(ctx, section_id: int = -1, name: str = ""):
    if section_id == -1:
        await ctx.send("Invalid section id, appending new section.")
    if name == "":
        current_datetime = str(datetime.datetime.now())
        current_datetime = current_datetime.replace("-", "")
        current_datetime = current_datetime.replace(":", "")
        current_datetime = current_datetime.replace(".", "")
        current_datetime = current_datetime.replace(" ", "_")
        name = f"new_section_{len(global_.platform[global_.branch])}_{current_datetime}."
    await ctx.send(f"New section `{name}` id `{global_.platform[global_.branch].add(name, section_id)}`.")

@section.command(name="swap")
async def swap(ctx, section_id_1: int, section_id_2: int):
    global_.platform[global_.branch].swap(section_id_1, section_id_2)
    await ctx.send(f"Branch id `{section_id_1}` and id `{section_id_2}` swapped.")

@section.command(name="delete")
async def delete(ctx, section_id: int = -1):
    global_.platform[global_.branch][section_id].delete()
    await ctx.send(f"Section `{section_id}` in branch `{global_.branch}` deleted.")

@section.command(name="display")
async def display(ctx, section_id: int = -1):
    if section_id == -1:
        first_line = f"Listing {len(global_.platform[global_.branch])} policies"
        line_limit_exceeded = ", limited to first 30" if len(global_.platform[global_.branch]) > 30 else ''
        line = "-" * int((len(first_line) + len(line_limit_exceeded)) * 1.4)
        await ctx.send(first_line + line_limit_exceeded + f":\n{line}\n" + "\n".join([f"Section {i} `{x.name}` - {len(x.policies_by_id)} policies" for i, x in zip(range(30), global_.platform[global_.branch])]) + ".")
    else:
        await ctx.send(f"Section {section_id} `{global_.platform[global_.branch][section_id].name}` - {len(global_.platform[global_.branch][section_id].policies_by_id)} policies.")

@section.command(name="select")
async def select(ctx, section_id: int = -1):
    global_.section = section_id
    await ctx.send(f"Set section selector to `{section_id}`.")


@bot.group(name="policy")
async def policy(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid subcommand.')


with open("rcbot.keys") as keys:
    key_dict = {}
    for line in keys:
        key = line.split(": ")
        key_dict[key[0]] = key[1]
    bot.run(key_dict["rcbot-alpha"])