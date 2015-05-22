from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from transfusion.models import Course, Assignment


def index(request):
    if not request.user.is_authenticated():
        return render(request, 'transfusion/index.html')
    else:
        return render(request, 'transfusion/logged_in_index.html')


def search(request):

    term = request.GET.get('term')

    if not term == "":
        results = User.objects.filter(Q(username__contains=term) | Q(last_name__contains=term))
    else:
        results = None

    context = {
        'term': term,
        'results': results
    }
    
    return render(request, 'transfusion/search.html', context)


def teacher_profile(request, teacher):
    user = User.objects.get(username=teacher)

    context = {
        'user': user,
    }

    return render(request, 'transfusion/teacher_profile.html', context)


def course(request, teacher, course):
    user = User.objects.get(username=teacher)
    t_course = Course.objects.get(id=course)
    assignments = t_course.assignment_set.order_by('-due_date')
    links = t_course.link_set.order_by('-id')

    context = {
        'user': user,
        'course': t_course,
        'assignments': assignments,
        'links': links,
    }

    return render(request, 'transfusion/course.html', context)


def sign_in(request):
    if request.method != "POST":
        messages.error(request, "Please login first.")
        return HttpResponseRedirect(reverse("transfusion:index"))

    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
        else:
            messages.error(request, "Your user account has been deactivated.")
    else:
        messages.error(request, "Your user account does not exist.")
        
    return HttpResponseRedirect(reverse("transfusion:index"))


def sign_out(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return HttpResponseRedirect(reverse('transfusion:index'))


@login_required
def edit_profile(request):
    if request.method != "POST":
        return render(request, 'transfusion/edit_teacher_info.html')
    else:
        school = request.POST.get("school")
        description = request.POST.get("description")

        profile = request.user.teacherprofile

        profile.school = school
        profile.description = description

        profile.save()

        return HttpResponseRedirect(reverse('transfusion:index'))



@login_required
def edit_course(request, course_id):

    try:
        course = Course.objects.get(id=course_id, user=request.user)
    except Course.DoesNotExist:
        messages.warning(request, "This course does not exist.")
        return HttpResponseRedirect(reverse('transfusion:index'))

    assignments = course.assignment_set.order_by('-due_date')
    links = course.link_set.order_by('-id')


    context = {
        'course': course,
        'assignments': assignments,
        'links': links,
    }

    return render(request, 'transfusion/edit_course.html', context)


def edit_course_info(request, course_id):
    try:
        course = Course.objects.get(id=course_id, user=request.user)
    except Course.DoesNotExist:
        messages.warning(request, "This course does not exist.")
        return HttpResponseRedirect(reverse('transfusion:index'))

    if request.method == "POST":
        name = request.POST.get('name')
        short_description = request.POST.get('short_description')
        description = request.POST.get('description')

        course.name = name
        course.short_description = short_description
        course.description = description

        course.save()

        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course_id}))

    else:

        context = {
            'course': course
        }

        return render(request, 'transfusion/edit_course_info.html', context)


def add_assignment(request, course_id):
    try:
        course = Course.objects.get(id=course_id, user=request.user)
    except Course.DoesNotExist:
        messages.warning(request, "This course does not exist.")
        return HttpResponseRedirect(reverse('transfusion:index'))

    if request.method == "POST":
        name = request.POST.get('name')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description')

        new_assignment = Assignment(name=name, due_date=due_date, description=description, course=course)
        try:
            new_assignment.save()
        except ValidationError:
            messages.error(request, "Unable to save assignment. Please try again.")

            context = {
                'course': course
            }
            return render(request, 'transfusion/add_assignment.html', context)

        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course.id}))

    else:
        context = {
            'course': course
        }
        return render(request, 'transfusion/add_assignment.html', context)


def edit_assignment(request, course_id, assignment_id):
    try:
        course = Course.objects.get(id=course_id, user=request.user)
        assignment = Assignment.objects.get(id=assignment_id, course=course)

    except Course.DoesNotExist:
        messages.warning(request, "This course does not exist.")
        return HttpResponseRedirect(reverse('transfusion:index'))

    except Assignment.DoesNotExist:
        messages.warning(request, "This assignment does not exist.")
        return HttpResponseRedirect(reverse('transfusion:index'))

    if request.method == "POST":
        name = request.POST.get('name')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description')

        assignment.name = name
        assignment.due_date = due_date
        assignment.description = description

        try:
            assignment.save()
        except ValidationError:
            messages.error(request, "Unable to save assignment. Please try again.")
            context = {
                'course': course
            }
            return render(request, 'transfusion/add_assignment.html', context)

        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course.id}))

    else:
        context = {
            'course': course,
            'assignment': assignment
        }
        return render(request, 'transfusion/edit_assignment.html', context)


def delete_assignment(request, course_id, assignment_id):
    try:
        assignment = Assignment.objects.get(id=assignment_id, course_id=course_id)
        assignment.delete()
        messages.success(request, "Assignment deleted.")
    except Assignment.DoesNotExist:
        messages.warning(request, "This assignment does not exist.")

    return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course_id}))