import discord
from discord.ext import commands
import youtube_dl

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_looped = False
        self.music_queue = []
        self.loop_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options':'-vn'}

        self.vc = ""


    def search_yt(self, item):
        with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info('ytsearch: %s' % item, download=False)['entries'][0]
            except Exception:
                return False
        
        return {'source': info['formats'][0]['url'], 'title': info['title']}


    def play_next(self):
        if self.is_looped and len(self.music_queue) == 0:
            self.music_queue = self.loop_queue

        if len(self.music_queue) > 0:            
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            self.music_queue.pop(0)
        else:
            self.is_playing = False

    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            if self.vc == "" or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.play_next()
        else:
            self.is_playing = False


    @commands.command()
    async def p(self, ctx, *args):
        query = " ".join(args)
        voice_channel = ctx.author.voice.channel

        #this does not work - message is not send when not connected to channel
        if voice_channel is None:
            await ctx.send("Connect to voice channel!")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Error downloading the song ??\_(???)_/??")
            else:
                self.music_queue.append([song, voice_channel])
                self.loop_queue.append([song, voice_channel])
                if self.is_playing == False:
                    await self.play_music()
                else:
                    await ctx.send(self.music_queue[-1][0]['title'] + " added to queue!")


    @commands.command()
    async def loop(self, ctx):
        if self.is_looped:
            await ctx.send('Loop mode is `OFF`')
            self.is_looped = False
        else:
            await ctx.send('Loop mode is `ON`')
            self.is_looped = True
            

    @commands.command()
    async def rm(self, ctx, *args):
        query = " ".join(args)
        for i in range(0, len(self.music_queue)):
            if query.lower() in self.music_queue[i][0]['title'].lower():
                await ctx.send("Removing " + self.music_queue[i][0]['title'] + " from queue..")
                del self.music_queue[i]
        

    @commands.command()
    async def q(self, ctx):
        retval = ""

        if self.is_looped:
            for i in range(0, len(self.loop_queue)):
                retval += self.loop_queue[i][0]['title']+"\n"
        else:
            for i in range(0, len(self.music_queue)):
                retval += self.music_queue[i][0]['title']+"\n"

        if retval != "":
            if self.is_looped:
                await ctx.send('Looped queue:')
            await ctx.send(retval)
        else:
            await ctx.send("Queue is empty.")


    @commands.command()
    async def s(self, ctx):
        if self.vc != "" and self.vc:
            self.vc.stop()