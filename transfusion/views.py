import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.db.utils import IntegrityError
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.encoding import smart_str
from transfusion.models import Course, Assignment, Link, TeacherProfile, File
from transfusion_v2.settings import BASE_DIR, MEDIA_ROOT


def index(request):
    if not request.user.is_authenticated():
        return render(request, 'transfusion/index.html')
    else:
        return render(request, 'transfusion/logged_in_index.html')


def search(request):

    term = request.GET.get('term')

    if not term == "":
        results = User.objects.filter(Q(username__icontains=term) | Q(last_name__icontains=term))
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
    files = t_course.file_set.order_by('-id')

    context = {
        'user': user,
        'course': t_course,
        'assignments': assignments,
        'links': links,
        'files': files
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
        messages.error(request, "Account not found, perhaps you entered your password incorrectly?")
        
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
    files = course.file_set.order_by('-id')


    context = {
        'course': course,
        'assignments': assignments,
        'links': links,
        'files': files
    }

    return render(request, 'transfusion/edit_course.html', context)


@login_required
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

        messages.success(request, "Course changed.")

        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course_id}))

    else:

        context = {
            'course': course
        }

        return render(request, 'transfusion/edit_course_info.html', context)


@login_required
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

        messages.success(request, "Assignment added.")

        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course.id}))

    else:
        context = {
            'course': course
        }
        return render(request, 'transfusion/add_assignment.html', context)


@login_required
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

        messages.success(request, "Assignment changed.")

        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course.id}))

    else:
        context = {
            'course': course,
            'assignment': assignment
        }
        return render(request, 'transfusion/edit_assignment.html', context)


@login_required
def delete_assignment(request, course_id, assignment_id):
    try:
        assignment = Assignment.objects.get(id=assignment_id, course_id=course_id)
        assignment.delete()
        messages.success(request, "Assignment deleted.")
    except Assignment.DoesNotExist:
        messages.warning(request, "This assignment does not exist.")

    return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course_id}))


@login_required
def add_link(request, course_id):
    try:
        course = Course.objects.get(id=course_id, user=request.user)
    except Course.DoesNotExist:
        messages.warning(request, "This course does not exist.")
        return HttpResponseRedirect(reverse('transfusion:index'))

    if request.method == "POST":
        name = request.POST.get('name')
        address = request.POST.get('address')
        description = request.POST.get('description')

        new_link = Link(name=name, address=address, description=description, course=course)
        try:
            new_link.save()
        except ValidationError:
            messages.error(request, "Unable to save link. Please try again.")

            context = {
                'course': course
            }
            return render(request, 'transfusion/add_link.html', context)

        messages.success(request, "Link added.")

        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course.id}))

    else:
        context = {
            'course': course
        }
        return render(request, 'transfusion/add_link.html', context)


@login_required
def edit_link(request, course_id, link_id):
    try:
        course = Course.objects.get(id=course_id, user=request.user)
        link = Link.objects.get(id=link_id, course=course)

    except Course.DoesNotExist:
        messages.warning(request, "This course does not exist.")
        return HttpResponseRedirect(reverse('transfusion:index'))

    except Link.DoesNotExist:
        messages.warning(request, "This link does not exist.")
        return HttpResponseRedirect(reverse('transfusion:index'))

    if request.method == "POST":
        name = request.POST.get('name')
        address = request.POST.get('address')
        description = request.POST.get('description')

        link.name = name
        link.address = address
        link.description = description

        try:
            link.save()
        except ValidationError:
            messages.error(request, "Unable to save link. Please try again.")
            context = {
                'course': course
            }
            return render(request, 'transfusion/add_link.html', context)

        messages.success(request, "Link changed.")

        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course.id}))

    else:
        context = {
            'course': course,
            'link': link,
        }
        return render(request, 'transfusion/edit_link.html', context)


@login_required
def delete_link(request, course_id, link_id):
    try:
        link = Link.objects.get(id=link_id, course_id=course_id)
        link.delete()
        messages.success(request, "Link deleted.")
    except Link.DoesNotExist:
        messages.warning(request, "This link does not exist.")

    return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course_id}))


@login_required
def delete_file(request, course_id, file_id):
    try:
        file = File.objects.get(id=file_id, course_id=course_id)
        os.remove(os.path.join(file.path, file.filename))
        file.delete()
        messages.success(request, "File deleted.")
    except Link.DoesNotExist:
        messages.warning(request, "This file does not exist.")

    return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course_id}))


@login_required
def add_course(request):

    if request.method == "POST":
        name = request.POST.get("name")
        short_description = request.POST.get("short_description")
        description = request.POST.get('description')

        course = Course(name=name, short_description=short_description, description=description, user=request.user)

        try:
            course.save()
        except ValueError:
            messages.warning(request, "Unable to save course. Please try again.")
            return HttpResponseRedirect(reverse("transfusion:add_course"))

        messages.success(request, "Course created.")
        return HttpResponseRedirect(reverse("transfusion:edit_course", kwargs={'course_id': course.id}))

    else:
        return render(request, 'transfusion/add_course.html')


@login_required
def preferences(request):

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get("last_name")
        email = request.POST.get('email_address')

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email

        try:
            request.user.save()
        except ValueError:
            messages.warning(request, "Unable to save user preferences.")
            return render(request, "transfusion/preferences.html")

        messages.success(request, "Preferences updated.")
        return HttpResponseRedirect(reverse("transfusion:index"))

    else:
        return render(request, "transfusion/preferences.html")


@login_required
def change_password(request):

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        new_password_repeat = request.POST.get("new_password_repeat")

        if new_password != new_password_repeat:
            messages.warning(request, "Your passwords do not match. Please try again.")
            return render(request, 'transfusion/change_password.html')

        if request.user.check_password(current_password):
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, "Password changed. You may have to login again.")
            return HttpResponseRedirect(reverse('transfusion:preferences'))
        else:
            messages.warning(request, "Your old password was entered incorrectly. Please try again.")
            return render(request, 'transfusion/change_password.html')

    else:
        return render(request, 'transfusion/change_password.html')


@login_required
def delete_things(request):
    password = request.POST.get('password')
    course_id = request.POST.get('course_id')

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        messages.warning(request, "Course does not exist.")
        return HttpResponseRedirect(reverse("transfusion:index"))

    if 'assignments' in request.POST:
        try:
            assignments = Assignment.objects.filter(course=course)
            assignments.delete()
        except Assignment.DoesNotExist:
            pass

        messages.success(request, "All assignments deleted.")
        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course_id}))

    elif 'links' in request.POST:
        try:
            links = Link.objects.filter(course=course)
            links.delete()
        except Link.DoesNotExist:
            pass

        messages.success(request, "All links deleted.")
        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course_id}))

    elif 'course' in request.POST:
        # delete files before deleting everything else
        try:
            files = File.objects.filter(course=course)
            for file in files:
                print(os.path.join(file.path, file.filename))
                try:
                    os.remove(os.path.join(file.path, file.filename))
                except FileNotFoundError:
                    print('file not found')

            files.delete()
        except File.DoesNotExist:
            pass

        course.delete()
        messages.success(request, "Course deleted.")

    elif 'files' in request.POST:
        try:
            files = File.objects.filter(course=course)
            for file in files:
                print(os.path.join(file.path, file.filename))
                try:
                    os.remove(os.path.join(file.path, file.filename))
                except FileNotFoundError:
                    print('file not found')

            files.delete()
        except File.DoesNotExist:
            pass

        messages.success(request, "All files deleted.")
        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course_id}))

    return HttpResponseRedirect(reverse('transfusion:index'))


@login_required
def add_file(request, course_id):

    try:
        course = Course.objects.get(id=course_id, user=request.user)

    except Course.DoesNotExist:
        messages.warning(request, "This course does not exist.")
        return HttpResponseRedirect(reverse('transfusion:index'))

    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        file = request.FILES.get('file')

        folder = request.user.username + '/' + str(course.id)
        full_path = os.path.join(MEDIA_ROOT, folder)

        try:
            os.makedirs(full_path)
        except:
            pass

        new_dest = os.path.join(full_path, file.name)

        if os.path.isfile(new_dest):
            messages.error(request,
                           "This file already exists on the server. Please delete the old file, or rename the new one.")
            context = {
                'course': course,
                'autofill_name': name,
                'autofill_description': description
            }
            return render(request, 'transfusion/add_file.html', context)

        with open(new_dest, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        file = File(name=name, description=description, filename=file.name, path=full_path, course=course)

        file.save()

        messages.success(request, "File added.")

        return HttpResponseRedirect(reverse('transfusion:edit_course', kwargs={'course_id': course.id}))

    else:

        context = {
            'course': course,
        }
        return render(request, 'transfusion/add_file.html', context)


def download_file(request, file_id):

    try:
        file = File.objects.get(id=file_id)
    except File.DoesNotExist:
        messages.error(request, "File does not exist.")
        return HttpResponseRedirect(reverse('transfusion:index'))

    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file.filename)
    response['X-Sendfile'] = smart_str(os.path.join(file.path, file.filename))
    # It's usually a good idea to set the 'Content-Length' header too.
    # You can also set any other required headers: Cache-Control, etc.
    return response


def create_account(request):

    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_repeat = request.POST.get('retype_password')
        school = request.POST.get('school')

        if password != password_repeat:
            messages.error(request, "Your passwords do not match. Please try again.")
            return HttpResponseRedirect(reverse('transfusion:create_account'))

        try:
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
            profile = TeacherProfile(school=school, user=user)
            profile.save()
        except IntegrityError:
            messages.error(request, "That username is taken, please try another.")
            return HttpResponseRedirect(reverse('transfusion:create_account'))

        messages.success(request, "Account created. You may now log in.")
        return HttpResponseRedirect(reverse('transfusion:index'))

    return render(request, "transfusion/create_account.html")