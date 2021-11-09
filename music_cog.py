import discord
from discord.ext import commands
import youtube_dl

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.music_queue = []
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


    def play_next(self, ctx):
        if len(self.music_queue) > 0:            
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        else:
            self.is_playing = False


    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            if self.vc == "" or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
            # else:
            #     self.vc = await self.bot.move_to(self.music_queue[0][1])

            await ctx.send("Playing " + self.music_queue[-1][0]['title'])
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
            
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
                await ctx.send("Eroror downloading the song ¯\_(ツ)_/¯")
            else:
                self.music_queue.append([song, voice_channel])
                if self.is_playing == False:
                    # await ctx.send("Playing " + self.music_queue[-1][0]['title'])
                    await self.play_music(ctx)
                else:
                    await ctx.send(self.music_queue[-1][0]['title'] + " added to queue!")


    @commands.command()
    async def q(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += self.music_queue[i][0]['title']+"\n"

        print(retval)
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("Queue is empty.")


    @commands.command()
    async def s(self, ctx):
        if self.vc != "":
            self.vc.stop()
            await self.play_music()