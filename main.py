import discord
from discord.ext import commands, tasks
from discord.ui import View, Button, Select
import asyncio
import re
import time
import os

# Configurações iniciais
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

# Variáveis globais
cooldown_global = 120
ultimo_uso_global = None

# -----------------------------
# ⏰ Lembrete Automático com Timer
# -----------------------------

class ViewBotao(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.mensagem = None

    @discord.ui.button(label='📢 Divulgar o Servidor', style=discord.ButtonStyle.green, custom_id='divulgar')
    async def divulgar_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Compartilhe o link do nosso servidor com seus amigos! 🚀\nhttps://discord.gg/x2gHf2XEvx",
            ephemeral=True
        )

    @discord.ui.button(label='🎵 Nosso TikTok', style=discord.ButtonStyle.grey,custom_id='tiktok')
    async def tiktok_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Segue a gente no TikTok para ver clipes e novidades! 🎶\nhttps://www.tiktok.com/@sosalove333",
            ephemeral=True
        )

    @discord.ui.button(label='💬 Falar com Staff', style=discord.ButtonStyle.blurple, custom_id='suporte')
    async def suporte_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "📌 Vá até o canal de suporte: <#1353562103872618546>",
            ephemeral=True
        )

    async def start_timer(self):
        total = 5
        for restante in range(total, 0, -1):
            barra = f"[{'█' * restante}{'░' * (total - restante)}]"
            texto = f"⏳ Removendo em: {barra} {restante} minuto(s)..."
            try:
                await self.mensagem.edit(content=texto)
                await asyncio.sleep(60)
            except discord.HTTPException:
                break

    async def on_timeout(self):
        if self.mensagem:
            try:
                await self.mensagem.delete()
            except discord.HTTPException as e:
                print(f"Erro ao deletar mensagem: {e}")


@tasks.loop(hours=1)
async def lembrete_automatico():
    canal = bot.get_channel(1353555105961476107)

    if canal:
        view = ViewBotao()

        embed = discord.Embed(
            title="🔔 Lembrete Importante",
            description="Não se esqueça de divulgar o servidor e nos seguir no TikTok!",
            color=discord.Color.red()
        )
        embed.set_footer(text="A mensagem será removida automaticamente após 5 minutos.")
        embed.set_image(url="attachment://entrada.jpg")
        embed.set_thumbnail(url="attachment://logo.png")

        arquivos = [
            discord.File("entrada.jpg", filename="entrada.jpg"),
            discord.File("ezgif.com-crop.gif", filename="logo.png")
        ]

        msg = await canal.send(
            content="⏳ Removendo em: [█████] 5 minutos...",
            embed=embed,
            view=view,
            files=arquivos
        )

        view.mensagem = msg
        await view.start_timer()

# -----------------------------
# 🎉 Eventos do Bot
# -----------------------------

@bot.event
async def on_ready():
    await bot.tree.sync()
    lembrete_automatico.start()
    print("Bot inicializado com sucesso.")

@bot.event
async def on_member_join(member: discord.Member):
    canal = bot.get_channel(1360065538021261372)
    if canal:
        embed = discord.Embed(
            title="🎉 Novo membro chegou!",
            description=f"Bem-vindo(a) ao servidor, {member.mention}!",
            color=discord.Color.green()
        )
        embed.set_author(name=member.name, icon_url=member.display_avatar.url)
        embed.set_image(url="attachment://entrada.jpg")
        embed.set_thumbnail(url="attachment://logo.png")
        embed.set_footer(text="Estamos felizes por ter você aqui!")

        arquivos = [
            discord.File("entrada.jpg", filename="entrada.jpg"),
            discord.File("ezgif.com-crop.gif", filename="logo.png")
        ]

        view = View()
        view.add_item(Button(label="📜 Ver Regras", url="https://discord.com/channels/1353546355171393597/1360065538021261372"))

        await canal.send(embed=embed, files=arquivos, view=view)

@bot.event
async def on_member_remove(member: discord.Member):
    canal = bot.get_channel(1360065538021261372)
    if canal:
        embed = discord.Embed(
            title="💨 Um membro saiu...",
            description=f"{member.name} nos deixou. Até mais, betinha.",
            color=discord.Color.red()
        )
        embed.set_author(name=member.name, icon_url=member.display_avatar.url)
        embed.set_image(url="attachment://saida.png")
        embed.set_thumbnail(url="attachment://logo.png")
        embed.set_footer(text="Esperamos te ver de novo algum dia... ou não..")

        arquivos = [
            discord.File("saida.png", filename="saida.png"),
            discord.File("ezgif.com-crop.gif", filename="logo.png")
        ]

        await canal.send(embed=embed, files=arquivos)

@bot.event
async def on_message(msg: discord.Message):
    global ultimo_uso_global

    if msg.author.bot:
        return

    if re.fullmatch(r'[^\w]*est[áa]vel[^\w]*', msg.content.strip(), re.IGNORECASE):
        agora = time.time()
        if ultimo_uso_global and (agora - ultimo_uso_global) < cooldown_global:
            tempo_restante = int(cooldown_global - (agora - ultimo_uso_global))
            await msg.reply(f"{msg.author.mention}, o comando está em cooldown. Tente novamente em {tempo_restante}s.", delete_after=5)
            return

        ultimo_uso_global = agora
        await msg.reply(f"{msg.author.mention}, Relaxe, seu IP está Estável!\nhttps://youtu.be/GUVtZOjKotk")

    await bot.process_commands(msg)
    
    
@bot.event
async def on_member_join(member: discord.Member):
    tempo_de_conta = time.time() - member.created_at.timestamp()

    # ID do canal de logs (substitua pelo ID do seu canal de log)
    canal_logs_id = 1356428904386265190
    canal_logs = bot.get_channel(canal_logs_id)

    if tempo_de_conta < 7 * 24 * 60 * 60:
        try:
            await member.send("🚫 Sua conta é muito nova para entrar neste servidor. Tente novamente mais tarde.")
        except discord.Forbidden:
            pass

        await member.kick(reason="Conta criada há menos de 7 dias.")

        if canal_logs:
            embed = discord.Embed(
                title="🛡️ Kick de Segurança",
                description=f"Usuário `{member}` foi expulso automaticamente por ter uma conta criada há menos de 7 dias.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Criada em", value=discord.utils.format_dt(member.created_at, style='F'))
            embed.add_field(name="ID", value=member.id)
            embed.set_footer(text="Sistema automático de segurança")

            await canal_logs.send(embed=embed)

# -----------------------------
# 🧠 Comandos
# -----------------------------

@bot.command()
async def ola(ctx: commands.Context):
    await ctx.reply(f"Oi, {ctx.author.name}! Tudo bem?")

@bot.command()
async def enviar_embed(ctx: commands.Context):
    embed = discord.Embed(
        title="Título da Embed",
        description="Descrição da embed",
        color=discord.Color.blue()
    )
    embed.set_image(url="attachment://karma.png")
    embed.set_thumbnail(url="attachment://karma.png")
    embed.set_footer(text="Esse é o rodapé")
    embed.set_author(
        name="Haitiz",
        icon_url="https://cdn.discordapp.com/avatars/630387870531846156/067af89c19436d3a699b1402373b1bc9.png?size=2048",
        url="https://www.youtube.com"
    )
    await ctx.reply(embed=embed, file=discord.File("karma.png", filename="karma.png"))

@bot.command()
async def membro_favorito(ctx: commands.Context):
    class MenuView(View):
        @discord.ui.select(
            placeholder="Escolha até 3 membros",
            min_values=1,
            max_values=3,
            options=[
                discord.SelectOption(label='sosa', value='1', emoji='🔥'),
                discord.SelectOption(label='vani', value='2', emoji='🎯'),
                discord.SelectOption(label='sydney', value='3', emoji='💎')
            ]
        )
        async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
            jogos = {'1': '🔥 sosa', '2': '🎯 vani', '3': '💎 sydney'}
            escolhas = select.values
            nomes_escolhidos = [f"**{jogos[val]}**" for val in escolhas]
            texto_final = " | ".join(nomes_escolhidos)

            embed = discord.Embed(
                title="⭐ Membros Favoritos",
                description=f"Você escolheu:\n{texto_final}",
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    await ctx.send("Escolha seus membros favoritos:", view=MenuView())

# -----------------------------
# 🚀 Início do Bot
# -----------------------------


bot.run(os.getenv("DISCORD_TOKEN"))
