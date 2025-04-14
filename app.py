from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///equine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Horse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer)
    height = db.Column(db.Float)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo = db.Column(db.String(200))

    # Feeding
    am_hay = db.Column(db.Integer)
    pm_hay = db.Column(db.Integer)
    lunch_hay = db.Column(db.String(200))

    # Grain/Supplements
    am_grain = db.Column(db.String(200))
    am_supplements = db.Column(db.String(200))
    am_meds = db.Column(db.String(200))

    pm_grain = db.Column(db.String(200))
    pm_supplements = db.Column(db.String(200))
    pm_meds = db.Column(db.String(200))


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

temp_horse_data = {}



@app.route('/')
def home():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    role = request.form['role']
    new_user = User(username=username, role=role)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/horses')
def horse_list():
    horses = Horse.query.all()
    return render_template('horses.html', horses=horses)

@app.route('/add_horse_step1')
def add_horse_step1():
    return render_template('horse_step1.html')

@app.route('/add_horse_step2', methods=['POST'])
def add_horse_step2():
    # Save step 1 data
    temp_horse_data['name'] = request.form['name']
    temp_horse_data['age'] = request.form['age']
    temp_horse_data['height'] = request.form['height']
    
    # Filter users to show only trainers and clients
    eligible_owners = User.query.filter(User.role.in_(['client', 'trainer'])).all()
    
    return render_template('horse_step2.html', owners=eligible_owners)

@app.route('/add_horse_step3', methods=['POST'])
def add_horse_step3():
    selected_owner = request.form.get('owner')
    new_owner = request.form.get('new_owner')
    new_role = request.form.get('new_role')

    if new_owner and new_role:
        owner = User(username=new_owner, role=new_role)
        db.session.add(owner)
        db.session.commit()
        temp_horse_data['owner_id'] = owner.id
    else:
        # Fetch the existing user from the database
        owner = User.query.filter_by(username=selected_owner).first()
        if owner:
            temp_horse_data['owner_id'] = owner.id
        else:
            temp_horse_data['owner_id'] = None  # fallback or error handling

    return render_template('horse_step3.html')


@app.route('/add_horse_step4', methods=['POST'])
def add_horse_step4():
    temp_horse_data['am_hay'] = request.form['am_hay']
    temp_horse_data['pm_hay'] = request.form['pm_hay']
    temp_horse_data['lunch_hay'] = request.form['lunch_hay']

    return render_template('horse_step4.html')

@app.route('/add_horse_step5', methods=['POST'])
def add_horse_step5():
    temp_horse_data['am_grain'] = request.form['am_grain']
    temp_horse_data['am_supplements'] = request.form['am_supplements']
    temp_horse_data['am_meds'] = request.form['am_meds']
    
    temp_horse_data['pm_grain'] = request.form['pm_grain']
    temp_horse_data['pm_supplements'] = request.form['pm_supplements']
    temp_horse_data['pm_meds'] = request.form['pm_meds']

    return render_template('horse_step5.html')

@app.route('/add_horse_step6', methods=['POST'])
def add_horse_step6():
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            temp_horse_data['photo'] = filename
        else:
            temp_horse_data['photo'] = None
    else:
        temp_horse_data['photo'] = None

    return render_template('horse_step6.html', horse=temp_horse_data)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/save_horse', methods=['POST'])
def save_horse():
    horse = Horse(
        name=temp_horse_data['name'],
        age=temp_horse_data['age'],
        height=temp_horse_data['height'],
        owner_id=temp_horse_data['owner_id'],
        photo=temp_horse_data.get('photo'),
        am_hay=temp_horse_data.get('am_hay'),
        pm_hay=temp_horse_data.get('pm_hay'),
        lunch_hay=temp_horse_data.get('lunch_hay'),
        am_grain=temp_horse_data.get('am_grain'),
        pm_grain=temp_horse_data.get('pm_grain'),
        am_supplements=temp_horse_data.get('am_supplements'),
        pm_supplements=temp_horse_data.get('pm_supplements'),
        am_meds=temp_horse_data.get('am_meds'),
        pm_meds=temp_horse_data.get('pm_meds')
)
    db.session.add(horse)
    db.session.commit()
    temp_horse_data.clear()

    temp_horse_data.clear()
    return redirect(url_for('horse_list'))

@app.route('/horse/<int:horse_id>')
def view_horse(horse_id):
    horse = Horse.query.get_or_404(horse_id)
    return render_template('horse_profile.html', horse=horse, horse_id=horse_id)


@app.route('/edit_horse/<int:horse_id>', methods=['GET', 'POST'])
def edit_horse(horse_id):
    horse = Horse.query.get_or_404(horse_id)

    if request.method == 'POST':
        horse.name = request.form['name']
        horse.age = request.form['age']
        horse.height = request.form['height']
        horse.am_hay = request.form['am_hay']
        horse.pm_hay = request.form['pm_hay']
        horse.lunch_hay = request.form['lunch_hay']
        horse.am_grain = request.form['am_grain']
        horse.pm_grain = request.form['pm_grain']
        horse.am_supplements = request.form['am_supplements']
        horse.pm_supplements = request.form['pm_supplements']
        horse.am_meds = request.form['am_meds']
        horse.pm_meds = request.form['pm_meds']

        db.session.commit()
        return redirect(url_for('view_horse', horse_id=horse.id))

    return render_template('edit_horse.html', horse=horse, horse_id=horse.id)




with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
