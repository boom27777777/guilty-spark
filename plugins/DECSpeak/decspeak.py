import discord
import os

from random import randint

from guilty_spark.plugin_system.plugin import Plugin
from guilty_spark.plugin_system.data import plugin_file_path, plugin_file


class DECSpeak(Plugin):
    def __init__(self, name: str, bot):
        super().__init__(name, bot, commands=['speak'])

    async def help(self, message):
        args = message.content.split()
        if len(args) == 2:
            embed = self.build_embed(
                title='Speak',
                description='make the bot join your channel and say something'
            )
            embed.add_field(
                name='Voices:',
                value='```[:np],[:nh],[:nf],[:nd],[:nb],[:nu],[:nw],[:nr],[:nk],[:nv]```',
                inline=True
            )
            embed.add_field(
                name='Phonemes:',
                value='```_,aa,ae,ah,ao,aw,ax,ay,b,ch,d,dh,dx,eh,el,en,ey,f,g,hx,ih,ix,iy,jh,k,l,lx,m,n,nx,ow,oy,p,q,r,'
                      'rr,rx,s,sh,t,th,tx,uh,uw,v,w,yu,yx,z,zh```',
                inline=True
            )
        else:
            if args[2].startswith('voice'):
                embed = self.build_embed(
                    title='Speak/Voices',
                    description='These are the predefined voices for dectalk'
                )
                embed.add_field(name="[:np]", value="```Change to Paul’s voice (default male)```", inline=False)
                embed.add_field(name="[:nh]", value="```Change to Harry’s voice (full male voice)```", inline=False)
                embed.add_field(name="[:nf]", value="```Change to Frank’s voice (aged male)```", inline=False)
                embed.add_field(name="[:nd]", value="```Change to Dennis’s voice (male)```", inline=False)
                embed.add_field(name="[:nb]", value="```Change to Betty’s voice (full female voice)```", inline=False)
                embed.add_field(name="[:nu]", value="```Change to Ursula’s voice (aged female)```", inline=False)
                embed.add_field(name="[:nw]", value="```Change to Wendy’s voice (whispering female)```", inline=False)
                embed.add_field(name="[:nr]", value="```Change to Rita’s voice (female)```", inline=False)
                embed.add_field(name="[:nk]", value="```Change to Kit’s voice (child)```", inline=False)
                embed.add_field(name="[:nv]", value="```Change to Val’s voice```", inline=False)
            if args[2].startswith('phoneme'):
                embed = self.build_embed(
                    title='Speak/Phonemes',
                    description='These are all the valid phonemes```'
                )
                embed.add_field(
                    name="Usage",
                    value="```[phoneme <duration, pitch>]```",
                    inline=False,
                )
                embed.add_field(
                    name="All Phonemes",
                    inline=False,
                    value='```'
                          '_     silence\n'
                          'q     glottal stop\n'
                          'aa    b_o_b\n'
                          'ae    b_a_t\n'
                          'ah    b_u_t\n'
                          'ao    b_ou_ght\n'
                          'aw    bo_u_t\n'
                          'ax    _a_bout\n'
                          'ay    b_i_te\n'
                          'b     _b_ottle\n'
                          'ch    _ch_in\n'
                          'd     _d_ebt\n'
                          'dh    _th_is\n'
                          'dx    ri_d_er\n'
                          'eh    b_e_t\n'
                          'el    bott_le_\n'
                          'en    butt_on_\n'
                          'ey    b_a_ke\n'
                          'f     _f_in\n'
                          'g     _g_uess\n'
                          'hx    _h_ead\n'
                          'ih    b_i_t\n'
                          'ix    kiss_es_\n'
                          'iy    b_ea_t\n'
                          'jh    _g_in\n'
                          'k     _K_en\n'
                          'l     _l_et\n'
                          'lx    e_l_ectric\n'
                          'm     _m_et\n'
                          'n     _n_et\n'
                          'nx    si_ng_\n'
                          'ow    b_oa_t\n'
                          'oy    b_oy_\n'
                          'p     _p_et\n'
                          'r     _r_ed\n'
                          'rr    b_i_rd\n'
                          'rx    o_r_ation\n'
                          's     _s_it\n'
                          'sh    _sh_in\n'
                          't     _t_est\n'
                          'th    _th_in\n'
                          'tx    La_t_in\n'
                          'uh    b_o_ok\n'
                          'uw    l_u_te\n'
                          'v     _v_est\n'
                          'w     _w_et\n'
                          'yu    c_u_te\n'
                          'yx    _y_et\n'
                          'z     _z_oo\n'
                          'zh    a_z_ure```'
                )

        await self.bot.send_embed(embed)

    async def speak(self, user, channel, text):
        # avoid trampling a file if a user requests too much too fast
        # not perfect but who cares
        rand = str(randint(0, 99999))
        # store user input into a txt and pass it through std input
        inputname = rand + user.id + 'request.txt'
        inputpath = plugin_file(inputname, 'w')
        inputpath.write(text)
        inputpath = plugin_file_path(inputname)
        soundpath = plugin_file_path(rand + user.id + 'shitpost.wav')
        print(soundpath)
        command = 'wine ./plugins/DECSpeak/say.exe -pre "[:phoneme on]" -w "' + soundpath + '" <' + inputpath
        print(command)
        os.system(command)
        command = 'ffmpeg-normalize {path} -o {path}'.format(path=soundpath)
        os.system(command)
        await self.bot.play_sound(soundpath)
        # soundpath = plugin_file(soundpath, 'r')
        # await self.bot.send_file(channel, soundpath)
        # hopefully we don't delete the file before it finishes trying to play it!
        os.remove(inputpath)
        os.remove(soundpath)

    async def on_command(self, command, message: discord.Message):
        text = message.content.replace(command, '').strip()
        await self.speak(message.author, message.channel, text)

    async def on_plugin_message(self, *args, **kwargs):
        message = kwargs.setdefault('speak-message', None)
        user = kwargs.setdefault('user', None)
        if message and user:
            await self.speak(user, None, message)
