import discord
import re
import pyzotero

token = XXXXXX
test_server_link = "https://discord.gg/kN8vwQz"


class DiscordBOT(discord.Client):


    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        self.reading_list_groups = {}
        self.edit_log = {}
        self.features = {"-help": self.bothelp, "-new": self.new_article, "-zotero": self.zotero}
        for channel in client.get_all_channels():
            if 'reading-group' in channel.name:
                if "general" in channel.category.name.lower():
                    self.general_reading_list = channel
                else:
                    self.reading_list_groups[channel.category] = channel

# TODO: set mods only, make syntax more general (make double spaces acceptable)

    async def on_message(self, message: discord.Message):
        if message.author.id == self.user.id:
            return
        if self.user in message.mentions:
            message_list = message.content.split(" ")
            try:
                feature = self.features[message_list[1]]
                await feature(message)

            except KeyError:
                await message.channel.send("I don't understand. For instructions, try @readerbot -help")

    async def on_message_edit(self, old_message, new_message):

        if self.user in new_message.mentions:
            message_list = new_message.content.split(" ")
            feature = self.features[message_list[1]]
            await feature(new_message)

    async def bothelp(self, message):
        await message.channel.send(
            "To add a current reading: @ReadingListBOT -new {title} {link} {date}. Adding a discussion date is "
            "optional. ReadingListBOT will then post a clean copy of your post, pin it, and post it in the appropriate"
            "reading channels.\n"
            # "To add a link to Zotero: @ReadingListBOT -zotero {link}. arxiv links are prefered.\n"
            "To edit a mistaken entry, edit the original entry and it will update automatically.\n"
            "New articles can't be posted from the general category or lobby channels")

    async def new_article(self, message):
        if message.channel.category.name.lower() != "general" \
                and "lobby" not in message.channel.name.lower() \
                and "general" not in message.channel.name.lower() \
                and "reading-group" not in message.channel.name.lower():
            article = message.content.split("-new")[1]
            article_without_parens = re.sub('\(.+?\)', '', article)
            text_in_brackets = re.findall('{(.+?)}', article_without_parens)

            if len(text_in_brackets) == 2:
                title = text_in_brackets[0]
                link = text_in_brackets[1]
                output = "Title: **{}**\nIn: {}\nLink: {}".format(title, message.channel.mention, link)
                pin_output = "Title: **{}**\nLink: {}".format(title, link)
            elif len(text_in_brackets) == 3:
                title = text_in_brackets[0]
                link = text_in_brackets[1]
                date = text_in_brackets[2]
                output = "Title: **{}**\nIn: {}\nLink: {}\nDiscussion Date: {}".format(title, message.channel.mention, link, date)
                pin_output = "Title: **{}**\nLink: {}\nDiscussion Date: {}".format(title, link, date)
            else:
                await message.channel.send("I don't understand. For instructions, post @readerbot -help")
                self.edit_log[message.id] = []
                return
            # this determines if it is a new message or not. the switch has to be inside this function to avoid
            # cluttering the on_message and on_message_edit functions

            # checks if the message is present in the edit log, and if so that it's not empty (a broken post)
            if message.id in self.edit_log and self.edit_log[message.id] != []:
                children_messages = self.edit_log[message.id]
                new_local_message = await children_messages[0].edit(content=output)
                new_global_message = await children_messages[1].edit(content=output)
                new_pin_message = await children_messages[2].edit(content=pin_output)
                self.edit_log[message.id] = [new_local_message, new_global_message, new_pin_message]
            else:
                local_message = await self.reading_list_groups[message.channel.category].send(output)
                global_message = await self.general_reading_list.send(output)
                pin_message = await message.channel.send(pin_output)
                await pin_message.pin()
                self.edit_log[message.id] = [local_message, global_message, pin_message]
        else:
            await message.delete()
            await message.channel.send("Cannot post readings in the GENERAL category or lobbies. \n"
                                       "Please select a reading group channel instead")

    async def zotero(self):
        # TODO Parse the non-general and non-other categories and non-lobby channels to construct a file structure
        # TODO Automatically generate said file structure in the appropriate Zotero group
        # TODO Similar post/edit behaviour as -new, but taking the link and passing it to Zotero's magic
        # TODO Send an alert if the link is invalid or otherwise non-functional
        # TODO When posts are made from new categories and channels, add them as approrpriate

        pass


client = DiscordBOT()
client.run(token)
