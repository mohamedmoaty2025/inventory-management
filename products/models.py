from django.db import models




class Category(models.Model):
    name = models.CharField(max_length=255,unique= True)
    
    def __str__(self):
        return self.name
    
class Products(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits= 10 ,decimal_places=2)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='products/',null= True,blank=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True, blank=True, related_name="products")
    
    def __str__(self):
        return self.name
    
    def get_image(self):
        if self.image:
            return self.image.url
        return '/static/images/no-image.png'