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

class ImagePrediction(models.Model):
    id = models.AutoField(primary_key=True)
    image_path = models.CharField(max_length=255)
    class_label = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    
    # Relacionamento com o modelo InfosPecas
    peca = models.ForeignKey(InfosPecas, on_delete=models.CASCADE, related_name='predictions')

    def __str__(self):
        return f'{self.class_label} - {self.image_path}'