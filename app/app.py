from flask import Flask, render_template, request, redirect, url_for, flash
# from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from random import choice
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234567890'
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/cmsm'  # Update with your MySQL database details
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Customer(UserMixin, db.Model):
    __tablename__ = 'customers'

    customerid = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phones = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def get_id(self):
        return str(self.customerid)


class Technician(UserMixin, db.Model):
    __tablename__ = 'technicians'

    technicianid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def get_id(self):
        return str(self.technicianid)


class ServiceRequest(db.Model):
    __tablename__ = 'servicerequests'

    requestid = db.Column(db.Integer, primary_key=True)
    requestdate = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)

    # Set the default value for status to 'New'
    status = db.Column(db.Enum('New', 'In Progress', 'Completed'), default='New', nullable=True)

    customerid = db.Column(db.Integer, db.ForeignKey('customers.customerid'), nullable=True)
    customer = db.relationship('Customer', backref=db.backref('servicerequests', lazy=True))

    technicianid = db.Column(db.Integer, db.ForeignKey('technicians.technicianid'), nullable=True)
    technician = db.relationship('Technician', backref=db.backref('servicerequests', lazy=True))

    itemid = db.Column(db.Integer, db.ForeignKey('inventory.itemid'), nullable=True)
    item = db.relationship('Inventory', backref=db.backref('servicerequests', lazy=True))


class Inventory(db.Model):
    __tablename__ = 'inventory'

    itemid = db.Column(db.Integer, primary_key=True)
    itemname = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)


login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    # The user_id is the unique identifier for the user, which is stored in the session.
    # You need to return the User object based on this ID.
    # Example for Customer model:
    return Customer.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Try to authenticate as a customer
        customer = Customer.query.filter_by(email=email, password=password).first()

        if customer:
            login_user(customer)
            flash('Login successful!', 'success')
            return redirect(url_for('customer_dashboard'))  # Redirect to the customer dashboard after login

        # Try to authenticate as a technician
        technician = Technician.query.filter_by(email=email, password=password).first()

        if technician:
            login_user(technician)
            flash('Login successful!', 'success')
            return redirect(url_for('technician_dashboard'))  # Redirect to the technician dashboard after login

        flash('Login failed. Check your username and password.', 'error')

    return render_template('login.html')


@app.route('/customer-signup', methods=['GET', 'POST'])
def customer_signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        phones = request.form.get('phones')
        address = request.form.get('address')
        password = request.form.get('password')

        # Check if the email is already registered
        existing_customer = Customer.query.filter_by(email=email).first()

        if existing_customer:
            flash('Email is already registered. Please log in.', 'error')
            return redirect(url_for('login'))

        # Hash the password before saving it
        # hashed_password = generate_password_hash(password, method='sha256')

        # Create a new customer
        new_customer = Customer(
            firstname=firstname,
            lastname=lastname,
            email=email,
            phones=phones,
            address=address,
            password=password
            # password=hashed_password
        )

        # Add and commit the new customer to the database
        db.session.add(new_customer)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('customer_signup.html')


@app.route('/technician-dashboard')
def technician_dashboard():
    return render_template('technician_dashboard.html')


@app.route('/accept-work/<int:request_id>')
def accept_work(request_id):
    service_request = ServiceRequest.query.get(request_id)

    if service_request:
        service_request.status = 'In Progress'
        db.session.commit()
        # Additional logic as needed
        flash('Work accepted successfully!', 'success')
    else:
        flash('Service request not found', 'error')

    return redirect(url_for('dashboard'))

# CUSTOMER'S ROUTES ----------------------------------------------------------------------------------
@app.route('/customer-dashboard')
def customer_dashboard():
    #if current_user.is_authenticated:
     #   customer_id = current_user.id
      #  customer_service_requests = ServiceRequest.query.filter_by(customer_id=customer_id).all()

    return render_template('customer_dashboard.html')


@app.route('/check-in', methods=['POST'])
def check_in():
    '''
    request_id = request.form.get('request_id')
    # Add logic to check in on an existing request
    return f"Checking in on request with ID: {request_id}"
    '''

@app.route('/new-request')
def new_request():
    '''
    # Add logic to handle creating a new service request
    return "Create a New Service Request Page"
    '''


@app.route('/create-service-request', methods=['GET', 'POST'])
@login_required
def create_service_request():
    if request.method == 'POST':
        description = request.form.get('description')
        requestdate = request.form.get('requestdate')

        # Get a list of available technicians (you need to implement this logic)
        available_technicians = Technician.query.all()

        if not available_technicians:
            flash('No available technicians. Please try again later.', 'error')
            return redirect(url_for('dashboard'))

        # Randomly select a technician
        selected_technician = choice(available_technicians)

        # Create a new service request
        new_service_request = ServiceRequest(
            requestdate=requestdate,
            customerid=current_user.customerid,
            description=description,
            status='New',
            technicianid=selected_technician.technicianid  # Assign the work to the selected technician
        )

        db.session.add(new_service_request)
        db.session.commit()

        # Notify the customer about the request ID
        flash(f'Service request submitted successfully! Your request ID is {new_service_request.requestid}', 'success')

        return redirect(url_for('customer_dashboard'))

    return render_template('create_service_request.html', current_date="2024-01-30")


@app.route('/submit-service-request')#, methods=['POST'])
def submit_service_request():
    '''
    # Retrieve form data
    customer_name = request.form.get('customer_name')
    description = request.form.get('description')
    # You can handle the request_date based on your backend logic

    # Generate a unique service request ID (you may use your own logic)
    service_request_id = generate_unique_id()

    # Process the service request data (e.g., store it in the database)
    # ...

    # Pass the service request ID to the template

    return render_template('service_request_confirmation.html', service_request_id=service_request_id)'''
    return render_template('service_request_confirmation.html')


def generate_unique_id():
    # Implement your logic to generate a unique ID (e.g., using UUID)
    # Replace this with your actual implementation
    import uuid
    return str(uuid.uuid4())


# Route for checking service request status
@app.route('/check-status')#, methods=['POST'])
def check_status():
    '''
    # Retrieve service request ID from the form
    service_request_id = request.form.get('service_request_id')

    # Placeholder logic to get the status based on your backend data (replace this with your actual implementation)
    status = get_status_by_service_request_id(service_request_id)

    # Render the check_status.html template with the status
    return render_template('check_status.html', status=status, service_request_id=service_request_id)'''
    return render_template('check_status.html')


def get_status_by_service_request_id(service_request_id):
    # Implement your logic to retrieve the status based on the service request ID
    # Replace this with your actual implementation
    # This is a placeholder, you might fetch the status from the database
    return "In Progress"  # Replace with your actual status


if __name__ == '__main__':
    app.run(debug=True)
