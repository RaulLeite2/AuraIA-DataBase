import discord
from discord.ext import commands
import psycopg2
import matplotlib.pyplot as plt
from io import BytesIO

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="db.", intents=intents)

db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}


@bot.command()
async def select(ctx, coluna, tabela):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        cursor.execute(f"SELECT {coluna} FROM {tabela}")
        results = cursor.fetchall()

        await ctx.send("Resultados:")
        for row in results:
            await ctx.send(row)

    except psycopg2.Error as e:
        await ctx.send(f"Erro 404: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@bot.command()
async def clear(ctx, tablename):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Executa um comando para apagar todos os registros da tabela
        clear_query = f"DELETE FROM {tablename}"
        cursor.execute(clear_query)
        connection.commit()

        await ctx.send(f"Todos os registros da tabela {tablename} foram removidos!")

    except psycopg2.Error as e:
        await ctx.send(f"Erro ao conectar ao banco de dados: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@bot.command()
async def insert(ctx, tabela, coluna, value):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        insert_query = f"INSERT INTO {tabela} ({coluna}) VALUES ({value})"
        cursor.execute(insert_query)
        connection.commit()

        await ctx.send(f"Valor {value} inserido na tabela {tabela} com sucesso!")

    except psycopg2.Error as e:
        await ctx.send(f"Erro ao conectar ao banco de dados: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@bot.command()
async def create(ctx, tablename, columnname, datatype):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Exemplo: Criação de uma tabela com a coluna especificada pelo usuário
        create_query = f"CREATE TABLE {tablename} ({columnname} {datatype});"
        cursor.execute(create_query)
        connection.commit()

        await ctx.send(f"Tabela {tablename} criada com sucesso com a coluna {columnname}!")

    except psycopg2.Error as e:
        await ctx.send(f"Erro ao conectar ao banco de dados: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@bot.command()
async def execute(ctx, *, query):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        cursor.execute(query)

        # Verifica se a consulta é do tipo SELECT
        if query.lower().startswith("select"):
            results = cursor.fetchall()
            await ctx.send("Resultados:")
            for row in results:
                await ctx.send(row)
        else:
            await ctx.send("Comando executado com sucesso!")

    except psycopg2.Error as e:
        await ctx.send(f"Erro ao executar a consulta: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@bot.command()
async def grafic(ctx, coluna, tabela):
    try:
        await ctx.send("Qual tipo de gráfico você deseja criar? Digite 1 para Linhas ou 2 para Barras.")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        response = await bot.wait_for("message", check=check, timeout=30)

        if response.content == "1":
            chart_type = "linhas"
            plot_function = plt.plot
        elif response.content == "2":
            chart_type = "barras"
            plot_function = plt.bar
        else:
            await ctx.send("Opção inválida. O gráfico será criado com linhas por padrão.")
            chart_type = "linhas"
            plot_function = plt.plot

        await response.delete()  # Exclui a mensagem de escolha do usuário

        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        cursor.execute(f"SELECT {coluna} FROM {tabela}")
        results = cursor.fetchall()

        values = [row[0] for row in results]
        positions = list(range(1, len(values) + 1))  # Define posições para as barras

        plot_function(positions, values)  # Adiciona as posições como primeiro argumento
        plt.xlabel('Períodos')
        plt.ylabel('Valores')
        plt.title(f'Gráfico de {chart_type.capitalize()} da Coluna {coluna} na Tabela {tabela}')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        await ctx.send(file=discord.File(buffer, filename='chart.png'))

    except psycopg2.Error as e:
        await ctx.send(f"Erro 404: {e}")

@bot.command()
async def list_tables(ctx):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Consulta para obter a lista de tabelas no banco de dados
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = cursor.fetchall()

        if not tables:
            await ctx.send("Não há tabelas no banco de dados.")
            return

        # Para cada tabela, obtém a lista de colunas
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'")
            columns = cursor.fetchall()

            if columns:
                columns_list = ", ".join(column[0] for column in columns)
                await ctx.send(f"Tabela: {table_name}, Colunas: {columns_list}")
            else:
                await ctx.send(f"Tabela: {table_name}, Não há colunas.")

    except psycopg2.Error as e:
        await ctx.send(f"Erro ao conectar ao banco de dados: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
bot.run("MTEyNDg5NTU3NjE5OTI3ODYxMg.GxLENu.8jHrc1i3DgEUDRpLEMZQabGSBt_qhTfY4C314c")
