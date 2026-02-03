from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
from functools import wraps
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration - Use environment variables in production
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here_change_in_production')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
app.config['ENV'] = os.getenv('FLASK_ENV', 'development')

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'gif'}

# Create uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Portfolio data - Kola Ajay's Projects
PORTFOLIO_ITEMS = [
    {
        'id': 1,
        'title': 'Diamond Price Prediction',
        'description': 'Machine Learning regression model to predict diamond prices with high accuracy. Engineered feature engineering on large datasets and deployed visualizations using Matplotlib/Seaborn to present key price drivers to stakeholders.',
        'image': 'project1.jpg',
        'technologies': ['Python', 'Scikit-learn', 'Pandas', 'Matplotlib', 'Machine Learning'],
        'keyFeatures': [
            'Regression model for price prediction',
            'Extensive data preprocessing and feature engineering',
            'Data visualization using Matplotlib/Seaborn',
            'Optimization to reduce overfitting'
        ]
    },
    {
        'id': 2,
        'title': 'E-Commerce Management System',
        'description': 'Full-stack web application for managing products, customers, and orders. Designed and implemented a normalized SQL database schema with secure user authentication and dynamic shopping cart system.',
        'image': 'project2.jpg',
        'technologies': ['HTML5', 'CSS3', 'JavaScript', 'SQL', 'Web Development'],
        'keyFeatures': [
            'Scalable product and inventory management',
            'Normalized SQL database schema',
            'Secure user authentication',
            'Dynamic shopping cart system',
            'Responsive frontend design'
        ]
    },
    {
        'id': 3,
        'title': 'Data Science Portfolio',
        'description': 'Comprehensive data science projects demonstrating expertise in Python, data preprocessing, and predictive modeling with strong focus on machine learning algorithms and statistical analysis.',
        'image': 'project3.jpg',
        'technologies': ['Python', 'Data Science', 'NumPy', 'Pandas', 'Scikit-learn'],
        'keyFeatures': [
            'Data preprocessing and cleaning',
            'Feature engineering and selection',
            'Predictive model development',
            'Data analysis and visualization',
            'Algorithm optimization'
        ]
    }
]

SKILLS = {
    'Languages': ['Java', 'Python', 'C', 'SQL', 'JavaScript', 'HTML5', 'CSS3'],
    'Data Science & ML': ['Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Machine Learning'],
    'Frameworks & Tools': ['Git', 'GitHub', 'VSCode', 'Bootstrap', 'Eclipse'],
    'Core Concepts': ['Data Structures & Algorithms', 'OOP', 'SDLC', 'Database Management', 'Web Development']
}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== Routes ====================

@app.route('/')
def index():
    """Home page with portfolio overview"""
    visits = session.get('visits', 0)
    visits += 1
    session['visits'] = visits
    
    # Check for flash messages
    message = request.args.get('message', None)
    if message:
        flash(message, 'info')
    
    return render_template('index.html', projects=PORTFOLIO_ITEMS[:3], skills=SKILLS)

@app.route('/about')
def about():
    """About page"""
    user_name = session.get('user', 'Guest')
    return render_template('about.html', user_name=user_name)

@app.route('/portfolio')
def portfolio():
    """Portfolio/Projects page"""
    return render_template('portfolio.html', projects=PORTFOLIO_ITEMS, skills=SKILLS)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Individual project detail page with variable rule"""
    project = next((p for p in PORTFOLIO_ITEMS if p['id'] == project_id), None)
    if project is None:
        flash('Project not found!', 'danger')
        return redirect(url_for('portfolio'))
    return render_template('project_detail.html', project=project)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form handling"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Validate form data
        if not all([name, email, subject, message]):
            flash('Please fill in all required fields!', 'danger')
            return redirect(url_for('contact'))
        
        # Save contact message (in production, send email)
        contact_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'subject': subject,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Store in session for demo purposes
        contacts = session.get('contacts', [])
        contacts.append(contact_data)
        session['contacts'] = contacts
        
        flash(f'Thank you {name}! Your message has been received. I will get back to you soon!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/skills')
def skills():
    """Skills page"""
    return render_template('skills.html', skills=SKILLS)

@app.route('/services')
def services():
    """Services page"""
    services_list = [
        {
            'title': 'Web Development',
            'description': 'Full-stack web development with modern frameworks',
            'icon': '💻'
        },
        {
            'title': 'API Development',
            'description': 'RESTful and GraphQL API development',
            'icon': '⚙️'
        },
        {
            'title': 'Database Design',
            'description': 'Database architecture and optimization',
            'icon': '🗄️'
        },
        {
            'title': 'Consulting',
            'description': 'Technical consulting and code review',
            'icon': '📋'
        }
    ]
    return render_template('services.html', services=services_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        # Simple authentication (in production, use proper database)
        if username and password == 'password123':
            session['user'] = username
            
            # Set session expiration
            if remember:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=7)
            
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user = session.get('user')
    contacts = session.get('contacts', [])
    visits = session.get('visits', 0)
    
    return render_template('dashboard.html', user=user, contacts=contacts, visits=visits)

@app.route('/logout')
def logout():
    """Logout user"""
    user = session.get('user', 'User')
    session.clear()
    flash(f'Goodbye, {user}! You have been logged out.', 'info')
    return redirect(url_for('index', message=f'{user} logged out successfully!'))

@app.route('/resume', methods=['GET', 'POST'])
def resume():
    """Resume upload and download page"""
    if request.method == 'POST':
        # Check if file is in request
        if 'resume_file' not in request.files:
            flash('No file selected!', 'danger')
            return redirect(url_for('resume'))
        
        file = request.files['resume_file']
        
        if file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(url_for('resume'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to avoid conflicts
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Store in session
            uploaded_files = session.get('uploaded_files', [])
            uploaded_files.append({
                'filename': filename,
                'original_name': request.files['resume_file'].filename,
                'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            session['uploaded_files'] = uploaded_files
            
            flash('Resume uploaded successfully!', 'success')
            return redirect(url_for('resume'))
        else:
            flash('Invalid file type! Allowed types: pdf, txt, doc, docx, png, jpg, jpeg, gif', 'danger')
    
    uploaded_files = session.get('uploaded_files', [])
    return render_template('resume.html', uploaded_files=uploaded_files)

@app.route('/download/<filename>')
def download(filename):
    """Download uploaded file"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('File not found!', 'danger')
            return redirect(url_for('resume'))
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'danger')
        return redirect(url_for('resume'))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback form with file upload"""
    if request.method == 'POST':
        feedback_text = request.form.get('feedback')
        rating = request.form.get('rating')
        
        if not feedback_text:
            flash('Please provide feedback!', 'danger')
            return redirect(url_for('feedback'))
        
        feedback_data = {
            'feedback': feedback_text,
            'rating': rating,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Handle optional file upload
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    feedback_data['attachment'] = filename
        
        # Store feedback
        feedbacks = session.get('feedbacks', [])
        feedbacks.append(feedback_data)
        session['feedbacks'] = feedbacks
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback'))
    
    return render_template('feedback.html')

# ==================== Error Handlers ====================

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return render_template('errors/403.html'), 403

# ==================== Context Processors ====================

@app.context_processor
def inject_user():
    """Inject user data into all templates"""
    return {
        'current_user': session.get('user'),
        'is_logged_in': 'user' in session
    }

# ==================== Main ====================

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
