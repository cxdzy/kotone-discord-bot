import inspect
from types import SimpleNamespace
import discord
from discord import app_commands


# Bot setup
intents = discord.Intents.default()
intents.message_content = True


class KotoneBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced {len(self.tree.get_commands())} slash commands")

bot = KotoneBot()
SLASH_COMMANDS = {}
SLASH_COMMAND_ALIASES = {}


class SlashContext:
    def __init__(self, interaction, invoked_with, members):
        self.interaction = interaction
        self.author = interaction.user
        self.guild = interaction.guild
        self.channel = interaction.channel
        self.bot = interaction.client
        self.invoked_with = invoked_with
        self.message = SimpleNamespace(mentions=members)

    async def reply(self, content=None, **kwargs):
        kwargs.pop("mention_author", None)
        return await self.interaction.followup.send(
            content=content,
            wait=True,
            **kwargs,
        )

    async def send(self, content=None, **kwargs):
        return await self.reply(content, **kwargs)


def slash_command(
    name=None,
    *,
    aliases=(),
    group=None,
    autocomplete=None,
    descriptions=None,
):
    def decorator(callback):
        callback_signature = inspect.signature(callback)
        option_parameters = []
        for parameter in list(callback_signature.parameters.values())[1:]:
            annotation = parameter.annotation
            if annotation is inspect.Parameter.empty:
                annotation = str
            option_parameters.append(
                parameter.replace(
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=annotation,
                )
            )

        async def invoke(interaction, **options):
            await interaction.response.defer(thinking=True)
            members = [
                value
                for value in options.values()
                if isinstance(value, discord.Member)
            ]
            context = SlashContext(
                interaction,
                interaction.data.get("name", command_name),
                members,
            )
            await callback(context, **options)

        command_name = name or callback.__name__
        command_description = (callback.__doc__ or "Run this command.").strip()
        command_description = command_description.splitlines()[0][:100]
        parameters = [
            inspect.Parameter(
                "interaction",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=discord.Interaction,
            ),
            *option_parameters,
        ]
        invoke.__signature__ = inspect.Signature(parameters)
        invoke.__annotations__ = {
            parameter.name: parameter.annotation for parameter in parameters
        }
        if descriptions:
            invoke.__discord_app_commands_param_description__ = descriptions
        if autocomplete:
            app_commands.autocomplete(**autocomplete)(invoke)

        for registered_name in (command_name, *aliases):
            SLASH_COMMAND_ALIASES[registered_name] = tuple(
                alias
                for alias in (command_name, *aliases)
                if alias != registered_name
            )
            command = app_commands.Command(
                name=registered_name,
                description=command_description,
                callback=invoke,
            )
            if group is None:
                bot.tree.add_command(command)
            else:
                group.add_command(command)
            command_key = (
                f"{group.name} {registered_name}"
                if group is not None
                else registered_name
            )
            SLASH_COMMANDS[command_key] = command
        return callback

    return decorator
