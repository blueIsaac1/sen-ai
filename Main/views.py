from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login as login_django
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadForm
from .models import AnalisePeca
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .forms import InfosPecasForm
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer, TableStyle, Image
from reportlab.lib.pagesizes import A4
from datetime import datetime
matplotlib.use('Agg')

#logout
#upload de varios arquivos
#popup na hora do upload
#for para preencher a tabela graficos
#conteudo no footer
#grafico pizza na parte dos graficos
    


# Margens
margin_left = 1 * inch
margin_right = 1 * inch
margin_top = 1 * inch
margin_bottom = 1 * inch

@csrf_exempt
def main(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_path = f'media/{uploaded_file.name}'
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            idPeca = form.cleaned_data['idPeca']
            situPeca = 1
            IdUsuario = request.user.id
            AnalisePeca.objects.create(
                idPeca=idPeca,
                situPeca=situPeca,
                IdUsuario=IdUsuario,
                datahora=timezone.now()
            )
            return JsonResponse({'success': True, 'message': 'Upload realizado com sucesso!'})
        return JsonResponse({'success': False, 'message': 'Erro no envio do formulário.'})
    
    elif request.method == 'GET' and 'download_pdf' in request.GET:
        grafico_pizza_pandas()
        grafico_consulta_pandas()   
        df = consulta_sql_pdf()
        if df is None or df.empty:
            return HttpResponse("Erro ao consultar dados do banco de dados.", status=500)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin = 25, leftMargin = 25, topMargin = 25, bottomMargin = 25)
        elements = []
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        usuario_atual = request.user.username
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['Normal']
        title = "Relatório de Análise de Situação de Peças"
        data = f"<b>Data de Impressão</b>: {now}"
        user = f"<b>Usuário:</b> {usuario_atual}"
        texto_tabela = ("A tabela a seguir exibirá os resultados da inteligência artificial utilizando a seguinte convenção: "
                        "valores positivos serão representados por '0', e valores negativos por '1'. Esse formato facilita a "
                        "interpretação dos dados e permite uma análise mais clara dos resultados obtidos...")
        imagem_fig = "./figs/fig.png" # Caminho para a imagem requisitada 
        imagem_fig_2 = "./figs/situ_pie_chart.png"
        image_ds = "./Main/static/images/logoDS_1.png"
        elements.append(Image(image_ds, width=75, height=50))
        elements.append(Paragraph(title, title_style))  # Titulo
        elements.append(Paragraph(data, normal_style))
        elements.append(Paragraph(user, normal_style))
        elements.append(Spacer(1, 12))
        elements.append(Image(imagem_fig, width=300, height=270)) # Adiciona a imagem como um elemento 'Image' e personaliza seu tamanho após indicar o caminho definido acima
        elements.append(Paragraph(texto_tabela, normal_style))
        elements.append(Spacer(1, 12))
        # Criar a tabela a partir dos dados do DataFrame
        table_data = [['Nome da Peça', 'Situação', 'Análise']]
        for index, row in df.iterrows():
            table_data.append([row['nomePeca'], row['situPeca'], row['Análise']])
        table = Table(table_data)
        table.setStyle(TableStyle([ 
            ('BACKGROUND', (0, 0), (-1, 0), '#b9afaf'),
            ('BACKGROUND', (0, 1), (0, -1), '#ec1c24'),
            ('BACKGROUND', (0, 2), (0, -1), '#f49494'),
            ('GRID', (0, 0), (-1, -1), 1, 'black'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
        elements.append(Image(imagem_fig_2, width=273, height=225))

        # Gerar o PDF
        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=relatorio_situpeca.pdf'
        return response
    else:
        # Geração do gráfico
        conn = sqlite3.connect("./db.sqlite3") 
        query = """
        SELECT a.idLog, a.situPeca, a.idUsuario, a.datahora, a.idPeca_id, b.nomePeca
        FROM Main_analisepeca a
        JOIN Main_infospecas b on a.idPeca_id = b.idPeca;
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if 'nomePeca' in df.columns:
            pivot_table = df.pivot_table(index='nomePeca', columns='situPeca', aggfunc='size', fill_value=0)
            # Criar o gráfico
            fig, ax = plt.subplots(figsize=(12,8))
            pivot_table.plot(kind='bar', stacked=False, ax=ax, color=['#ec1c24', '#f49494'])
            ax.set_xlabel('Nome da Peça')
            ax.set_title('Número de Eventos por Nome da Peça e Situação')
            # Salvar o gráfico em um buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=200, transparent=True)
            buf.seek(0)
            plt.close(fig)
            plt.xticks(rotation=0)  
            plt.tight_layout()
        # Converter buffer em base64
            graph_url = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')
        else:
            graph_url = None

    # Outros dados
    form = UploadForm()
    users = User.objects.all()
    analises = AnalisePeca.objects.all()
    username = request.user.username

    return render(request, 'index.html', {
        'auth_users': users,
        'analises': analises,
        'form': form,
        'username': username,
        'graph_url': graph_url, # Passar a URL do gráfico para o template
    })



# GRAFICO PARA TESTE
def graficos(request):
    conn = sqlite3.connect("./db.sqlite3") 
    query = """
    SELECT a.idLog, a.situPeca, a.idUsuario, a.datahora, a.idPeca_id, b.nomePeca
    FROM Main_analisepeca a
    JOIN Main_infospecas b on a.idPeca_id = b.idPeca;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    if 'nomePeca' in df.columns:
        pivot_table = df.pivot_table(index='nomePeca', columns='situPeca', aggfunc='size', fill_value=0)
        # Criar o gráfico
        fig, ax = plt.subplots(figsize=(14,8))
        pivot_table.plot(kind='bar', stacked=False)
        ax.set_xlabel('(1 = Bom | 2 = Ruim)')
        ax.set_ylabel('Número de Eventos')
        ax.set_title('Número de Eventos por Nome da Peça e Situação')
        # Salvar o gráfico em um buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        plt.close(fig)
        plt.xticks(rotation=0)  
        plt.tight_layout()
        # Converter buffer em base64
        graph_url = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')
    else:
        graph_url = None
    return render(request, 'graficos.html', {
        'graph_url': graph_url  # Passar a URL do gráfico para o template
    })



# UPLOAD_FILE EM USO
def upload_file1(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Salvar o arquivo
            uploaded_file = request.FILES['file']
            file_path = f'media/{uploaded_file.name}'
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            # Obter o ID da peça selecionada
            idPeca = form.cleaned_data['idPeca']
            situPeca = 2  # Suponha que você tenha uma lógica para determinar isso
            IdUsuario = request.user.id
            # Registrar a análise
            AnalisePeca.objects.create(
                idPeca=idPeca,
                situPeca=situPeca,
                IdUsuario=IdUsuario,
                datahora=timezone.now()  # O timestamp é automaticamente adicionado
            )
            messages.success(request, 'Form submission successful')  # Redireciona para uma página de sucesso
    else:
        form = UploadForm()
    return render(request, 'upload.html', {'form': form})

# SEM USO
def cadastrar_peca(request):
    if request.method == 'POST':
        form = InfosPecasForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Redireciona para uma lista de peças ou outra página após salvar
    else:
        form = InfosPecasForm()
    return render(request, 'cadastrar_peca.html', {'form': form})



# LOGIN
@csrf_exempt
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'login.html', {'error_message': 'E-mail ou senha incorretos!'})

        user = authenticate(username=user.username, password=password)
        if user:
            login_django(request, user)
            return redirect(main)
        else:
            return render(request, 'login.html', {'error_message': 'E-mail ou senha incorretos!'})
        


# DATA FRAME
def consulta_sql_pdf():    
    try:
        conn = sqlite3.connect("./db.sqlite3")
        query = """
        SELECT b.nomePeca, a.situPeca, COUNT(*) AS Análise
        FROM Main_analisepeca a
        JOIN Main_infospecas b ON a.idPeca_id = b.idPeca
        WHERE a.situPeca IN (1, 2)
        GROUP BY b.nomePeca, a.situPeca;
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return None



# BARRAS
def grafico_consulta_pandas():
    try:
        conn = sqlite3.connect("./db.sqlite3")
        query = """
        SELECT a.idLog, a.situPeca, a.idUsuario, a.datahora, a.idPeca_id, b.nomePeca
        FROM Main_analisepeca a
        JOIN Main_infospecas b on a.idPeca_id = b.idPeca;
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if 'nomePeca' in df.columns:
            pivot_table = df.pivot_table(index='nomePeca', columns='situPeca', aggfunc='size', fill_value=0)
            # Criar o gráfico
            fig, ax = plt.subplots(figsize=(6, 5))
            pivot_table.plot(kind='bar', stacked=False, color=['#ec1c24', '#f49494'], ax=ax)
            # Configurar labels e título
            ax.set_xlabel('(1 = Bom | 2 = Ruim)')
            ax.set_title('Número de Eventos por Nome da Peça e Situação')
            # Ajustar o limite do eixo y baseado no valor máximo
            max_value = pivot_table.values.max()
            ax.set_ylim(0, max_value + 4)  # Adiciona uma margem de 10%
            # Configurar a rotação dos ticks no eixo x e ajustar layout
            plt.xticks(rotation=0)
            plt.tight_layout()
            # Salvar o gráfico em um arquivo
            plt.savefig('./figs/fig.png')
            plt.close(fig)
        else:
            print("A coluna 'nomePeca' não foi encontrada no DataFrame.")
            print(df)
    except ValueError as e:
        print(f"Erro ao consultar o banco de dados: {e}")



# PIZZA
def grafico_pizza_pandas():
    conn = sqlite3.connect("./db.sqlite3")
    # Consulta SQL para buscar os dados
    query = """
    SELECT a.idLog, a.situPeca, a.idUsuario, a.datahora, a.idPeca_id, b.nomePeca
    FROM Main_analisepeca a
    JOIN Main_infospecas b on a.idPeca_id = b.idPeca;
    """
    # Ler os dados em um DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()
    # Verificar se as colunas 'situPeca' e 'nomePeca' estão presentes
    if 'situPeca' in df.columns and 'nomePeca' in df.columns:
        # Agregar os dados por nome da peça e situação
        situ_counts = df.groupby('nomePeca')['situPeca'].value_counts().unstack().fillna(0)
        # Plotar um gráfico de pizza para cada peça
        for piece in situ_counts.index:
            plt.figure(figsize=(4, 5))
            situ_counts.loc[piece].plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=['#ec1c24', '#f49494'])
            # Definir propriedades do título
            plt.title(
                f'Distribuição da Situação para {piece}',
                fontsize=16,  # Ajustar o tamanho da fonte para que o texto caiba bem
                fontweight='bold',
                color='#000000',  # Alterar a cor do título para preto para melhor contraste
                family='Arial'
            )
            plt.tight_layout()
            # Salvar a figura com fundo transparente e ajustada ao conteúdo
            plt.savefig(f'./figs/situ_pie_chart.png', transparent=True, bbox_inches='tight', pad_inches=0.1)
            plt.close()
    else:
        print("As colunas 'situPeca' e/ou 'nomePeca' não foram encontradas no DataFrame.")
        print(df)

