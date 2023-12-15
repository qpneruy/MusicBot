import interactions

import interactions
from interactions import Embed


def create_embed(
        title: str = "",
        description: str = "",
        fields: list[tuple[str, str, bool]] = [],
        color: int = 0x0000FF,
        footer_text: str = None,
        footer_image: str = None,
        include_thumbnail: bool = False,
        image: str = None,
        video: str = None,
) -> interactions.Embed:
    embed = interactions.Embed(title=title, description=description, color=color)
    if image:
        embed.set_image(url=image)
    if video:
        embed.set_video(url=video)
    if include_thumbnail:
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/avatars/610841389164396565/9769cd5aa36e40c51d6512d9643c78de.png?size=4096")
    if footer_text:
        embed.set_footer(
            text=footer_text,
            icon_url=footer_image if footer_image else "https://cdn.discordapp.com/avatars/610841389164396565/9769cd5aa36e40c51d6512d9643c78de.png?size=4096",
        )
    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])
    return embed


def embed_make_pp(title: str, thumbnails: str, uploader: str, total: int):
    embed = Embed(
        title=f'{title}',
        description="ㅤ",
        color=0x5f9afa,
    )
    embed.set_author("➕ Đã thêm playlist 📋")
    embed.set_image(thumbnails)
    embed.add_field(name="Author: ", value=f'**{uploader}**', inline=True)
    embed.add_field(name="Số lượng: ", value=f'**{total}**', inline=True)
    return embed
