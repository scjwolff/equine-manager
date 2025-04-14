from flask import Flask, render_template, request, redirect, url_for

import os
from werkzeug.utils import secure_filename
from flask import send_from_directory


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

temp_horse_data = {}


users = []
horses = []

@app.route('/')
def home():
    return render_template('index.html', users=users)

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    role = request.form['role']
    users.append({'username': username, 'role': role})
    return redirect(url_for('home'))

@app.route('/horses')
def horse_list():
    return render_template('horses.html', horses=horses)

@app.route('/add_horse', methods=['POST'])
def add_horse():
    name = request.form['name']
    feed = request.form['feed']
    turnout = request.form['turnout']
    horses.append({'name': name, 'feed': feed, 'turnout': turnout})
    return redirect(url_for('horse_list'))

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
    eligible_owners = [user for user in users if user['role'] in ['client', 'trainer']]
    
    return render_template('horse_step2.html', owners=eligible_owners)

@app.route('/add_horse_step3', methods=['POST'])
def add_horse_step3():
    selected_owner = request.form.get('owner')
    new_owner = request.form.get('new_owner')
    new_role = request.form.get('new_role')
    
    if new_owner and new_role:
        owner_name = new_owner
        users.append({'username': new_owner, 'role': new_role})
    else:
        owner_name = selected_owner

    temp_horse_data['owner'] = owner_name
    
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
    horses.append(temp_horse_data.copy())
    temp_horse_data.clear()
    return redirect(url_for('horse_list'))

@app.route('/horse/<int:horse_id>')
def view_horse(horse_id):
    if horse_id >= len(horses):
        return "Horse not found", 404
    horse = horses[horse_id]
    return render_template('horse_profile.html', horse=horse, horse_id=horse_id)

@app.route('/edit_horse/<int:horse_id>', methods=['GET', 'POST'])
def edit_horse(horse_id):
    if horse_id >= len(horses):
        return "Horse not found", 404

    horse = horses[horse_id]

    if request.method == 'POST':
        # Update data
        horse['name'] = request.form['name']
        horse['age'] = request.form['age']
        horse['height'] = request.form['height']
        horse['am_hay'] = request.form['am_hay']
        horse['pm_hay'] = request.form['pm_hay']
        horse['lunch_hay'] = request.form['lunch_hay']
        horse['am_grain'] = request.form['am_grain']
        horse['pm_grain'] = request.form['pm_grain']
        horse['am_supplements'] = request.form['am_supplements']
        horse['pm_supplements'] = request.form['pm_supplements']
        horse['am_meds'] = request.form['am_meds']
        horse['pm_meds'] = request.form['pm_meds']
        return redirect(url_for('view_horse', horse_id=horse_id))

    return render_template('edit_horse.html', horse=horse, horse_id=horse_id)





if __name__ == '__main__':
    app.run(debug=True)
