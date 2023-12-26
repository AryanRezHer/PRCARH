import os
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'Platafora de Recentas de Cocina'
#Path para encontrar la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'usuarios.db')
#Inicializar Flask_login
login_manager = LoginManager()
login_manager.init_app(app)
#Inicializar db
db=SQLAlchemy(app)

#declaracion de clases
class usuarios(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

class recetas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(50), nullable=False)
    receta = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(50), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
     return usuarios.query.get(user_id)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        usr = request.form['username']
        pwd = request.form['password']
        if usr and pwd:
            try:
                user = usuarios.query.filter_by(username=usr,password=pwd).first()
                login_user(user)
                return redirect(url_for('feed',id=current_user.id))
            except AttributeError:
                mensaje = 'Por favor registrese primero'
                return render_template('singup.html', mensaje=mensaje)

    return render_template('login.html')

@app.route('/singup', methods=['GET','POST'])
def singup():
    if request.method == 'POST':
        usr = request.form['username']
        pwd = request.form['password']
        if usr and pwd:
            new_user = usuarios(username=usr,password=pwd)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('singup.html')

@app.route('/usuario')
@login_required
def usuario():
    return render_template('profile.html', id=current_user.id)

@app.route('/return')
@login_required
def volver():
    return redirect(url_for('feed', id=current_user.id))

@app.route('/addreceta')
@login_required
def new_receta():
    return render_template('addreceta.html')

@app.route('/feed/<int:id>')
@login_required
def feed(id):
     receta = recetas.query.all()
     return render_template('feed.html', recetas = receta)

@app.route('/feed/addreceta', methods=['GET','POST'])
@login_required
def add():
    try:
        titulo = request.form['titulo']
        receta = request.form['receta']
        autor = request.form['autor']
        if titulo and receta:
            post = recetas(titulo=titulo,receta=receta,autor = autor,usuario_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('feed', id=current_user.id))
    except TypeError:
        return render_template('addreceta.html')


@app.route('/profile/<int:id>')
@login_required
def profile(id):
     return redirect('profile', id=current_user.id)

@app.route('/logout')
@login_required
def logout():
     logout_user()
     return redirect(url_for('index'))

@app.route('/eliminar/<id>')
def eliminarreceta(id):
    receta = recetas.query.filter_by(id=int(id)).first()
    if current_user.id == receta.usuario_id:
        db.session.delete(receta)
        db.session.commit()
        return redirect(url_for('feed', id=current_user.id))
    return redirect(url_for('feed', id=current_user.id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)