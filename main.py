import os
import shutil
from datetime import datetime

import discord
from botconf import Conf
from cachetools import LRUCache
from contextBot.Bot import Bot
from contextBot.Context import Context
from paradata import BotData

# Configuration file for environment variables.

CONF_FILE = "paradox.conf"

conf = Conf(CONF_FILE)

# ------------------------------
# Read the environment variables

PREFIX = conf.get("PREFIX")

# Discord channel ids for logging endpoints and internal communication
CHEAT_CH = conf.get("CHEAT_CH")
FEEDBACK_CH = conf.get("FEEDBACK_CH")
PREAMBLE_CH = conf.get("PREAMBLE_CH")
BOT_LOG_CH = conf.get("BOT_LOG_CH")
LOG_CHANNEL = conf.get("LOG_CHANNEL")

# Server where the referenced emojis live
EMOJI_SERVER = conf.get("EMOJI_SERVER")

# ------------------------------
# Initialise data
BOT_DATA_FILE = conf.get("BOT_DATA_FILE")
CURRENT_APP = conf.get("APP")

botdata = BotData(BOT_DATA_FILE, app=CURRENT_APP)

# Initialise logs
LOGNAME = conf.get("LOGFILE")
LOGDIR = conf.get("LOGDIR")

LOGFILE = "{}/{}.log".format(LOGDIR, LOGNAME)
LOGFILE_LAST = "{}/{}.last.log".format(LOGDIR, LOGNAME)

if os.path.isfile(LOGFILE):
    if os.path.isfile(LOGFILE_LAST):
        shutil.move(LOGFILE_LAST, "{}/{}{}.log".format(LOGDIR, datetime.utcnow().strftime("%s"), LOGNAME))
    shutil.move(LOGFILE, LOGFILE_LAST)
else:
    with open(LOGFILE, "w") as file:
        pass

# -------------------------------
# Get the valid prefixes in given context


async def get_prefixes(ctx):
    """
        Returns a list of valid prefixes in this context.
        Currently just bot and server prefixes
        """
    prefix = 0
    prefix_conf = ctx.server_conf.guild_prefix
    if ctx.server:
        prefix = await prefix_conf.get(ctx)
    user_prefix = await ctx.bot.data.users.get(ctx.authid, "custom_prefix")
    prefix = prefix if prefix else ctx.bot.prefix
    return [prefix, user_prefix] if user_prefix else [prefix]


# Initialise the bot
bot = Bot(data=botdata, bot_conf=conf, prefix=PREFIX, prefix_func=get_prefixes, log_file=LOGFILE)

bot.DEBUG = conf.get("DEBUG")
bot.objects["logfile"] = open(bot.LOGFILE, 'a+')


async def log(bot, logMessage):
    print(logMessage)
    bot.objects["logfile"].write(logMessage + "\n")
    if bot.DEBUG > 1:
        ctx = Context(bot=bot)
        log_splits = await ctx.msg_split(logMessage, True)
        for log in log_splits:
            await bot.send_message(discord.utils.get(bot.get_all_channels(), id=LOG_CHANNEL), log)


Bot.log = log

# --------------------------------

# Load shared config and utils
bot.load("config", "global_events", "utils", ignore=["RCS", "__pycache__"])

# Add shared bot info
bot.objects["sorted cats"] = ["Info", "Fun", "Social", "Utility", "Moderation", "Server Admin", "Maths", "Meta", "Misc"]

bot.objects["sorted_conf_pages"] = [("General", ["Guild settings", "Starboard", "Mathematical settings"]),
                                    ("Manual Moderation", ["Moderation", "Logging"]),
                                    ("Join/Leave Messages", ["Join message", "Leave message"])]

# Pass to app to load app-specific objects and resources
bot.load("apps/shared", "apps/{}".format(CURRENT_APP if CURRENT_APP else "default"), ignore=["RCS", "__pycache__"])

bot.objects["regions"] = {
    "brazil": "Brazil",
    "eu-central": "Central Europe",
    "hongkong": "Hong Kong",
    "japan": "Japan",
    "russia": "Russia",
    "singapore": "Singapore",
    "sydney": "Sydney",
    "us-central": "Central United States",
    "us-east": "Eastern United States",
    "us-south": "Southern United States",
    "us-west": "Western United States",
    "eu-west": "Western Europe",
    "vip-amsterdam": "Amsterdam (VIP)",
    "vip-us-east": "Eastern United States (VIP)"
}

emojis = {
    "emoji_tex_del": "delete",
    "emoji_tex_show": "showtex",
    "emoji_tex_errors": "errors",
    "emoji_tex_delsource": "delete_source",
    "emoji_bot": "parabot",
    "emoji_botowner": "botowner",
    "emoji_botmanager": "botmanager",
    "emoji_online": "ParaOn",
    "emoji_idle": "ParaIdle",
    "emoji_dnd": "ParaDND",
    "emoji_offline": "ParaInvis",
    "emoji_next": "Next",
    "emoji_more": "More",
    "emoji_delete": "delete",
    "emoji_loading": "loading",
    "emoji_prev": "Previous"
}

# Initialise bot objects

bot.objects["ready"] = False
bot.objects["command_cache"] = LRUCache(1000)

# ----Discord event handling----


def get_emoji(name):
    emojis = bot.get_server(id=EMOJI_SERVER).emojis
    return discord.utils.get(emojis, name=name)


@bot.event
async def on_ready():
    GAME = conf.getStr("GAME")
    if GAME == "":
        GAME = "Type {}help for usage!".format(PREFIX)
    bot.objects["GAME"] = GAME
    GAME = await Context(bot=bot).ctx_format(GAME)
    await bot.change_presence(status=discord.Status.online, game=discord.Game(name=GAME))
    log_msg = "Logged in as\n{bot.user.name}\n{bot.user.id}\
        \nUsing configuration {app}.\
        \nLogged into {n} servers.\
        \nLoaded {CH} command handlers.\
        \nListening for {cmds} command keywords.\
        \nReady to process commands.".format(
        bot=bot, app=bot.objects["app"], n=len(bot.servers), CH=len(bot.handlers), cmds=len(bot.cmd_cache))

    for emoji in emojis:
        bot.objects[emoji] = get_emoji(emojis[emoji])

    bot.objects["cheat_report_channel"] = discord.utils.get(bot.get_all_channels(), id=CHEAT_CH)
    bot.objects["feedback_channel"] = discord.utils.get(bot.get_all_channels(), id=FEEDBACK_CH)
    bot.objects["preamble_channel"] = discord.utils.get(bot.get_all_channels(), id=PREAMBLE_CH)
    bot.objects["server_change_log_channel"] = discord.utils.get(bot.get_all_channels(), id=BOT_LOG_CH)

    await bot.log(log_msg)
    """
    ctx = Context(bot=bot)
    # This log isn't really needed. If it doesn't start up, it won't log anyway.
    with open(LOGFILE, "r") as f:
        log_splits = await ctx.msg_split(f.read(), True)
        for log in log_splits:
            await bot.send_message(discord.utils.get(bot.get_all_channels(), id=LOG_CHANNEL), log)
    """


async def publish_ready(bot):
    bot.objects["ready"] = True


bot.add_after_event("ready", publish_ready, priority=100)
# ----Event loops----
# ----End event loops----

# ----Everything is defined, start the bot!----
bot.run(conf.get("TOKEN"))
