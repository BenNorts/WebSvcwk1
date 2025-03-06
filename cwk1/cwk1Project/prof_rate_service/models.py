from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

# Create your models here.
class Module(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return u'%s %s' % (self.code, self.name)

class Professor(models.Model):
    name = models.CharField(max_length=30)
    professor_code = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return u'%s %s' % (self.professor_code, self.name)

class ModuleInstance(models.Model):
    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    academic_year = models.PositiveIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(3000)]
    )

    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES)
    professors = models.ManyToManyField(Professor)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['module', 'academic_year', 'semester'],
                name='unique_module_Instance'
            )
        ]

    def __str__(self):
        return u'%s %s %s' % (self.module, self.academic_year, self.semester)

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module_instance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'module_instance', 'professor'],
                name='unique_rating'
            )
        ]

    def clean(self):
        if not self.module_instance.professors.filter(id=self.professor.id).exists():
            raise ValidationError('The selected professor does not teach this module instance.')
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return u'%s %s %s' % (self.module_instance, self.professor, self.user)