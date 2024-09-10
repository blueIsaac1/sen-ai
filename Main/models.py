<<<<<<< HEAD
from django.db import models
from django.contrib.auth.models import User

class InfosPecas(models.Model):
    idPeca = models.AutoField(primary_key=True)  # AUTO_INCREMENT em Django
    nomePeca = models.CharField(max_length=255, unique=True)
    situPeca = models.IntegerField()
    fornecedorPeca = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nomePeca

class AnalisePeca(models.Model):
    idLog = models.AutoField(primary_key=True)  # AUTO_INCREMENT em Django
    idPeca = models.ForeignKey(InfosPecas, on_delete=models.CASCADE)
    situPeca = models.IntegerField()
    IdUsuario = models.IntegerField(User)
    datahora = models.DateTimeField(auto_now_add=True)  # Adiciona automaticamente o timestamp

    def __str__(self):
        return f"Análise {self.idLog} - {self.idPeca.nomePeca}"
=======
from django.db import models
from django.contrib.auth.models import User

class InfosPecas(models.Model):
    idPeca = models.AutoField(primary_key=True)  # AUTO_INCREMENT em Django
    nomePeca = models.CharField(max_length=255, unique=True)
    situPeca = models.IntegerField()
    fornecedorPeca = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nomePeca

class AnalisePeca(models.Model):
    idLog = models.AutoField(primary_key=True)  # AUTO_INCREMENT em Django
    idPeca = models.ForeignKey(InfosPecas, on_delete=models.CASCADE)
    situPeca = models.IntegerField()
    IdUsuario = models.IntegerField(User)
    datahora = models.DateTimeField(auto_now_add=True)  # Adiciona automaticamente o timestamp

    def __str__(self):
        return f"Análise {self.idLog} - {self.idPeca.nomePeca}"
>>>>>>> 930e0c7 (Teste de primeiro git)
