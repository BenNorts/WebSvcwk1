from django.urls import path
from . import views

urlpatterns = [
    path('allModuleInstances/', views.allModuleInstances, name='allModuleInstances'),
    path('allProfessorRatings/', views.allProfessorRatings, name='allProfessorRatings'),
    path('professorModuleRating/<str:professorCode>/<str:moduleCode>/', views.professorModuleRating, name='professorModuleRating'),
    path('rateProfessor/', views.rateProfessor, name='rateProfessor'),
    path('', views.homeView, name='home'),
    path('registerUser/', views.registerUser, name='registerUser')
]