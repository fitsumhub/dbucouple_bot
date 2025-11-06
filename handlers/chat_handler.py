async def match_notification(context, user1, user2):
    await context.bot.send_message(chat_id=user1, text=f"🎉 You matched with @{user2}!")

