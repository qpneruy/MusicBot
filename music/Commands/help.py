import interactions
import pymysql
from interactions import Embed, ActionRow, Button, ButtonStyle
from interactions.ext.paginators import Paginator

from modules import create_embed


class Help(interactions.Extension):
    help_commands = None

    @interactions.listen(interactions.events.Startup)
    async def on_startup(self):
        self.help_commands: list[interactions.InteractionCommand] = []
        for interaction_command in self.bot.interaction_tree.values():
            self.create_commands_recursive(interaction_command)

    def create_commands_recursive(self, interaction_command):
        if isinstance(interaction_command, interactions.InteractionCommand):
            self.help_commands.append(interaction_command)
        elif isinstance(interaction_command, dict):
            for interaction_subcommand in interaction_command.values():
                self.create_commands_recursive(interaction_subcommand)
        else:
            raise Exception(f"Unknown interaction command type in /help: {type(interaction_command)}")

    @interactions.slash_command(name="help", description="all command")
    async def help(self, ctx: interactions.SlashContext):
        fields_list = []
        for command in self.help_commands:
            if command.is_enabled(ctx):
                if isinstance(command, interactions.SlashCommand):
                    name = str(command.name)
                    if command.group_name:
                        name += " " + str(command.group_name)
                    if command.sub_cmd_name:
                        name += " " + str(command.sub_cmd_name)

                    desc = str(command.description)
                    if command.group_name:
                        desc = str(command.group_description)
                    if command.sub_cmd_name:
                        desc = str(command.sub_cmd_description)

                    fields_list.append(interactions.EmbedField(name=f"/{name}", value=desc))
                else:
                    fields_list.append(
                        interactions.EmbedField(name=f"{command.name}",
                                                value="there no command to show here")
                    )
        chunked_fields_list = [fields_list[i: i + 10] for i in range(0, len(fields_list), 10)]  # noqa
        embeds = []
        for i, fields_list in enumerate(chunked_fields_list):
            embed = create_embed(
                title=f"Help | Trang {i + 1}/{len(chunked_fields_list)}",
                color=0x5f9afa,
                footer_text="Contact @tinhdev061/</Джихё> to report bugs / suggestions!",
                include_thumbnail=True,
            )
            embed.add_fields(*fields_list)
            embeds.append(embed)

        paginator = Paginator.create_from_embeds(self.bot, *embeds)
        await paginator.send(ctx)

    @interactions.slash_command(name="about", description="Bot status")
    async def _about(self, ctx: interactions.SlashContext):
        embed = Embed(
            title="-------BOT STATUS-------",
            description="ㅤ",
            color=0x00BAFF,
        )
        button = ActionRow(
            Button(
                style=ButtonStyle.URL,
                label="github.com",
                url="https://github.com/Tinhdev061"
            )
        )
        connect_thread = pymysql.connect(host='127.0.0.1', user='root', password='W2:)G8%ZLj~8#',
                                         database='discord_guild')
        embed.add_field(name="🏠LOCALHOST PING", value=f"{round(ctx.bot.latency * 1000)} msㅤㅤㅤㅤㅤ", inline=True)
        embed.add_field(name="🗃️DATABASE PING", value=f'{connect_thread.ping()} ms')
        embed.add_field(name="⚓CONNECT:", value=f'{connect_thread.get_host_info()}')
        embed.add_field(name="Author: ", value="qpneruy (TinhDev061)")
        await ctx.send(embeds=embed, components=button)
