from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),  # Página de login
    path('home/', views.main, name='main'),  # Página inicial ou principal
    path('graficos/', views.graficos, name='graficos'),  # Página de gráficos
    path('upload/', views.upload_file1, name='upload_file'),  # Página de upload de arquivos
    path('cadastrar-peca/', views.cadastrar_peca, name='cadastrar_peca'),
]
