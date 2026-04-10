from django.db import models


class Bulletin(models.Model):
    eleve = models.ForeignKey('eleves.Eleve', on_delete=models.CASCADE, related_name='bulletins')
    inscription = models.ForeignKey('eleves.Inscription', on_delete=models.CASCADE, related_name='bulletins')
    cycle = models.ForeignKey('finances.CycleConfig', on_delete=models.SET_NULL, related_name='bulletins', null=True, blank=True)
    periode = models.CharField(max_length=50)
    date_generation = models.DateField(auto_now_add=True)
    moyenne_generale = models.DecimalField(max_digits=5, decimal_places=2)
    rang = models.PositiveIntegerField(default=0)
    mention = models.CharField(max_length=50, blank=True)
    appreciation = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='bulletins/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Bulletin'
        verbose_name_plural = 'Bulletins'
        ordering = ['-date_generation']
    
    def __str__(self):
        return f"Bulletin {self.eleve} - {self.periode}"
