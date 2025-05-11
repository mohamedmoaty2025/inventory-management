from django.db import models

class Products(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits= 10 ,decimal_places=2)
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products_image/',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
