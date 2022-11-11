import random
from flask import Blueprint, redirect, render_template, url_for, flash
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
    
        flair_scan = form.flair_scan.data
        flair_scan_path = './scans/' + secure_filename(flair_scan.filename)
        flair_scan.save(flair_scan_path)
        
        t1ce_scan = form.t1ce_scan.data
        t1ce_scan_path = './scans/' + secure_filename(t1ce_scan.filename)
        t1ce_scan.save(t1ce_scan_path)
        
        t2_scan = form.t2_scan.data
        t2_scan_path = './scans/' + secure_filename(t2_scan.filename)
        t2_scan.save(t2_scan_path)
        
        temp_image_flair = nib.load(flair_scan_path).get_fdata()
        temp_image_flair = scaler.fit_transform(temp_image_flair.reshape(-1, temp_image_flair.shape[-1])).reshape(temp_image_flair.shape)

        temp_image_t1ce = nib.load(t1ce_scan_path).get_fdata()
        temp_image_t1ce = scaler.fit_transform(temp_image_t1ce.reshape(-1, temp_image_t1ce.shape[-1])).reshape(temp_image_t1ce.shape)

        temp_image_t2 = nib.load(t2_scan_path).get_fdata()
        temp_image_t2 = scaler.fit_transform(temp_image_t2.reshape(-1, temp_image_t2.shape[-1])).reshape(temp_image_t2.shape)

        temp_combined_images = np.stack([temp_image_flair, temp_image_t1ce, temp_image_t2], axis = 3)
        test_scan = temp_combined_images[56:184, 56:184, 13:141]    
        
        test_scan_input = np.expand_dims(test_scan, axis = 0)
        
        config = tf.ConfigProto()
        
        with tf.Session(config = config) as sess:
            with sess.as_default:
                my_model = tf.keras.models.load_model('attention_unet_85', compile=False)
                print(my_model.summary())
                test_prediction = my_model.predict(test_scan_input)
                test_prediction_argmax = np.argmax(test_prediction, axis = 4)[0, :, :, :]    
                
                n_slice = 55
                rand_num = str(random.randint(100, 999))
                file_path = rand_num + '.png'
                
                plt.figure(figsize=(8,8))
                plt.plot(231)
                plt.imshow(test_scan[:, :, n_slice, 1], cmap='gray')
                plt.title('Testing Scan')
                plt.savefig('./scans/' + file_path)
                
                combined_scan = Scan(
                    scan_file = 'scans/' + file_path,
                    scan_type = ScanTypes.combined
                )
                
                db.session.add(combined_scan)
                db.session.commit()
                
                plt.clf()
                plt.figure(figsize=(8,8))
                plt.plot(231)
                plt.imshow(test_prediction_argmax[:, :, n_slice])
                plt.title('Prediction on test image')
                plt.savefig('./predicted/' + file_path)
                
                predicted_scan = Scan(
                    scan_file = 'predicted/' + file_path,
                    scan_type = ScanTypes.predicted
                )
                
                db.session.add(predicted_scan)
                db.session.commit()
                
                
        return redirect(url_for('main_bp.upload_scans'))
    
    return render_template(
        "upload_scans.html",
        title="Upload Scans",
        form = form,
        template = 'signup-page',
    )

@main_bp.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for("auth_bp.login"))