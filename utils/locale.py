import json
import os

import discord
from discord import app_commands
from typing import Any

def load_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_all_translations() -> dict[str, dict[str, Any]]:
    return {
        "ja": load_json("locales/ja.json"),
        "en": load_json("locales/en.json")
    }


def deep_get(d: dict, key: str) -> str:
    keys = key.split(".")
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return key  # キーが見つからない場合はそのまま返す
    # 最終的に文字列以外だったら無効とする
    return d if isinstance(d, str) else key



translations = load_all_translations()


def t(locale: str, key: str, **kwargs) -> str:
    lang = "ja" if locale.startswith("ja") else "en"
    text = deep_get(translations.get(lang, {}), key)
    try:
        return text.format(**kwargs)
    except Exception:
        return text


class MyTranslator(app_commands.Translator):
    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext
    ) -> str:
        lang = "ja" if locale.value.startswith("ja") else "en"
        return deep_get(translations.get(lang, {}), string.message)
