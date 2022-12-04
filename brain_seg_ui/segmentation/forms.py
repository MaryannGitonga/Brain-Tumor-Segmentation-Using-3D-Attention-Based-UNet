from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SelectField, FileField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional
)

from .models import db, User

class SignupForm(FlaskForm):
    
    medical_id = IntegerField(
        'Medical ID',
        validators = [DataRequired()]
    )
    
    first_name = StringField(
        'First Name',
        validators = [DataRequired()]
    )
    
    last_name = StringField(
        'Last Name',
        validators = [DataRequired()]
    )
    
    email = StringField(
        'Email',
        validators=[
            Length(min=6),
            Email(message='Enter a valid email.'),
            DataRequired()
        ]
    )
    
    phone_no = StringField(
        'Phone Number',
    )
    
    role = SelectField(
        'Role',
        validators=[ DataRequired()],
        choices=[('neurologist', 'neurologist'), ('sonographer', 'sonographer')]
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, message='Select a stronger password')
        ]
    )
    
    confirm = PasswordField(
        'Confirm your Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )
    
    submit = SubmitField('Register')
    
    
class LoginForm(FlaskForm):
    
    medical_id = IntegerField(
        'Medical ID',
        validators = [DataRequired()]
    )
   
    password = PasswordField(
       'Password', 
       validators=[DataRequired()]
    )
    
    submit = SubmitField('Log In')

class UploadScansForm(FlaskForm):
    def getPatients():
        patients_list = list()
        patients = db.session.query(User).filter(User.role == None)
        
        for patient in patients:
            patients_list.append((
                patient.id, 
                str(patient.medical_id) + ' - ' + patient.first_name + ' ' + patient.last_name
                ))
            
        return patients_list
    
    patient = SelectField(
        'Patient',
        validators=[DataRequired()],
        choices=getPatients()
    )
    
    flair_scan = FileField(
        'Flair Scan',
        validators=[DataRequired()]
    )
    
    t1ce_scan = FileField(
        'T1CE Scan',
        validators=[DataRequired()]
    )
    
    t2_scan = FileField(
        'T2 Scan',
        validators=[DataRequired()]
    )
    
    submit = SubmitField('Segment Tumor')
    