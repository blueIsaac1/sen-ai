from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login as login_django
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
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
import re
import os
import base64
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer, TableStyle, Image
from reportlab.lib.pagesizes import A4
from datetime import datetime
from keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model
import numpy as np
from django.conf import settings
from Main.models import InfosPecas, ImagePrediction
from django.http import HttpResponseRedirect
import time as tmp
from datetime import datetime
matplotlib.use('Agg')

#lastversion

today = datetime.now().date()
model_path = os.path.join(settings.MEDIA_ROOT_2, 'meu_modelo.keras')

# Verificar se o modelo existe
if not os.path.isfile(model_path):
    raise FileNotFoundError(f"O modelo não foi encontrado no caminho: {model_path}")

# Carregar o modelo
model = load_model(model_path)

def get_first_file_from_directory(directory_path):
    try:
        files = os.listdir(directory_path)
        # Filtra apenas arquivos
        files = [f for f in files if os.path.isfile(os.path.join(directory_path, f))]
        # Se houver arquivos, retorna o caminho do primeiro
        if files:
            first_file = files[0]
            return os.path.join(directory_path, first_file)
        else:
            print("Nenhum arquivo encontrado no diretório.")
            return None
    except FileNotFoundError:
        print(f"O diretório {directory_path} não foi encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao acessar o diretório: {e}")
        return None

def predict_image(model, image_path, img_height, img_width):
    img = load_img(image_path, target_size=(img_width, img_height))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255
    prediction = model.predict(img_array)
    return prediction

def get_class_label(prediction, class_indices):
    class_label = list(class_indices.keys())[np.argmax(prediction)]
    return class_label

def guardar_analise(image_path, class_label, peca_id):
    try:
        timestamp = timezone.now()
        try:
            peca = InfosPecas.objects.get(idPeca=peca_id)
        except InfosPecas.DoesNotExist:
            print(f"Peça com id {peca_id} não encontrada.")
            return
        
        # Cria uma nova análise
        ImagePrediction.objects.create(
            image_path=image_path,
            class_label=class_label,
            timestamp=timestamp,
            peca=peca
        )
        return class_label
    except Exception as e:
        # Captura e imprime qualquer exceção
        print(f"Erro ao guardar a análise: {e}")

def get_db_path_from_project_root(db_name):
    # Obtém o diretório atual do script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navega um nível acima
    parent_dir = os.path.dirname(current_dir)
    # Constrói o caminho completo para o banco de dados
    db_path = os.path.join(parent_dir, db_name)
    return db_path

def ensure_directory_exists(directory):
    """Cria o diretório se ele não existir."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def consulta_label():
    conn = sqlite3.connect("./db.sqlite3")
    cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
    # Consulta para selecionar o último item inserido
    query = """
    SELECT class_label
    FROM Main_imageprediction
    ORDER BY id DESC
    LIMIT 1
    """
    cursor.execute(query)  # Executa a consulta
    last_label = cursor.fetchone()  # Obtém o último registro
    conn.close()  # Fecha a conexão
    return re.sub(r'[^a-zA-Z\s]', '', last_label[0])

@csrf_exempt
@login_required(login_url='/auth/')
def main(request):
    last_label = consulta_label()
    is_staff = request.user.is_staff 
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_path = f'IA_Imagens/_Verificar/{uploaded_file.name}'
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Previsão de IA
            class_indices = { 'Bom': 0, 'Ruim': 1 }  # Ajuste conforme seus índices de classe
            prediction = predict_image(model, file_path, 150, 150)
            class_label = get_class_label(prediction, class_indices)           
            # Insert no banco de dados
            image_path = "Null"
            peca_id = 1
            guardar_analise(image_path, class_label, peca_id)
            # Mover o arquivo para a pasta _Analisadas
            analyzed_directory = 'IA_Imagens/_Analisadas'
            if not os.path.exists(analyzed_directory):
                os.makedirs(analyzed_directory)
            new_file_path = os.path.join(analyzed_directory, uploaded_file.name)
            os.rename(file_path, new_file_path)
            request.session['analise_resultado'] = class_label
            return HttpResponseRedirect("/auth/home/#upload")
        return HttpResponse('Erro ao processar o formulário.')
    
    # GERAÇÃO PDF GERAL
    elif request.method == 'GET' and 'download_pdf' in request.GET:
        matplotlib.rcParams['text.color'] = 'black'
        matplotlib.rcParams['axes.labelcolor'] = 'black'
        matplotlib.rcParams['xtick.color'] = 'black'
        matplotlib.rcParams['ytick.color'] = 'black'
        matplotlib.rcParams['axes.edgecolor'] = 'black'
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
                        "valores positivos serão representados por 'Bom' e 'Ruim' Esse formato facilita a "
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
            table_data.append([row['nomePeca'], row['class_label'], row['Análise']])
        table = Table(table_data)
        table.setStyle(TableStyle([ 
            ('BACKGROUND', (0, 0), (-1, 0), '#b9afaf'),
            ('BACKGROUND', (0, 1), (0, -1), '#f49494'),
            ('BACKGROUND', (0, 2), (0, -1), '#ec1c24'),
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
    # GERAÇÃO PDF GERAL TODAY
    elif request.method == 'GET' and verificar_registros_hoje() == True and 'download_pdf_today' in request.GET:
        matplotlib.rcParams['text.color'] = 'black'
        matplotlib.rcParams['axes.labelcolor'] = 'black'
        matplotlib.rcParams['xtick.color'] = 'black'
        matplotlib.rcParams['ytick.color'] = 'black'
        matplotlib.rcParams['axes.edgecolor'] = 'black'
        grafico_pizza_pandas_today()
        grafico_consulta_pandas_today()   
        df = consulta_sql_pdf_today()
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
                        "valores positivos serão representados por 'Bom' e 'Ruim' Esse formato facilita a "
                        "interpretação dos dados e permite uma análise mais clara dos resultados obtidos...")
        imagem_fig = "./figs/fig_today.png" # Caminho para a imagem requisitada 
        imagem_fig_2 = "./figs/situ_pie_chart_today.png"
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
            table_data.append([row['nomePeca'], row['class_label'], row['Análise']])
        table = Table(table_data)
        table.setStyle(TableStyle([ 
            ('BACKGROUND', (0, 0), (-1, 0), '#b9afaf'),
            ('BACKGROUND', (0, 1), (0, -1), '#f49494'),
            ('BACKGROUND', (0, 2), (0, -1), '#ec1c24'),
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
    
    elif request.method == 'GET' and 'logout_user' in request.GET:
        logout(request)  # Realiza o logout do usuário
        return redirect('/auth/')  # Redireciona para a página de login
    else:
        # Geração do gráfico (lightMode)
        matplotlib.rcParams['text.color'] = 'black'
        matplotlib.rcParams['axes.labelcolor'] = 'black'
        matplotlib.rcParams['xtick.color'] = 'black'
        matplotlib.rcParams['ytick.color'] = 'black'
        matplotlib.rcParams['axes.edgecolor'] = 'black'
        conn = sqlite3.connect("./db.sqlite3") 
        query = """
        SELECT a.id, a.class_label, a.timestamp, b.idPeca, b.nomePeca
        FROM Main_imageprediction a
        JOIN Main_infospecas b ON a.peca_id = b.idPeca;

        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if 'class_label' in df.columns:
            # Contar a quantidade de ocorrências por class_label
            class_counts = df['class_label'].value_counts()
            
            # Criar o gráfico de pizza
            fig, ax = plt.subplots(figsize=(10,6))
            ax.pie(class_counts, labels=class_counts.index, autopct='%1.1f%%', colors=['#AB0B12', '#F97A82'], startangle=140)
            ax.set_title('Distribuição das Classes')
            
            # Salvar o gráfico em um buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=200, transparent=True)
            buf.seek(0)
            plt.close(fig)
            
            # Converter buffer em base64
            graph_url = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')
        else:
            graph_url = None
        
        # Geração do Gráfico (darkMode)
        matplotlib.rcParams['text.color'] = 'white'
        matplotlib.rcParams['axes.labelcolor'] = 'white'
        matplotlib.rcParams['xtick.color'] = 'white'
        matplotlib.rcParams['ytick.color'] = 'white'
        matplotlib.rcParams['axes.edgecolor'] = 'white'
        conn = sqlite3.connect("./db.sqlite3") 
        query = """
        SELECT a.id, a.class_label, a.timestamp, b.idPeca, b.nomePeca
        FROM Main_imageprediction a
        JOIN Main_infospecas b ON a.peca_id = b.idPeca;

        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if 'class_label' in df.columns:
            # Contar a quantidade de ocorrências por class_label
            class_counts = df['class_label'].value_counts()
            
            # Criar o gráfico de pizza
            fig, ax = plt.subplots(figsize=(10,6))
            ax.pie(class_counts, labels=class_counts.index, autopct='%1.1f%%', colors=['#28425E', '#6098A2'], startangle=140)
            ax.set_title('Distribuição das Classes')
            
            # Salvar o gráfico em um buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=200, transparent=True)
            buf.seek(0)
            plt.close(fig)
            
            # Converter buffer em base64
            graph_url_dark = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')
        else:
            graph_url_dark = None

    # Outros dados
    form = UploadForm()
    users = User.objects.all()
    analises = AnalisePeca.objects.all()
    predictions = ImagePrediction.objects.all()
    infospecas_ = InfosPecas.objects.all()
    username = request.user.username

    # Preparar um dicionário para armazenar a contagem por peça
    contagem_por_peca = {}
    contagem_por_peca_ruim = {}
    for peca in infospecas_:
        # Filtrar previsões para cada peça
        previsoes_peca = predictions.filter(peca_id=peca.idPeca)
        # Contar quantas previsões são "Bom" para essa peça
        contagem_bom = previsoes_peca.filter(class_label="Bom").count()

        contagem_ruim = previsoes_peca.filter(class_label='Ruim').count()
        # Adicionar ao dicionário
        contagem_por_peca[peca.nomePeca] = contagem_bom
        contagem_por_peca_ruim[peca.nomePeca] = contagem_ruim

    # Criar o DataFrame
    df = pd.DataFrame({
        'Nome da Peça': list(contagem_por_peca.keys()),
        'Análise (Bom)': list(contagem_por_peca.values()),
        'Análise (Ruim)': list(contagem_por_peca_ruim.values())
    })

    # Converter o DataFrame para HTML
    html_table = df.to_html(index=False, classes='tabelaDataFrame')

    grafico_consulta_pandas_today()
    grafico_pizza_pandas_today()
    verificar_registros_hoje()
    analise_resultado = request.session.pop('analise_resultado', None)
    return render(request, 'index.html', {
        'auth_users': users,
        'analises': analises,
        'form': form,
        'username': username,
        'graph_url': graph_url, # Passar a URL do gráfico para o template
        'graph_url_dark': graph_url_dark, # Passar a URL do gráfico DARK para o template
        'is_staff': is_staff,
        'html_table': html_table,
        'consulta_label': consulta_label(),
        'is_ruim': consulta_label() == 'Ruim',
        'is_bom': consulta_label() == 'Bom',
        'verify_today': verificar_registros_hoje(),
        'analise_resultado': analise_resultado

        # Linkar a variavel com o html/javascript
    })



# GRAFICO PARA TESTE
def graficos(request):
    matplotlib.rcParams['text.color'] = 'black'
    matplotlib.rcParams['axes.labelcolor'] = 'black'
    matplotlib.rcParams['xtick.color'] = 'black'
    matplotlib.rcParams['ytick.color'] = 'black'
    matplotlib.rcParams['axes.edgecolor'] = 'black'
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
        SELECT b.nomePeca, a.class_label, COUNT(*) AS Análise
        FROM Main_imageprediction a
        JOIN Main_infospecas b ON a.peca_id = b.idPeca
        WHERE a.class_label IN ('Bom', 'Ruim')
        GROUP BY b.nomePeca, a.class_label;
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return None

def consulta_sql_pdf_today():    
    try:
        conn = sqlite3.connect("./db.sqlite3")
        query_check = """
        SELECT COUNT(*) as count
        FROM Main_imageprediction
        WHERE DATE(timestamp) = DATE('now');
        """
        df_check = pd.read_sql_query(query_check, conn)
        if df_check['count'].iloc[0] == 0:
            print("Não há registros para a data de hoje.")
            conn.close()
            return
        conn = sqlite3.connect("./db.sqlite3")
        query = """
        SELECT b.nomePeca, a.class_label, COUNT(*) AS Análise
        FROM Main_imageprediction a
        JOIN Main_infospecas b ON a.peca_id = b.idPeca
        WHERE a.class_label IN ('Bom', 'Ruim')
        AND DATE(a.timestamp) = DATE('now')
        GROUP BY b.nomePeca, a.class_label;
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
        SELECT a.id, a.class_label, a.timestamp, b.idPeca, b.nomePeca
        FROM Main_imageprediction a
        JOIN Main_infospecas b ON a.peca_id = b.idPeca;
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if 'class_label' in df.columns:
            pivot_table = df.pivot_table(columns='class_label', aggfunc='size', fill_value=0)
            # Criar o gráfico
            fig, ax = plt.subplots(figsize=(6, 5))
            pivot_table.plot(kind='bar', stacked=False, color=['#f49494', '#ec1c24'], ax=ax)
            # Configurar labels e título
            ax.set_xlabel('Bom | Ruim')
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
            print("A coluna 'class_label' não foi encontrada no DataFrame.")
            print(df)
    except ValueError as e:
        print(f"Erro ao consultar o banco de dados: {e}")



# PIZZA
def grafico_pizza_pandas():
    conn = sqlite3.connect("./db.sqlite3")
    # Consulta SQL para buscar os dados
    query = """
    SELECT a.id, a.class_label, a.timestamp, b.idPeca, b.nomePeca
    FROM Main_imageprediction a
    JOIN Main_infospecas b ON a.peca_id = b.idPeca;
    """
    # Ler os dados em um DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()
    # Verificar se as colunas 'situPeca' e 'nomePeca' estão presentes
    if 'class_label' in df.columns and 'nomePeca' in df.columns:
        # Agregar os dados por nome da peça e situação
        situ_counts = df.groupby('nomePeca')['class_label'].value_counts().unstack().fillna(0)
        # Plotar um gráfico de pizza para cada peça
        for piece in situ_counts.index:
            plt.figure(figsize=(4, 5))
            situ_counts.loc[piece].plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=['#f49494', '#ec1c24'])
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

def grafico_consulta_pandas_today():
    try:
        conn = sqlite3.connect("./db.sqlite3")
        query_check = """
        SELECT COUNT(*) as count
        FROM Main_imageprediction
        WHERE DATE(timestamp) = DATE('now');
        """
        df_check = pd.read_sql_query(query_check, conn)
        if df_check['count'].iloc[0] == 0:
            print("Não há registros para a data de hoje.")
            conn.close()
            return
        conn = sqlite3.connect("./db.sqlite3")
        query = """
        SELECT a.id, a.class_label, a.timestamp, b.idPeca, b.nomePeca
        FROM Main_imageprediction a
        JOIN Main_infospecas b ON a.peca_id = b.idPeca
        WHERE DATE(a.timestamp) = DATE('now');
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if 'class_label' in df.columns:
            pivot_table = df.pivot_table(columns='class_label', aggfunc='size', fill_value=0)
            # Criar o gráfico
            fig, ax = plt.subplots(figsize=(6, 5))
            pivot_table.plot(kind='bar', stacked=False, color=['#f49494', '#ec1c24'], ax=ax)
            # Configurar labels e título
            ax.set_xlabel('Bom | Ruim')
            ax.set_title('Número de Eventos por Nome da Peça e Situação')
            # Ajustar o limite do eixo y baseado no valor máximo
            max_value = pivot_table.values.max()
            ax.set_ylim(0, max_value + 4)  # Adiciona uma margem de 10%
            # Configurar a rotação dos ticks no eixo x e ajustar layout
            plt.xticks(rotation=0)
            plt.tight_layout()
            # Salvar o gráfico em um arquivo
            plt.savefig('./figs/fig_today.png')
            plt.close(fig)
        else:
            print("A coluna 'class_label' não foi encontrada no DataFrame.")
            print(df)
    except ValueError as e:
        print(f"Erro ao consultar o banco de dados: {e}")



# PIZZA
def grafico_pizza_pandas_today():
    conn = sqlite3.connect("./db.sqlite3")
    query_check = """
    SELECT COUNT(*) as count
    FROM Main_imageprediction
    WHERE DATE(timestamp) = DATE('now');
    """
    df_check = pd.read_sql_query(query_check, conn)
    if df_check['count'].iloc[0] == 0:
        print("Não há registros para a data de hoje.")
        conn.close()
        return
    # Consulta SQL para buscar os dados
    query = """
    SELECT a.id, a.class_label, a.timestamp, b.idPeca, b.nomePeca
    FROM Main_imageprediction a
    JOIN Main_infospecas b ON a.peca_id = b.idPeca
    WHERE DATE(a.timestamp) = DATE('now');
    """
    # Ler os dados em um DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()
    # Verificar se as colunas 'situPeca' e 'nomePeca' estão presentes
    if 'class_label' in df.columns and 'nomePeca' in df.columns:
        # Agregar os dados por nome da peça e situação
        situ_counts = df.groupby('nomePeca')['class_label'].value_counts().unstack().fillna(0)
        # Plotar um gráfico de pizza para cada peça
        for piece in situ_counts.index:
            plt.figure(figsize=(4, 5))
            situ_counts.loc[piece].plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=['#f49494', '#ec1c24'])
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
            plt.savefig(f'./figs/situ_pie_chart_today.png', transparent=True, bbox_inches='tight', pad_inches=0.1)
            plt.close()
    else:
        print("As colunas 'situPeca' e/ou 'nomePeca' não foram encontradas no DataFrame.")
        print(df)


def verificar_registros_hoje():
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect("./db.sqlite3")
        
        # Consulta SQL para verificar registros para a data atual
        query = """
        SELECT COUNT(*) as count
        FROM Main_imageprediction
        WHERE DATE(timestamp) = DATE('now');
        """
        
        # Executar a consulta e obter o resultado
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Verificar se há registros para hoje
        registros_existentes = df['count'].iloc[0] > 0
        
        return registros_existentes
        
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return False