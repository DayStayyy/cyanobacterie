from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import predictor
from datetime import datetime, timedelta
from data import DataManager
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Clé secrète pour les sessions
data_manager = DataManager()

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    lakes = data_manager.get_user_lakes(session['username'])
    return render_template('index.html', lakes=lakes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if data_manager.verify_user(username, password):
            session['username'] = username
            return redirect(url_for('home'))
        return render_template('login.html', error="Identifiants invalides")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        success, message = data_manager.register_user(username, password)
        if success:
            return redirect(url_for('login'))
        return render_template('register.html', error=message)
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/lakes', methods=['GET', 'POST'])
def lakes():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        lake_name = request.form['name']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        lake_type = request.form['type']
        
        success, message = data_manager.add_lake(
            session['username'], 
            lake_name, 
            latitude, 
            longitude, 
            lake_type
        )
        
        if not success:
            return render_template('lakes.html', 
                                 error=message, 
                                 lakes=data_manager.get_user_lakes(session['username']))
    
    return render_template('lakes.html', 
                         lakes=data_manager.get_user_lakes(session['username']))

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Non authentifié'}), 401
    
    try:
        data = request.form
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        lake_type = data['lakeType']

        predictions = []
        current_date = datetime.now()
        
        for i in range(7):
            date = current_date + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            risk_analysis = predictor.predict_for_date(
                latitude, 
                longitude, 
                date_str, 
                lake_type
            )
            print(risk_analysis)
            
            predictions.append({
                'date': date_str,
                'flag': risk_analysis[0],
                'message': risk_analysis[1],
                'conditions': risk_analysis[2]
            })

        return jsonify({
            'success': True,
            'predictions': predictions
        })

    except Exception as e:
        print(f"Erreur app predict: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)