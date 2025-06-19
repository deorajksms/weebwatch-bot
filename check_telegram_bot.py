import telegram
import asyncio

async def check_bot():
    bot = telegram.Bot("7897903573:AAEqBcTb8IRV3FXtXYrE4r6aQh30QhrVot8")
    me = await bot.get_me()
    print(me)

asyncio.run(check_bot())
