import asyncio
import discord
from discord.ext import commands
import ctypes.util
import youtube_dl

textChatIDlist = [170682390786605057, 302137557896921089, 302965414793707522, 293186321395220481, 570471843538927638] 
ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    opus = ctypes.util.find_library("opus")
    discord.opus.load_opus(opus)
    
class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await ctx.send(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Music(commands.Cog, name='Music'):
    """Voice related commands.
    Works in multiple guilds at once.
    """
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, guild):
        state = self.voice_states.get(guild.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[guild.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await channel.connect()
        state = self.get_voice_state(channel.guild)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command()
    @commands.guild_only()
    async def join(self, ctx, *, channel):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            """Joins a voice channel."""
            try:
                await self.create_voice_client(channel)
            except discord.ClientException:
                await ctx.send('Already in a voice channel...')
            except discord.InvalidArgument:
                await ctx.send('This is not a voice channel...')
            else:
                await ctx.send('Ready to play audio in ' + channel.name)

    @commands.command()
    @commands.guild_only()
    async def summon(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            """Summons the bot to join your voice channel."""
            summoned_channel = ctx.message.author.voice.channel
            if summoned_channel is None:
                await ctx.send('You are not in a voice channel.')
                return False

            state = self.get_voice_state(ctx.message.guild)
            if state.voice is None:
                state.voice = await summoned_channel.connect()
            else:
                await state.voice.move_to(summoned_channel)

        return True
           

    @commands.command()
    @commands.guild_only()
    async def play(self, ctx, *, song : str):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            """Plays a song.
            If there is a song currently in the queue, then it is
            queued until the next song is done playing.
            This command automatically searches as well from YouTube.
            The list of supported sites can be found here:
            https://rg3.github.io/youtube-dl/supportedsites.html
            """
            state = self.get_voice_state(ctx.message.guild)
            opts = {
                'default_search': 'auto',
                'quiet': True,
            }

            if state.voice is None:
                success = await ctx.invoke(self.summon)
                if not success:
                    return

            try:
                player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
            except Exception as e:
                fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                await ctx.send(fmt.format(type(e).__name__, e))
            else:
                player.volume = 0.6
                entry = VoiceEntry(ctx.message, player)
                await ctx.send('Enqueued ' + str(entry))
                await state.songs.put(entry)

    @commands.command()
    @commands.guild_only()
    async def volume(self, ctx, value : int):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            """Sets the volume of the currently playing song."""

            state = self.get_voice_state(ctx.message.guild)
            if state.is_playing():
                player = state.player
                player.volume = value / 100
                await ctx.send('Set the volume to {:.0%}'.format(player.volume))

    @commands.command()
    @commands.guild_only()
    async def pause(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            """Pauses the currently played song."""
            state = self.get_voice_state(ctx.message.guild)
            if state.is_playing():
                player = state.player
                player.pause()

    @commands.command()
    @commands.guild_only()
    async def resume(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            """Resumes the currently played song."""
            state = self.get_voice_state(ctx.message.guild)
            if state.is_playing():
                player = state.player
                player.resume()

    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            """Stops playing audio and leaves the voice channel.
            This also clears the queue.
            """
            guild = ctx.message.guild
            state = self.get_voice_state(guild)

            if state.is_playing():
                player = state.player
                player.stop()

            try:
                state.audio_player.cancel()
                del self.voice_states[guild.id]
                await state.voice.disconnect()
            except:
                pass

    @commands.command()
    @commands.guild_only()
    async def skip(self, ctx):
        channelID = ctx.message.channel.id
        if channelID in textChatIDlist:
            """Vote to skip a song. The song requester can automatically skip.
            3 skip votes are needed for the song to be skipped.
            """

            state = self.get_voice_state(ctx.message.guild)
            if not state.is_playing():
                await ctx.send('Not playing any music right now...')
                return

            voter = ctx.message.author
            if voter == state.current.requester:
                await ctx.send('Requester requested skipping song...')
                state.skip()
            elif voter.id not in state.skip_votes:
                state.skip_votes.add(voter.id)
                total_votes = len(state.skip_votes)
                if total_votes >= 3:
                    await ctx.send('Skip vote passed, skipping song...')
                    state.skip()
                else:
                    await ctx.send('Skip vote added, currently at [{}/3]'.format(total_votes))
            else:
                await ctx.send('You have already voted to skip this song.')

    @commands.command()
    @commands.guild_only()
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.guild)
        if state.current is None:
            await ctx.send('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await ctx.send('Now playing {} [skips: {}/3]'.format(state.current, skip_count))


def setup(bot):
	bot.add_cog(Music(bot))
