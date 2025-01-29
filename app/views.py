from django.shortcuts import render , redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import authenticate,login, logout
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm
from .models import Record, Teacher, QuestionBank
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
import csv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def	home(request):

	return render(request,"index/home.html")


def	frontpage(request):

	return render(request,"frontpage.html")


def front(request):
    records = Record.objects.all().order_by('state')

    # Extract unique states and cities for dropdowns
    states = records.values_list('state', flat=True).distinct()
    cities = records.values_list('city', flat=True).distinct()

    # Apply filters based on GET parameters
    filters = {
        'state': request.GET.get('state', ''),
        'city': request.GET.get('city', ''),
        'school': request.GET.get('school', ''),
        'grade': request.GET.get('grade', '')
    }

    if filters['state']:
        records = records.filter(state__icontains=filters['state'])
    if filters['city']:
        records = records.filter(city__icontains=filters['city'])
    if filters['school']:
        records = records.filter(school_name__icontains=filters['school'])
    if filters['grade']:
        records = records.filter(standard__icontains=filters['grade'])

    # Pagination logic
    paginator = Paginator(records, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Login logic for POST requests
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in!")
            return redirect('frontpage')
        else:
            messages.error(request, "There was an error logging in. Please try again.")
            return redirect('home')

    # Context for rendering the template
    context = {
        'page_obj': page_obj,
        'states': states,
        'cities': cities,
        'filters': filters,  # Pass filters for persistence
    }

    return render(request, 'front.html', context)


def get_suggestions(request):
    query = request.GET.get('term', '')
    filter_type = request.GET.get('type', '')

    if filter_type == 'state':
        suggestions = Record.objects.filter(state__icontains=query).values_list('state', flat=True).distinct()
    elif filter_type == 'school':
        suggestions = Record.objects.filter(school_name__icontains=query).values_list('school_name', flat=True).distinct()
    elif filter_type == 'grade':
        suggestions = Record.objects.filter(standard__icontains=query).values_list('standard', flat=True).distinct()
    elif filter_type == 'city':
        suggestions = Record.objects.filter(city__icontains=query).values_list('city', flat=True).distinct()
    else:
        suggestions = []

    return JsonResponse(list(suggestions), safe=False)


def logout_user(request):
     
	logout(request)
	messages.success(request, "You Have Been Logged Out...")
	return redirect('home')


def register_user(request):
	
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			# Authenticate and login
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, "You Have Successfully Registered! Welcome!")
			return redirect('home')
	else:
		form = SignUpForm()
		return render(request, 'register.html', {'form':form})

	return render(request, 'register.html', {'form':form})


def student_record(request, pk):
	if request.user.is_authenticated:
		# Look Up Records
		student_record = Record.objects.get(id=pk)
		return render(request, 'record.html', {'student_record':student_record})
	else:
		messages.success(request, "You Must Be Logged In To View That Page...")
		return redirect('home')
	

def update_record(request, pk):
	if request.user.is_authenticated:
		current_record = Record.objects.get(id=pk)
		form = AddRecordForm(request.POST or None, instance=current_record)
		if form.is_valid():
			form.save()
			messages.success(request, "Record Has Been Updated!")
			return redirect('home')
		return render(request, 'update_record.html', {'form':form})
	else:
		messages.success(request, "You Must Be Logged In...")
		return redirect('home')
	

def export_csv(request):
    # Fetch filters from the GET request
    state_query = request.GET.get('state', '')
    city_query = request.GET.get('city', '')
    school_query = request.GET.get('school', '')
    grade_query = request.GET.get('grade', '')

    # Filter records based on the provided parameters
    records = Record.objects.all()
    if state_query:
        records = records.filter(state__icontains=state_query)
    if city_query:
        records = records.filter(city__icontains=city_query)
    if school_query:
        records = records.filter(school_name__icontains=school_query)
    if grade_query:
        records = records.filter(standard__icontains=grade_query)

    # Create an HTTP response for the CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="records.csv"'

    # Write the CSV data
    writer = csv.writer(response)
    # Add header row
    writer.writerow(['Student ID', 'First Name', 'Last Name', 'School Name', 'Email', 
                     'Gender', 'Class', 'Section', 'Phone', 'Block', 'City', 'State', 
                     'Funder'])
    
    # Write data rows
    for record in records:
        writer.writerow([
            record.student_id, record.first_name, record.last_name, record.school_name, 
            record.email, record.gender, record.standard, record.section, record.phone, 
            record.block, record.city, record.state, record.funder
        ])

    return response

def get_states(request):
    if request.method == "GET":
        states = Record.objects.values_list('state', flat=True).distinct()
        return JsonResponse(list(states), safe=False)

def get_cities(request):
    if request.method == "GET":
        state = request.GET.get('state', None)
        if state:
            cities = Record.objects.filter(state=state).values_list('city', flat=True).distinct()
        else:
            cities = Record.objects.values_list('city', flat=True).distinct()
        return JsonResponse(list(cities), safe=False)
    

def student_list(request):
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not authenticated

    # Get the teacher's profile
    try:
        teacher_profile = request.user.teacher
        if not teacher_profile.school_name:
            raise Teacher.DoesNotExist

        # Get students from the teacher's school
        students = Record.objects.filter(school_name=teacher_profile.school_name)
        
        return render(request, 'student_list.html', {'students': students})
    
    except Teacher.DoesNotExist:
        # If the teacher profile or school is not found, show a contact admin message
        contact_email = "admin@gmail.com"
        message = f"Plese contact your admin at {contact_email} to assign a school."
        return render(request, 'student_list.html', {'message': message})

def delete_record(request, pk):
	if request.user.is_authenticated:
		delete_it =  get_object_or_404(Record, id=pk)
		delete_it.delete()
		messages.success(request, "Record Deleted Successfully...")
		return redirect('student-list')
	else:
		messages.success(request, "You Must Be Logged In To Do That...")
		return redirect('student-list')	

def add_record(request):
	form = AddRecordForm(request.POST or None)
	if request.user.is_authenticated:
		if request.method == "POST":
			if form.is_valid():
				add_record = form.save()
				messages.success(request, "Record Added...")
				return redirect('front')
		return render(request, 'add_record.html', {'form':form})
	else:
		messages.success(request, "You Must Be Logged In...")
		return redirect('student-list')


def update_record(request, pk):
	if request.user.is_authenticated:
		current_record = Record.objects.get(id=pk)
		form = AddRecordForm(request.POST or None, instance=current_record)
		if form.is_valid():
			form.save()
			messages.success(request, "Record Has Been Updated!")
			return redirect('student-list')
		return render(request, 'update_record.html', {'form':form})
	else:
		messages.success(request, "You Must Be Logged In...")
		return redirect('student-list')

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from .models import FormResponse, Record

def open_form(request, standard, student_id):
    # Get the student object
    student = get_object_or_404(Record, id=student_id)

    # Check if the student has already submitted the form
    already_submitted = FormResponse.objects.filter(student=student, standard=standard).exists()

    if already_submitted:
        return render(request, 'form.html', {'student': student, 'form_submitted': True})

    # Define the questions and options for each standard
    questions_data = {
        6: [
            {'question': 'What is 1 + 10?', 'options': ['1', '2', '3', '4'], 'correct_answer': '2'},
            {'question': 'What is 2 + 2?', 'options': ['2', '3', '4', '5'], 'correct_answer': '4'},
            {'question': 'What is 3 + 3?', 'options': ['5', '6', '7', '8'], 'correct_answer': '6'},
            {'question': 'What is 4 + 4?', 'options': ['7', '8', '9', '10'], 'correct_answer': '8'},
            {'question': 'What is 5 + 5?', 'options': ['9', '10', '11', '12'], 'correct_answer': '10'},
        ],
        7: [
            {'question': 'What is 2 * 2?', 'options': ['2', '3', '4', '5'], 'correct_answer': '4'},
            {'question': 'What is 3 * 3?', 'options': ['6', '7', '8', '9'], 'correct_answer': '9'},
            {'question': 'What is 4 * 4?', 'options': ['12', '13', '14', '16'], 'correct_answer': '16'},
            {'question': 'What is 5 * 5?', 'options': ['24', '25', '26', '27'], 'correct_answer': '25'},
            {'question': 'What is 6 * 6?', 'options': ['30', '32', '34', '36'], 'correct_answer': '36'},
        ],
    }

    # Get the questions for the requested standard
    questions = questions_data.get(standard, [])

    return render(request, 'form.html', {'student': student, 'questions': questions, 'form_submitted': False})

def submit_form(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(Record, id=student_id)
        standard = student.standard

        # Check if the form was already submitted
        if FormResponse.objects.filter(student=student, standard=standard).exists():
            return JsonResponse({'error': 'Form already submitted'}, status=400)

        correct_count = 0
        responses = {}

        # Define the questions and correct answers (same as in open_form view)
        questions_data = {
            6: [
                {'question': 'What is 1 + 10?', 'options': ['1', '2', '3', '4'], 'correct_answer': '2'},
                {'question': 'What is 2 + 2?', 'options': ['2', '3', '4', '5'], 'correct_answer': '4'},
                {'question': 'What is 3 + 3?', 'options': ['5', '6', '7', '8'], 'correct_answer': '6'},
                {'question': 'What is 4 + 4?', 'options': ['7', '8', '9', '10'], 'correct_answer': '8'},
                {'question': 'What is 5 + 5?', 'options': ['9', '10', '11', '12'], 'correct_answer': '10'},
            ],
            7: [
                {'question': 'What is 2 * 2?', 'options': ['2', '3', '4', '5'], 'correct_answer': '4'},
                {'question': 'What is 3 * 3?', 'options': ['6', '7', '8', '9'], 'correct_answer': '9'},
                {'question': 'What is 4 * 4?', 'options': ['12', '13', '14', '16'], 'correct_answer': '16'},
                {'question': 'What is 5 * 5?', 'options': ['24', '25', '26', '27'], 'correct_answer': '25'},
                {'question': 'What is 6 * 6?', 'options': ['30', '32', '34', '36'], 'correct_answer': '36'},
            ],
        }

        # Get the questions for the requested standard
        questions = questions_data.get(standard, [])

        # Process the form responses
        for question in questions:
            answer = request.POST.get(f'question_{question["question"]}')
            responses[question["question"]] = answer
            if answer == question['correct_answer']:
                correct_count += 1

        # Save the responses to the FormResponse model
        FormResponse.objects.create(
            student=student,
            standard=standard,
            responses=responses,
            submitted_at=timezone.now(),
        )

        print("Form submitted Successfully")
        return redirect('student-list')
    
      
    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.db.models import Count

def dashboardd(request):
    # Get all filter values from the request
    selected_funder = request.GET.get('funder', '')
    selected_district = request.GET.get('district', '')
    selected_school = request.GET.get('school', '')
    selected_status = request.GET.get('assessment_status', '')  # New filter

    # Query for the main data
    students = Record.objects.all()
    if selected_funder:
        students = students.filter(funder=selected_funder)
    if selected_district:
        students = students.filter(city=selected_district)
    if selected_school:
        students = students.filter(school_name=selected_school)

    # Filter by assessment status
    if selected_status == "filled":
        students = students.filter(formresponse__isnull=False)
    elif selected_status == "not_filled":
        students = students.filter(formresponse__isnull=True)

    # Generate data for charts (example)
    funder_data = students.values('funder').annotate(total=Count('id')).order_by('-total')
    district_data = students.values('city').annotate(total=Count('id')).order_by('-total')
    grade_data = students.values('standard').annotate(total=Count('id')).order_by('standard')

    # Prepare charts for Plotly
    funder_chart = {
        "data": [{
            "x": [entry['funder'] for entry in funder_data],
            "y": [entry['total'] for entry in funder_data],
            "type": "bar",
        }],
        "layout": {"title": "Assessments by Funder"}
    }
    district_chart = {
        "data": [{
            "x": [entry['city'] for entry in district_data],
            "y": [entry['total'] for entry in district_data],
            "type": "bar",
        }],
        "layout": {"title": "Assessments by District"}
    }
    grade_chart = {
        "data": [{
            "x": [entry['standard'] for entry in grade_data],
            "y": [entry['total'] for entry in grade_data],
            "type": "bar",
        }],
        "layout": {"title": "Assessments by Grade"}
    }

    # Pass data to the template
    context = {
        "funders": Record.objects.values_list('funder', flat=True).distinct(),
        "districts": Record.objects.values_list('city', flat=True).distinct(),
        "schools": Record.objects.values_list('school_name', flat=True).distinct(),
        "selected_funder": selected_funder,
        "selected_district": selected_district,
        "selected_school": selected_school,
        "selected_status": selected_status,
        "funder_chart": funder_chart,
        "district_chart": district_chart,
        "grade_chart": grade_chart,
        "school_assessed": students.values('school_name').distinct().count(),
        "students_assessed": students.count(),
        "total_schools": Record.objects.values('school_name').distinct().count(),
        "total_students": Record.objects.count(),
    }
    return render(request, "dashboardd.html", context)
