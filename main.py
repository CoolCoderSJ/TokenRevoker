import keep_alive
import discord
import os
import time
import discord.ext
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions,  CheckFailure, check
import re
import requests, random
from IPy import IP
from easypydb import DB
from github import Github
g = Github(os.environ['GITHUB_TOKEN'])
repo = g.get_repo("CoolCoderSJ/TokenRevoker")

db = DB("db", os.environ['DB_TOKEN'])
db.autoload = True
db.autosave = True

def Service(token):
	if re.search(r"""[M-Z][A-Za-z\d]{23}.[\w-]{6}.[\w-]{27}""", token):
		return "Discord"
	elif re.search(r"""xapp-[0-9a-zA-Z]-[0-9A-Z]{11}-[0-9]{13}-[0-9a-zA-Z]{24}""", token):
		return "Slack API Key"
	elif re.search(r"""https://hooks.slack.com/services/""", token):
		return "Slack Webhook URL"
	elif re.search(r"""(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)""", token):
		result = re.search(r"""(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)""", token)
		ip = result.group(0)
		ip = IP(ip)
		if ip.iptype() == 'PUBLIC':
			return "IPv4"
		return 'Unknown'
	elif re.search(r"""([0-9a-f]{4}:){7}([0-9a-f]{4})""", token):
		return "IPv6"
	else:
		return "Unknown"


client = discord.Client()

client = commands.Bot(command_prefix = '+')

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name="+services  | SnowCoder ⠕#5223"))
    print(f"Logged in")

@client.command()
async def services(ctx):
	embed = discord.Embed(title="Supported Services-", description="""
**DISCORD**
**Slack API Key**
**Slack Webhook**
**IPv4**
**IPv6**
	""")
	await ctx.send(embed=embed)

@client.event
async def on_message(message):
	await client.process_commands(message)
	if str(message.author.id) in db.data.keys():
		return
	channel = await message.author.create_dm()
	if message.content != "":
		service = Service(message.content)
		if service != "Unknown":
			if service == "IPv4" or service == "IPv6":
				
				await channel.send(f"Uh oh! We detected an {service} in your message! Make sure you stay safe!\n\nMessage Link: {message.jump_url}")
			else:
				token = message.content.split()
				tok = ""
				letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
				for char in range(25):
					tok += random.choice(letters)
				text = ""
				if service == "Slack Webhook URL":
					text = "To make sure that your Webhook URL got revoked visit https://api.slack.com/apps , and make sure that at least one url is revoked for any of the apps."
				if service == "Slack API Key":
					tok = "SLACKTOKEN"
					text = "To make sure that your Webhook URL got revoked visit https://api.slack.com/apps , and make sure that at least one token has revoked for any of the apps."
				try:
					repo.create_file(f"leakedtoken{tok}.txt", f"Hey there!\n\nWe've created this file because a token was reported on Discord, and was asked to be revoked. \n\nGuild: {message.guild.name}\nReporter: {message.author.name}#{message.author.discriminator}\n\nGuessed Service: {service}\nTOKEN: {message}", f"Hey there!\n\nWe've created this file because a token was reported on Discord, and was asked to be revoked. \n\nGuild: {message.guild.name}\nReporter: {message.author.name}#{message.author.discriminator}\n\nGuessed Service: {service}\nTOKEN: {message.content}", branch="leakedtokens")
				except:
					repo.update_file(f"leakedtoken{tok}.txt", f"Hey there!\n\nWe've created this file because a token was reported on Discord, and was asked to be revoked. \n\nGuild: {message.guild.name}\nReporter: {message.author.name}#{message.author.discriminator}\n\nGuessed Service: {service}\nTOKEN: {message.content}", f"Hey there!\n\nWe've created this file because a token was reported on Discord, and was asked to be revoked. \n\nGuild: {message.guild.name}\nReporter: {message.author.name}#{message.author.discriminator}\n\nGuessed Service: {service}\nTOKEN: {message}", branch="leakedtokens")
				await channel.send(f"Hey there!\n\nYou've just leaked a token, but no worries, its been revoked! \n\nGuild: {message.guild.name}\nReporter: {message.author.name}#{message.author.discriminator}\n\nGuessed Service: {service}\n{text}\n\nMessage Link: {message.jump_url}")
	# print(message.attachments)
	if message.attachments != []:
		ocr = os.environ['OCR_KEY']
		for attachment in message.attachments:
			response = requests.get(f"https://api.ocr.space/parse/imageUrl?apikey={ocr}&url={attachment.url}")
			txt = response.text
			service = Service(txt)
			print(service)
			if service != "Unknown":
				if service == "IPv4" or service == "IPv6":
					try:
						await channel.send(f"Uh oh! We detected an {service} in your message! Stay safe!\n\nMessage URL: {message.jump_url}")
					except:
						pass
				else:
					token = txt.split()
					tok = ""
					for char in token[0:10]:
						tok += char
					try:
						repo.create_file(f"leakedtoken{tok}.txt", f"Hey there!\n\nWe've created this file because a token was reported on Discord, and was asked to be revoked. \n\nGuild: {message.guild.name}\nReporter: {message.author.name}#{message.author.discriminator}\n\nGuessed Service: {service}\nTOKEN: {message}", f"Hey there!\n\nWe've created this file because a token was reported on Discord, and was asked to be revoked. \n\nGuild: {message.guild.name}\nReporter: {message.author.name}#{message.author.discriminator}\n\nGuessed Service: {service}\nTOKEN: {txt}", branch="leakedtokens")
					except:
						repo.update_file(f"leakedtoken{tok}.txt", f"Hey there!\n\nWe've created this file because a token was reported on Discord, and was asked to be revoked. \n\nGuild: {message.guild.name}\nReporter: {message.author.name}#{message.author.discriminator}\n\nGuessed Service: {service}\nTOKEN: {txt}", f"Hey there!\n\nWe've created this file because a token was reported on Discord, and was asked to be revoked. \n\nGuild: {message.guild.name}\nReporter: {message.author.name}#{message.author.discriminator}\n\nGuessed Service: {service}\nTOKEN: {message}", branch="leakedtokens")
					await channel.send(f"Hey there!\n\nYou've just leaked a token, but no worries, its been revoked! \n\nGuild: {message.guild.name}\nReporter: {message.author.name}#{message.author.discriminator}\n\nGuessed Service: {service}\n\nMessage Link: {message.jump_url}")
	

@client.command()
async def whitelist(ctx):
	id = str(ctx.author.id)
	if id in db.data.keys():
		await ctx.send("You are already whitelisted.")
	else:
		db[id] = "WHITELIST"
		await ctx.send("You have been whitelisted. You will not be DM'd for any more alerts.")

@client.command()
async def rmwhitelist(ctx):
	id = str(ctx.author.id)
	if id in db.data.keys():
		del db[id]
		await ctx.send("You have been removed from the whitelist.")
	else:
		await ctx.send("You are not whitelisted.")

@client.command()
async def ping(ctx):
	await ctx.send('Pong! {0}'.format(round(client.latency, 1)))

@client.command()
async def revoke(ctx, token):
	service = Service(token)
	if service != "Unknown":
		token = token.split()
		tok = ""
		for char in token[0:10]:
			tok += char
		repo.create_file(f"leakedtoken{tok}.txt", f"Hey there!\n\nWe've created this file because a token was reported on Discord, and was asked to be revoked. \n\nGuild: {ctx.guild.name}\nReporter: {ctx.author.name}#{ctx.author.discriminator}\n\nGuessed Service: {service}\nTOKEN: {tok}", f"Hey there!\n\nWe've created this file because a token was reported on Discord, and was asked to be revoked. \n\nGuild: {ctx.guild.name}\nReporter: {ctx.author.name}#{ctx.author.discriminator}\n\nGuessed Service: {service}\nTOKEN: {tok}", branch="leakedtokens")
		await ctx.send(f"Hey there!\n\You've just leaked a token, but no worries, its been revoked! \n\nGuild: {ctx.guild.name}\nReporter: {ctx.author.name}#{ctx.author.discriminator}\n\nGuessed Service: {service}")
	

keep_alive.keep_alive()
client.run(os.getenv("TOKEN"))
