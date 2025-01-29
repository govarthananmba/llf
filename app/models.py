from django.db import models

from django.contrib.auth.models import User

class Record(models.Model):
	student_id = models.CharField(max_length=50,unique=True)
	first_name = models.CharField(max_length=50)
	last_name =  models.CharField(max_length=50)
	school_name =  models.CharField(max_length=100)
	email =  models.CharField(max_length=100)
	gender=models.CharField(max_length=10)
	standard=models.IntegerField()
	section=models.CharField(max_length=10)
	phone = models.CharField(max_length=15)
	block =  models.CharField(max_length=100)
	city =  models.CharField(max_length=50)
	state =  models.CharField(max_length=50)
	funder =models.CharField(max_length=50)
	

	def __str__(self):
		
		return(f"{self.student_id} {self.first_name} {self.last_name} {self.school_name}")


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=100)
 

    def __str__(self):
        return f"{self.user.username} - {self.school_name}"
    

class FormResponse(models.Model):
    student = models.ForeignKey(Record, on_delete=models.CASCADE)
    standard = models.IntegerField()
    responses = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    assessment_status = models.CharField(max_length=50, default="Not Assessed")  # Add this field

    
class QuestionBank(models.Model):
    standard = models.IntegerField()
    question_text = models.TextField()
    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    option_3 = models.CharField(max_length=255)
    option_4 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Standard {self.standard}: {self.question_text[:50]}..."
