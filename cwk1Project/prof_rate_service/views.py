from django.db import DatabaseError, IntegrityError
from django.core.exceptions import FieldError, ValidationError
from django.http import JsonResponse, HttpResponse
from .models import ModuleInstance, Professor, Rating
from django.db.models import Avg, F, IntegerField
from django.db.models.functions import Round, Cast
import logging
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group


#-------------------------------------------------------------------------
# Service Option 1: allModuleInstances
# Returns: A list of all module instances and the professors teaching them:
#          [module_code, module_name, academic_year, semester, taught_by]
#-------------------------------------------------------------------------
def allModuleInstances(request):

    logger = logging.getLogger(__name__)

    # Try fetch all module instances, along with their related professors and modules
    try:
        query = (ModuleInstance.objects.prefetch_related('professors')
                .select_related('module')
        )
    
    # Catch exceptions if query fails + return error messages with relevant HTTP codes
    except DatabaseError as e:
        logger.exception('Database error: %s', str(e))
        return JsonResponse({'error': 'Database encountered an error.'}, status=500)
    except Exception as e:
        logger.exception('Unexpected error: %s', str(e))
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
    
    if not query:
        logger.info('allModuleInstances query returned no results.')
        return JsonResponse({'module_instances': []}, safe=False, status=200)

    response = []

    # Build repsonse if query is successful
    for item in query:
        moduleInstanceData = {
            'module_code': item.module.code, # Fetched from related Module table
            'module_name': item.module.name, # Fetched from related Module table
            'academic_year': item.academic_year,
            'semester': item.semester,
            'taught_by': [] # Initialise taught_by to allow addition of professors
        }

        # Add related professors to taught_by field in response
        for p in item.professors.values_list('professor_code', 'name'):
            moduleInstanceData['taught_by'].append({'professor_code': p[0], 'professor_name': p[1]})

        # Add response data to response variable
        response.append(moduleInstanceData)

    return JsonResponse({'module_instances': response}, safe=False, status=200)



#---------------------------------------------------------------------------
# Service Option 2: allProfessorRatings
# Returns: A list of each professor along with their overall rating:
#          [professor code, professor name, avg rating across all instances]
#---------------------------------------------------------------------------
def allProfessorRatings(request):

    logger = logging.getLogger(__name__)

    # Try fetch all professors along with their average ratings
    try:
        query = (Professor.objects
                .values(
                    'professor_code',
                    'name'
                )
                .annotate(rating=Cast(Round(Avg('rating__rating')), IntegerField()))
        )
    
    # Catch exceptions if query fails + return error messages with relevant HTTP codes
    except DatabaseError as e:
        logger.exception('Database error: %s', str(e))
        return JsonResponse({'error': 'Database encountered an error.'}, status=500)
    except Exception as e:
        logger.exception('Unexpected error: %s', str(e))
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
    
    if not query:
        logger.info('Searching for professor ratings returned no results.')
        return JsonResponse({'module_instances': []}, safe=False, status=200)

    # Query result has all information we need
    # Therefore no need to build up response, simply list
    response = list(query)

    return JsonResponse({'all_professor_ratings': response}, safe=False, status=200)



#-------------------------------------------------------------------------
# Service Option 3: professorModuleRating
# Returns: A professor's avg rating for a specific module instance:
#          [professor name, professor code, the module instance code,
#          the module instance name, avg professor rating for instance]
#-------------------------------------------------------------------------
def professorModuleRating(request, professorCode, moduleCode):

    logger = logging.getLogger(__name__)

    # Check provided professor code is of a valid format
    if not professorCode.isalnum():
        logger.warning('Invalid professor code', professorCode)
        return JsonResponse({'error': 'Provided professor code is invalid.'}, status=400)
    
    # Check provided module code is of a valid format
    if not moduleCode.isalnum():
        logger.warning('Invalid module code', moduleCode)
        return JsonResponse({'error': 'Provided module code is invalid.'}, status=400)

    # Try fetch all rating objects for a professor and module instance,
    # and calculate avg rating across retrieved ratings
    try:
        query = (Rating.objects
            .filter(
                module_instance__module__code=moduleCode,
                professor__professor_code=professorCode
            )
            .values(
                module_code=F('module_instance__module__code'),
                module_name=F('module_instance__module__name'),
                professor_code=F('professor__professor_code'),
                professor_name=F('professor__name')
            )
            .annotate(rating=Cast(Round(Avg('rating')), IntegerField()))
        )

    # Catch exceptions if query fails + return error messages with relevant HTTP codes
    except FieldError as e:
        logger.exception('Field error: %s', str(e))
        return JsonResponse({'error': 'Invalid field name or query parameters.'}, status=400)
    except DatabaseError as e:
        logger.exception('Database error: %s', str(e))
        return JsonResponse({'error': 'Database encountered an error.'}, status=500)
    except Exception as e:
        logger.exception('Unexpected error: %s', str(e))
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

    if not query:
        logger.info('professorModuleRating query returned no results.')
        return JsonResponse({'error': 'Professor ' + professorCode + ' does not teach Module ' + moduleCode}, status=404)
    

    # Query result has all information we need
    # Therefore no need to build up response, simply list
    response = list(query)

    return JsonResponse({'professor_module_rating': response}, safe=False, status=200)




#---------------------------------------------------------------------------
# Service Option 4: rateProfessor
# Returns: Success message that rating has been added to database
#---------------------------------------------------------------------------
@login_required
@csrf_exempt
def rateProfessor(request):
    
    logger = logging.getLogger(__name__)

    # Only try process request if POST method is used
    # Else return 405 error
    if request.method == "POST":
        professorCode = request.POST.get("professor_code")
        moduleCode = request.POST.get("module_code")
        academicYear = request.POST.get("year")
        moduleSemester = request.POST.get("semester")
        userRating = request.POST.get("rating")

        # Check user rating can be converted into an integer
        try:
            userRating = int(userRating)
        except ValueError:
            logger.exception('Rating error: Provided rating is not an integer.')
            return JsonResponse({'error': 'Provided rating must be a number between 1 and 5.'}, status=400)

        # Check user rating is between 1 and 5
        if userRating < 1 or userRating > 5:
            logger.exception('Rating error: Provided rating is not between 1 and 5.')
            return JsonResponse({'error': 'Provided rating must be between 1 and 5.'}, status=400)
        
        # Check academic year can be converted into an integer
        try:
            academicYear = int(academicYear)
        except ValueError:
            logger.exception('Year error: Provided year is not an integer.')
            return JsonResponse({'error': 'Provided year must be a year between 2000 and 3000.'}, status=400)
        
        # Check academic year is within model constraints
        if academicYear < 2000 or academicYear > 3000:
            logger.exception('Year error: Provided year is not between 2000 and 3000.')
            return JsonResponse({'error': 'Provided year must be between 2000 and 3000.'}, status=400)
        
        # Check module semester can be converted into an integer
        try:
            moduleSemester = int(moduleSemester)
        except ValueError:
            logger.exception('Semester error: Provided semester is not an integer.')
            return JsonResponse({'error': 'Provided semester must be either be 1 or 2.'}, status=400)
        
        # Check module semester is within model constraints
        if moduleSemester < 1 or moduleSemester > 2:
            logger.exception('Semester error: Provided semester is neither 1 nor 2.')
            return JsonResponse({'error': 'Provided semester must be be either 1 or 2.'}, status=400)


        try:
            # Try fetch user specified professor and module instance from database
            professor = Professor.objects.get(professor_code=professorCode)
            moduleInstance = ModuleInstance.objects.get(academic_year=academicYear,
                                                        semester=moduleSemester,
                                                        module__code=moduleCode)
            
            # Add new rating to database for specified professor and module instance
            (Rating.objects
                    .create(
                        user=request.user,
                        module_instance=moduleInstance,
                        professor=professor,
                        rating=userRating
                    )
            )

            return JsonResponse({'professor_module_rating': 'Rating successfully added to system.'}, status=201)

        # Catch exceptions if any query fails + return error messages with relevant HTTP codes
        except Professor.DoesNotExist as e:
            logger.exception('DoesNotExist error: %s', str(e))
            return JsonResponse({'error': 'Provided professor code is invalid'}, status=404)
        except ModuleInstance.DoesNotExist as e:
            logger.exception('DoesNotExist error: %s', str(e))
            return JsonResponse({'error': 'Provided module instance is invalid. Please check the module code, year, and semester.'}, status=404)
        except ValidationError as e:
            logger.exception('Validation error: %s', str(e))
            return JsonResponse({'error': e.message}, status=400)
        except IntegrityError as e:
            logger.exception('Integrity error: %s', str(e))
            return JsonResponse({'error': 'This rating has previously been made for this professor and module instance.'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method used. Please try again with a POST request.'}, status=405)


#---------------------------------------------------------------------------
# Service: registerUser
# Returns: Success message that user has been added to database
#---------------------------------------------------------------------------
def registerUser(request):
    logger = logging.getLogger(__name__)

    # Only try process request if POST method is used
    # Else return 405 error
    if request.method == "POST":
        try:
            username = request.POST.get("new_username")
            email = request.POST.get("new_email")
            password = request.POST.get("new_password")

            # Check if provided email is already in use
            if User.objects.filter(email=email).exists():
                logger.info('Email error: tried to register with email already in use.')
                return JsonResponse({'error': 'Email already in use. Please register with a different email.'}, status=400)
            
            # Check if provided username is already in use
            if User.objects.filter(username=username).exists():
                logger.info('Username error: tried to register with username already in use.')
                return JsonResponse({'error': 'Username already in use. Please use a different username.'}, status=400)
            
            # Create new user with provided username, email, and password
            newUser = User.objects.create_user(username=username, email=email, password=password)

            # Add new user to Student permissions group
            studentGroup = Group.objects.get(name='Student')
            newUser.groups.add(studentGroup)

            return JsonResponse({'register_user': 'User registered successfully.'}, status=201)
        
        # Catch exceptions if any query fails + return error messages with relevant HTTP codes
        except IntegrityError as e:
            logger.exception('Integrity error: %s', str(e))
            return JsonResponse({'error': 'An internal error occured during user creation.'}, status=500)
        except ValidationError as e:
            logger.exception('Validation error: %s', str(e))
            return JsonResponse({'error': 'Input data is invalid. Please ensure you have submitted correctly formatted username, email, and password.'}, status=400)
        except KeyError as e:
            logger.exception('Key error: %s', str(e))
            return JsonResponse({'error': 'User creation failed due to missing values for either username, email, or password.'}, status=400)
        except Group.DoesNotExist:
            logger.exception('Group error: permission group does not exist.')
            return JsonResponse({'error': 'Unexpected error occurred when creating user.'}, status=500)
        except Exception as e:
            logger.exception('Unexpected error: %s', str(e))
            return JsonResponse({'error': 'An unexpected error occurred during user registration.'}, status=500)
        
    return JsonResponse({'error': 'Invalid request method used. Please try again with a POST request.'}, status=405)


#---------------------------------------------------------------------------
# Service: homeView
# Returns: String. Used for redirection post-login.
#---------------------------------------------------------------------------
def homeView(request):
    return HttpResponse("Welcome to the home page!")