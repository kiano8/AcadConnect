from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Course, Assessment, GradeSnapshot
from .forms import CourseForm, AssessmentForm
from apps.notifications.models import Notification


@login_required
def grade_dashboard(request):
    courses = Course.objects.filter(user=request.user).prefetch_related('assessments')

    # Calculate overall GPA
    total_points = 0
    total_credits = 0
    for course in courses:
        gp = course.grade_points
        if gp is not None:
            total_points += gp * course.credit_hours
            total_credits += course.credit_hours
    current_gpa = round(total_points / total_credits, 2) if total_credits > 0 else None

    # Risk alerts
    threshold = request.user.gpa_threshold
    at_risk_courses = []
    for course in courses:
        grade = course.computed_grade
        if grade is not None and grade < 70:
            at_risk_courses.append(course)
            Notification.objects.get_or_create(
                user=request.user,
                message=f"⚠️ Risk Alert: Your grade in {course.name} is {grade:.1f}%.",
                notification_type='grade',
            )

    # Grade snapshots for charts
    chart_data = {}
    for course in courses:
        snapshots = GradeSnapshot.objects.filter(course=course).order_by('timestamp')
        chart_data[course.name] = {
            'labels': [s.timestamp.strftime('%b %d') for s in snapshots],
            'data': [s.computed_grade for s in snapshots],
        }

    context = {
        'courses': courses,
        'current_gpa': current_gpa,
        'at_risk_courses': at_risk_courses,
        'chart_data': chart_data,
        'gpa_threshold': threshold,
    }
    return render(request, 'grades/dashboard.html', context)


@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            course.save()
            messages.success(request, f"Course '{course.name}' added!")
            return redirect('grades:dashboard')
    else:
        form = CourseForm()
    return render(request, 'grades/course_form.html', {'form': form, 'action': 'Add'})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, user=request.user)
    assessments = course.assessments.order_by('-date')
    return render(request, 'grades/course_detail.html', {'course': course, 'assessments': assessments})


@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk, user=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect('grades:dashboard')
    return render(request, 'grades/course_confirm_delete.html', {'course': course})


@login_required
def assessment_add(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, user=request.user)
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.course = course
            assessment.save()
            # Save grade snapshot
            grade = course.computed_grade
            if grade is not None:
                GradeSnapshot.objects.create(course=course, computed_grade=grade)
            messages.success(request, f"Assessment '{assessment.name}' added!")
            return redirect('grades:course_detail', pk=course.pk)
    else:
        form = AssessmentForm()
    return render(request, 'grades/assessment_form.html', {'form': form, 'course': course})


@login_required
def assessment_edit(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, course__user=request.user)
    course = assessment.course
    if request.method == 'POST':
        form = AssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            grade = course.computed_grade
            if grade is not None:
                GradeSnapshot.objects.create(course=course, computed_grade=grade)
            messages.success(request, f"Assessment '{assessment.name}' updated!")
            return redirect('grades:course_detail', pk=course.pk)
    else:
        form = AssessmentForm(instance=assessment)
    return render(request, 'grades/assessment_form.html', {
        'form': form,
        'course': course,
        'assessment': assessment,
        'editing': True,
    })


@login_required
def assessment_delete(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk, course__user=request.user)
    course = assessment.course
    if request.method == 'POST':
        assessment.delete()
        messages.success(request, "Assessment deleted.")
        return redirect('grades:course_detail', pk=course.pk)
    return render(request, 'grades/assessment_confirm_delete.html', {'assessment': assessment})
