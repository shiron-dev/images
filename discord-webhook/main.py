import os
from typing import Any

import discord
import requests


def parse_webhook_urls(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    return [url.strip() for url in raw_value.split(",") if url.strip()]


def create_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    intents.guilds = True
    return intents


def build_reply_metadata(message: discord.Message) -> dict[str, str | None]:
    if message.reference and isinstance(message.reference.resolved, discord.Message):
        return {
            "reply_message_id": str(message.reference.message_id),
            "reply_channel_id": str(message.reference.channel_id),
            "reply_guild_id": str(message.reference.guild_id) if message.reference.guild_id else None,
        }

    return {
        "reply_message_id": None,
        "reply_channel_id": None,
        "reply_guild_id": None,
    }


def build_payload(message: discord.Message) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "content": message.content,
        "author": message.author.name,
        "author_id": str(message.author.id),
        "channel": message.channel.name,
        "channel_id": str(message.channel.id),
        "server": message.guild.name if message.guild else "Direct Message",
        "server_id": str(message.guild.id) if message.guild else None,
        "message_id": str(message.id),
        "timestamp": message.created_at.isoformat(),
        "is_bot": message.author.bot,
        "is_reply": message.reference is not None,
    }
    payload.update(build_reply_metadata(message))
    return payload


def post_to_webhooks(webhook_urls: list[str], payload: dict[str, Any], message_id: int) -> None:
    headers = {"Content-Type": "application/json"}

    for url in webhook_urls:
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            print(f"メッセージID {message_id} を {url} に転送しました。")
        except requests.exceptions.RequestException as error:
            print(f"{url} への送信中にエラーが発生しました: {error}")


DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
WEBHOOK_URLS = parse_webhook_urls(os.getenv("WEBHOOK_URLS"))

client = discord.Client(intents=create_intents())

@client.event
async def on_ready() -> None:
    print(f"{client.user} としてログインしました。")
    print("---------------------------------")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return

    payload = build_payload(message)
    post_to_webhooks(WEBHOOK_URLS, payload, message.id)


if DISCORD_BOT_TOKEN and WEBHOOK_URLS:
    client.run(DISCORD_BOT_TOKEN)
else:
    print("エラー: DISCORD_BOT_TOKEN または WEBHOOK_URLS が設定されていません。")
    print("環境変数を設定してください。")
