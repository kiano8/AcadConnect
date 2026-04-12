from django.db import models
from django.conf import settings


class Course(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    credit_hours = models.FloatField(default=3.0)
    professor = models.CharField(max_length=100, blank=True)
    semester = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=7, default='#2A9D8F')

    def __str__(self):
        return f"{self.code} - {self.name}" if self.code else self.name

    @property
    def computed_grade(self):
        assessments = self.assessments.all()
        if not assessments:
            return None
        weighted_sum = sum(
            (a.score / a.max_score) * a.weight for a in assessments if a.max_score > 0
        )
        total_weight = sum(a.weight for a in assessments)
        if total_weight == 0:
            return None
        return (weighted_sum / total_weight) * 100

    @property
    def letter_grade(self):
        grade = self.computed_grade
        if grade is None:
            return 'N/A'
        if grade >= 97: return 'A+'
        if grade >= 93: return 'A'
        if grade >= 90: return 'A-'
        if grade >= 87: return 'B+'
        if grade >= 83: return 'B'
        if grade >= 80: return 'B-'
        if grade >= 77: return 'C+'
        if grade >= 73: return 'C'
        if grade >= 70: return 'C-'
        if grade >= 67: return 'D+'
        if grade >= 60: return 'D'
        return 'F'

    @property
    def grade_points(self):
        lg = self.letter_grade
        mapping = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'F': 0.0, 'N/A': None
        }
        return mapping.get(lg)


class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('exam', 'Exam'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
        ('lab', 'Lab'),
        ('participation', 'Participation'),
        ('other', 'Other'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    name = models.CharField(max_length=100)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES, default='assignment')
    score = models.FloatField()
    max_score = models.FloatField(default=100)
    weight = models.FloatField(default=1.0, help_text="Relative weight in final grade calculation")
    date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.course.name})"

    @property
    def percentage(self):
        if self.max_score == 0:
            return 0
        return (self.score / self.max_score) * 100


class GradeSnapshot(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='snapshots')
    computed_grade = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
