from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required, logout_user
from .enums import Roles
from .forms import UploadScansForm
from .models import db, User
from .utils import *

# Blueprint Configuration
main_bp = Blueprint(
    "main_bp", __name__, template_folder="templates", static_folder="static"
)


@main_bp.route("/", methods=["GET"])
@login_required
def home():
    return render_template(
        "home.html",
        title="Home - Brain Tumor Segmentation",
        template="home-template",
        current_user=current_user,
        neur = Roles.neurologist,
    )
    
    
@main_bp.route('/seed_patients', methods=['GET'])
@login_required
def seed_patients():
    util_seed_patients()
    return redirect(url_for('main_bp.home'))

    

@main_bp.route('/upload_scans', methods=['GET', 'POST'])
@login_required
def upload_scans():
    form = UploadScansForm()
    
    if form.validate_on_submit():
        success = util_upload_and_segment(form)               
        
        if success:           
            return redirect(url_for('main_bp.upload_scans'))
    
    return render_template(
        "upload_scans.html",
        title="Upload Scans",
        form = form,
        template = 'signup-page',
        neur = Roles.neurologist,
    )

@main_bp.route('/view_patients', methods=['GET'])
@login_required
def view_patients():
    patients = db.session.query(User).filter(User.role == None)
        
    return render_template(
        'patients.html',
        template = 'dashboard-page',
        patients = patients,
        body = 'View Patients',
        neur = Roles.neurologist,

    )

@main_bp.route('/view_scans/<patient_ID>', methods=['GET'])
@login_required
def view_scans(patient_ID):
    response = util_get_scans(patient_ID)
    
    if response['status'] == 200: 
        scans_list = response['scans']
        patient = response['patient']           
        return render_template('scans.html',
                            scans = scans_list,
                            template = 'dashboard-page',
                            body = 'Scans for: ' + ' ' +  str(patient.medical_id) + ' - ' + patient.first_name + ' ' + patient.last_name,
                            neur = Roles.neurologist,
                            )
    return redirect('main_bp.view_patients')

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth_bp.login"))