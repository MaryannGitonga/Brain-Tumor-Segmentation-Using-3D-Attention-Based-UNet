import os
import random
from flask import Blueprint, redirect, render_template, url_for, request
from flask_login import current_user, login_required, logout_user
from .enums import Roles, ScanTypes
from .forms import UploadScansForm
from sklearn.preprocessing import MinMaxScaler
from werkzeug.utils import secure_filename
import numpy as np
import nibabel as nib
import tensorflow as tf
import matplotlib.pyplot as plt
from .models import db, User, Scan
from os.path import join, dirname, realpath

SCANS_PATH = join(dirname(realpath(__file__)), 'static/scans/')
PREDICTED_PATH = join(dirname(realpath(__file__)), 'static/predicted/')
MODEL_PATH = join(dirname(realpath(__file__)), './trial_4attention_unet_3d')

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
    patients = list()
    user_1 = User(
                medical_id = 100,
                first_name = 'Jane',
                last_name = 'Doe',
                email = 'jane.doe@gmail.com',
                password = '12345678'
            )
    patients.append(user_1)
    
    user_2 = User(
                medical_id = 200,
                first_name = 'John',
                last_name = 'Doe',
                email = 'john.doe@gmail.com',
                password = '12345678'
            )
    patients.append(user_2)
    
    user_3 = User(
                medical_id = 300,
                first_name = 'Jeanne',
                last_name = 'Eliah',
                email = 'jeanne.eliah@gmail.com',
                password = '12345678'
            )
    patients.append(user_3)
    
    for user in patients:
        user.set_password(user.password)
        db.session.add(user)
        db.session.commit()
        
    return redirect(url_for('main_bp.home'))
    

@main_bp.route('/upload_scans', methods=['GET', 'POST'])
@login_required
def upload_scans():
    form = UploadScansForm()
    
    if form.validate_on_submit():
        scaler = MinMaxScaler()
    
        flair_scan = request.files['flair_scan']
        flair_scan_path = secure_filename(flair_scan.filename)
        flair_scan.save(os.path.join(SCANS_PATH, flair_scan_path))
        
        t1ce_scan = request.files['t1ce_scan']
        t1ce_scan_path = secure_filename(t1ce_scan.filename)
        t1ce_scan.save(os.path.join(SCANS_PATH, t1ce_scan_path))
        
        t2_scan = request.files['t2_scan']
        t2_scan_path = secure_filename(t2_scan.filename)
        t2_scan.save(os.path.join(SCANS_PATH, t2_scan_path))
        
        temp_image_flair = nib.load(os.path.join(SCANS_PATH,flair_scan_path)).get_fdata()
        temp_image_flair = scaler.fit_transform(temp_image_flair.reshape(-1, temp_image_flair.shape[-1])).reshape(temp_image_flair.shape)

        temp_image_t1ce = nib.load(os.path.join(SCANS_PATH,t1ce_scan_path)).get_fdata()
        temp_image_t1ce = scaler.fit_transform(temp_image_t1ce.reshape(-1, temp_image_t1ce.shape[-1])).reshape(temp_image_t1ce.shape)

        temp_image_t2 = nib.load(os.path.join(SCANS_PATH,t2_scan_path)).get_fdata()
        temp_image_t2 = scaler.fit_transform(temp_image_t2.reshape(-1, temp_image_t2.shape[-1])).reshape(temp_image_t2.shape)

        temp_combined_images = np.stack([temp_image_flair, temp_image_t1ce, temp_image_t2], axis = 3)
        test_scan = temp_combined_images[56:184, 56:184, 13:141]    
        
        test_scan_input = np.expand_dims(test_scan, axis = 0)
        
        # config = tf.compat.v1.ConfigProto()
        
        # tf.compat.v1.disable_eager_execution()
        # with tf.compat.v1.Session(config = config) as sess:
        #     with sess.as_default:
        
        my_model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        
        test_prediction = my_model.predict(test_scan_input)
        test_prediction_argmax = np.argmax(test_prediction, axis = 4)[0, :, :, :]    
        
        n_slice = 40
        rand_num = str(random.randint(100, 999))
        file_path = rand_num + '.png'
        
        plt.figure(figsize=(8,8))
        plt.plot(231)
        plt.imshow(test_scan[:, :, n_slice, 1], cmap='gray')
        plt.title('Testing Scan')
        plt.savefig(os.path.join(SCANS_PATH, file_path))
        
        combined_scan = Scan(
            scan_file = 'scans/' + file_path,
            scan_type = ScanTypes.combined,
            patient_id = form.patient.data
        )
        
        db.session.add(combined_scan)
        db.session.commit()
        
        print('Classes in prediction************ ', np.unique(test_prediction))
        print('Classes in argmax************ ', np.unique(test_prediction_argmax))
        plt.clf()
        plt.figure(figsize=(8,8))
        plt.plot(231)
        plt.imshow(test_prediction_argmax[:, :, n_slice])
        plt.title('Prediction on test image')
        plt.savefig(os.path.join(PREDICTED_PATH, file_path))
        
        predicted_scan = Scan(
            scan_file = 'predicted/' + file_path,
            scan_type = ScanTypes.predicted,
            patient_id = form.patient.data
        )
        
        db.session.add(predicted_scan)
        db.session.commit()
                
                
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
    scans_list = list()
    print("Patient ID: ", patient_ID)
    scans = db.session.query(Scan).filter_by(patient_id = patient_ID)
    
    patient = db.session.query(User).filter_by(id = patient_ID).first()
    
    if scans.count() > 0:
        for i in range(scans.count() - 1):
            scans_list.append({
                'scan': scans[i].scan_file,
                'predicted': scans[i + 1].scan_file,
                'created_on' : scans[i].created_on.date()
            })
            
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
    """User log-out logic."""
    logout_user()
    return redirect(url_for("auth_bp.login"))