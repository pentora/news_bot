import requests
from bs4 import BeautifulSoup
import schedule
import time
from googletrans import Translator
import discord
from discord.ext import commands
import asyncio

TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
CHANNEL_ID = 123456789  # 投稿したいDiscordチャンネルのID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

def crawl_news(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # ニュースサイトの構造に応じてここを調整
    articles = soup.find_all('article')
    return [{'title': a.find('h2').text, 'content': a.find('p').text} for a in articles]

def translate_text(text, target_lang='en'):
    translator = Translator()
    return translator.translate(text, dest=target_lang).text

def summarize_text(text):
    # ここに要約ロジックを実装
    # 簡単な例: 最初の2文を抽出
    sentences = text.split('。')
    return '。'.join(sentences[:2]) + '。'

async def post_to_discord(channel, content):
    await channel.send(content)

async def daily_task():
    news_url = "https://example-news-site.com"
    articles = crawl_news(news_url)
    
    channel = bot.get_channel(CHANNEL_ID)
    
    for article in articles:
        translated_title = translate_text(article['title'])
        summarized_content = summarize_text(article['content'])
        translated_summary = translate_text(summarized_content)
        
        message = f"**原題**: {article['title']}\n"
        message += f"**翻訳タイトル**: {translated_title}\n"
        message += f"**要約**: {translated_summary}\n"
        
        await post_to_discord(channel, message)
        await asyncio.sleep(1)  # APIレート制限を避けるため

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    bot.loop.create_task(scheduled_task())

async def scheduled_task():
    while True:
        now = time.localtime()
        if now.tm_hour == 9 and now.tm_min == 0:
            await daily_task()
        await asyncio.sleep(60)  # 1分ごとにチェック

bot.run(TOKEN)