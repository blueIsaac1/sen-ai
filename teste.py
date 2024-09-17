import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoMain.settings')
django.setup()

from Main.models import AnalisePeca, InfosPecas
from django.contrib.auth.models import User
from datetime import datetime

def populate():
    # Dados fictícios para InfosPecas
    fictitious_infos = [
        {'nomePeca': 'Peça A'},
        {'nomePeca': 'Peça B'},
        {'nomePeca': 'Peça C'},
        {'nomePeca': 'Peça D'},
    ]

    for data in fictitious_infos:
        infos_peca, created = InfosPecas.objects.get_or_create(**data)
        if created:
            print(f"Created InfosPecas: {infos_peca}")
        else:
            print(f"Already exists InfosPecas: {infos_peca}")

    # Crie um usuário fictício
    user, created = User.objects.get_or_create(username='fictitious_user', defaults={'password': 'password'})

    # Obtenha IDs de InfosPecas
    infos_pecas_ids = InfosPecas.objects.values_list('id', flat=True)

    # Dados fictícios para AnalisePeca
    fictitious_analises = [
        {'idPeca_id': infos_pecas_ids[0], 'situPeca': 1, 'IdUsuario': user.id},
        {'idPeca_id': infos_pecas_ids[1], 'situPeca': 2, 'IdUsuario': user.id},
        {'idPeca_id': infos_pecas_ids[2], 'situPeca': 3, 'IdUsuario': user.id},
        {'idPeca_id': infos_pecas_ids[3], 'situPeca': 4, 'IdUsuario': user.id},
    ]

    for data in fictitious_analises:
        analise_peca = AnalisePeca.objects.create(**data)
        print(f"Created AnalisePeca: {analise_peca}")

if __name__ == "__main__":
    populate()
