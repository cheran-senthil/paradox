class Command:
    def __init__(self, name, func, CH, **kwargs):
        self.name = name
        self.func = func
        self.handler = CH
        self.short_help = kwargs["short_help"] if "short_help" in kwargs else None
        self.long_help = kwargs["long_help"] if "long_help" in kwargs else None
        self.category = kwargs["category"] if "category" in kwargs else None
        self.aliases = kwargs["aliases"] if "aliases" in kwargs else None

    async def run(self, cmd_ctx):
        await self.func(cmd_ctx)
