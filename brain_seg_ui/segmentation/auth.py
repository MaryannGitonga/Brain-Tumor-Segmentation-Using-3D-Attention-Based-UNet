from flask import (
    Blueprint, 
    render_template, 
    flash,
    request, 
    redirect,  
    url_for
)
from .forms import SignupForm, LoginForm
from .enums import Roles
from flask_login import (
    current_user,
    login_user
)

from .models import db, User
from . import login_manager

from .utils import util_create_user

auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(medical_id = form.medical_id.data).first()
        # if user.role != Roles.neurologist.value or user.role != Roles.sonographer.value:
        #     return redirect(url_for('auth_bp.login'))
                
        if user and user.check_password(password = form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for('main_bp.upload_scans'))
        
        flash('Invalid medical ID or password.')
        return redirect(url_for('auth_bp.login'))
    
    return render_template(
        'login.html',
        form = form,
        title = 'Log In.',
        template = 'login-page',
    )

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(medical_id = form.medical_id.data).first()
        
        if existing_user is None:
            user = util_create_user(form)
            if user:
                print('User: ', user.medical_id)
                login_user(user)
                return redirect(url_for('main_bp.home'))
    
    return render_template(
        'signup.html',
        title = 'Create an Account',
        form = form,
        template = 'signup-page',
    )
    
    
@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in upon page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash("You must be logged in to view that page.")
    return redirect(url_for("auth_bp.login"))
    
    
    