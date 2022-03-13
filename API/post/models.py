from django.db import models
from django.utils.timezone import now


class Post(models.Model):
    title = models.CharField(max_length=100, verbose_name="title")
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey('user.User', on_delete=models.PROTECT)
    image = models.ImageField(upload_to="image/post/", blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(default=now)
    
    class Meta:
        ordering = ("-timestamp",)
        
    def __str__(self):
        return self.title


class Like(models.Model):
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)

    class Meta:
        ordering = ("-timestamp",)
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user} {self.post}"