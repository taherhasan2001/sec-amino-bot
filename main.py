import time, re
from pymino import Bot
from pymino.ext import Context, ObjectTypes
from config import COM_ID, EMAIL, KEY, MAIN_SECURITY_CHAT_ID, PASSWORD


class ArabicBadWordDetector:
    def __init__(self):
        # Read bad words from file (one per line)
        with open("badwords.txt", "r", encoding="utf-8") as f:
            # Strip whitespace and ignore empty lines
            self.bad_words = [line.strip() for line in f if line.strip()]

        # Remove duplicates if needed
        unique_bad_words = list(set(self.bad_words))

        # Build regex: match exact words, case-sensitive
        self.pattern = re.compile(
            r"(?<![\wء-ي])(" + "|".join(map(re.escape, unique_bad_words)) + r")(?![\wء-ي])"
        )

    def detect(self, text):
        """Return 1 if bad words detected, 0 otherwise"""
        return 1 if self.pattern.search(text) else 0


def is_bad_word(text: str) -> int:
    """
    Detects bad words in the given Arabic text.

    :param text: The Arabic text to check for bad words.
    :return: 1 if bad words are detected, 0 otherwise.
    """
    return ArabicBadWordDetector().detect(text)


#############################


def join_all_chats(size: int = 100):
    """
        It fetches public chats in the community and joins them.
    """
    counter = 1
    chats = bot.community.fetch_public_chats(size=size).json()
    for chat in chats:
        chat_id = chat["threadId"]
        bot.community.join_chat(chatId=chat_id)
        time.sleep(2)
        print(f"Joined {counter}/{size} chat: {chat['title']} ")
        counter += 1

    print("Bot has joined all public chats in the community.")



def get_all_message_info(ctx: Context, message: str):
    # user_id = ctx.author.userId
    user_name = ctx.author.username
    user_obj = bot.community.fetch_object(object_id=ctx.author.userId, comId=COM_ID)
    user_url = user_obj.json()['linkInfoV2'].get('extensions')['linkInfo']['shareURLFullPath']
    chat_info = bot.community.fetch_object(object_id=ctx.chatId, comId=COM_ID, object_type=ObjectTypes.CHAT)
    chat_url = chat_info.json()['linkInfoV2']['extensions']['linkInfo']['shareURLShortCode']

    content = f"Message: {message}\n\nUser Name: {user_name}\nChat URL: {chat_url}\nUser URL: {user_url}"
    return content


bot = Bot(
    service_key=KEY,
    community_id=COM_ID,
)


@bot.on_text_message()
def message(ctx: Context, message: str):
    """
    Handles incoming text messages in the community.
    If a bad word is detected, it sends a warning message.
    """
    if is_bad_word(message):
        content = get_all_message_info(ctx, message)
        print(content)
        bot.community.send_message(chatId=MAIN_SECURITY_CHAT_ID, content=content)


@bot.on_ready()
def on_ready():
    print("Bot is ready and running!")
    join_all_chats(size=30)  # Adjust size as needed
    bot.community.send_message(comId=COM_ID, chatId=MAIN_SECURITY_CHAT_ID, content="Hello, I'm here!")


bot.run(
    email=EMAIL,
    password=PASSWORD,
)
