import re
from paraSetting import paraSetting


class BOOL(paraSetting):
    """
    A sort of boolean type, more like a wrapper for a boolean.
    """
    accept = "Yes/No, True/False, Enabled/Disabled"
    inputexps = {"^yes$": True,
                 "^true$": True,
                 "^enabled?$": True,
                 "^no$": False,
                 "^false$": False,
                 "^disabled?$": False}
    outputs = {True: "",
               False: ""}

    def humanise(cls, ctx, raw):
        return cls.outputs[raw]

    def understand(cls, ctx, userstr):
        for pattern in cls.inputexps:
            if re.match(pattern, userstr, re.I):
                return cls.inputexps[pattern]
        ctx.cmd_err = (1, "I don't understand this value. Acceptable values are: {}".format(cls.accept))
        return None


class STR(paraSetting):
    """
    Just a plain string, nothing special
    """
    accept = "Any text"

    def humanise(cls, ctx, raw):
        return "\"{}\"".format(str(raw))

    def understand(cls, ctx, userstr):
        return userstr


class FMTSTR(STR):
    """
    Formatable string
    TODO: accepted keys in variable from somewhere
    """
    accept = "Formatted string, accepted keys are:\n"
    accept += "\t $username$, $mention$, $id$, $tag$, $displayname$, $server$"


class CHANNEL(paraSetting):
    """
    Channel type.
    """
    accept = "Channel mention/id/name"

    def humanise(self, ctx, raw):
        """
        Expect raw to be channel id or 0, an empty.
        """
        if not raw:
            return "None"
        return "<#{}>".format(raw)

    def understand(self, ctx, userstr):
        """
        User can enter a channel mention or an id, or even a name.
        TODO: Check if the channel actually exists given an id.
        """
        userstr = str(userstr)
        chid = userstr.strip('<#!>')
        if chid.isdigit():
            return chid
        if not ctx.server:
            ctx.cmd_err = (1, "Not in a server, please provide channel id or mention.")
            return None
        for ch in ctx.server.channels:
            if ch.name.lower() == userstr.lower():
                return ch.id
        ctx.cmd_err = (1, "I can't find this channel, please provide an id or mention.")
        return None


"""
class YES_BOOL(BOOL):
    name = "Yes/No"
    outputs = {True: "Yes",
               False: "No"}


class ENABLED_BOOL(BOOL):
    name = "Enabled/Disabled"
    outputs = {True: "Enabled",
               False: "Disabled"}
"""
'''
class userList(paraSetting):
    name = "List of users"
    accept = "[+/add | -/remove] <userid/mention>"
    str_already_in_list = ""
    str_not_in_list = ""
    str_removed_from_list = ""
    str_added_to_list = ""

    def humanise(self, raw):
        """
        Expect raw to be a list, possibly of strings, possible of integers, containing userids.
        """
        if self.client is None:
            return ', '.join([str(user) for user in raw if str(user).isdigit()])
        users = [str(user) for user in raw]
        user_tags = [discord.utils.get(self.client.get_all_members(), id=user) for user in users]
        userlist = [str(user) for user in user_tags if user]
        return '`{}`'.format('`, `'.join(userlist))

    def understand(self, userstr):
        params = userstr.split(' ')
        action = params[0]
        if (action in ['+', 'add']) and (len(params) == 2) and params[1].strip('<!@>').isdigit():
            userid = int(params[1].strip('<!@>'))
            if userid in self.raw:
                (self.error, self.errmsg) = (3, self.str_already_in_list)
                return self.raw
            else:
                self.raw.append(userid)
                (self.error, self.errmsg) = (0, self.str_added_to_list)
                return self.raw
        elif (action in ['-', 'remove']) and (len(params) == 2) and params[1].strip('<!@>').isdigit():
            userid = int(params[1].strip('<!@>'))
            if userid not in self.raw:
                (self.error, self.errmsg) = (3, self.str_not_in_list)
                return self.raw
            else:
                self.raw.remove(userid)
                (self.error, self.errmsg) = (0, self.str_removed_from_list)
                return self.raw
        else:
            (self.error, self.errmsg) = (1, "I don't understand your input. Valid input is: `{}`".format(self.accept))
            return self.raw
'''


"""
class userBlackList(userList):
    name = "List of users"
    accept = "[+/add | -/remove] <userid/mention>"
    str_already_in_list = "I have already blacklisted this user!"
    str_not_in_list = "This user hasn't been blacklisted."
    str_removed_from_list = "Let's hope they stay out of trouble. That user is no longer blacklisted."
    str_added_to_list = "I never liked them anyway, that user is now blacklisted."


class userMasterList(userList):
    name = "List of users"
    accept = "[+/add | -/remove] <userid/mention>"
    str_already_in_list = "This user is already one of my masters!"
    str_not_in_list = "This user is not one of my masters!"
    str_removed_from_list = "I have rejected this master."
    str_added_to_list = "I accept this user as a new master."
"""


'''
class SERVER(_settingType):
    """
    Server type.
    Incomplete.
    """
    name = "server"
    accept = "Server name/ server id"
'''