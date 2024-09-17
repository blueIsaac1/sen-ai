from django.contrib import admin
from Main.models import InfosPecas, AnalisePeca, ImagePrediction

@admin.register(InfosPecas)
class InfosPecasAdmin(admin.ModelAdmin):
    pass

@admin.register(AnalisePeca)
class AnalisePecaAdmin(admin.ModelAdmin):
    pass

@admin.register(ImagePrediction)
class ImagePredictionAdmin(admin.ModelAdmin):
    pass

