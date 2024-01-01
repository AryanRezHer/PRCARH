import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
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
    ingredientes = db.Column(db.String(200), nullable=False)
    receta = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(50), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)

class comentarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
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

@app.route('/search', methods=['GET','POST'])
@login_required
def buscador():
    if request.method == 'POST':
        busqueda = request.form['buscador']
        mensaje = 'No hemos encontrado ningun resultado como ' + busqueda
        receta = recetas.query.filter(recetas.titulo.ilike(f"%{busqueda}%") | recetas.autor.ilike(f"%{busqueda}%")).all()
        return render_template('buscador.html', recetas = receta, mensaje=mensaje)
        
    return redirect(url_for('volver'))


@app.route('/addreceta')
@login_required
def new_receta():
    return render_template('addreceta.html')

@app.route('/feed/<int:id>')
@login_required
def feed(id):
    receta = recetas.query.all()
    #antesdetener vue.js
    #post_like = Like.query.filter_by(receta_id=recetas.id).first()
    return render_template('feed.html', recetas = receta)

@app.route('/feed/addreceta', methods=['GET','POST'])
@login_required
def add():
    try:
        titulo = request.form['titulo']
        ingredientes = request.form['ingredientes']
        receta = request.form['receta']
        autor = request.form['autor']
        if titulo and receta:
            post = recetas(titulo=titulo,ingredientes=ingredientes,receta=receta,autor = autor,usuario_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            post_like = Like(receta_id = post.id, usuario_id=current_user.id)
            db.session.add(post_like)
            db.session.commit()
            return redirect(url_for('feed', id=current_user.id))
    except TypeError:
        return render_template('addreceta.html')
    
@app.route('/get_likes')
@login_required
def get_likes():
    likes_value = Like.query.filter_by(receta_id=recetas.id).first()
    data = {'id': likes_value.id ,'receta_id': likes_value.receta_id ,'usuario_id': likes_value.usuario_id, 'likes': likes_value.likes if likes_value else None}
    return jsonify(data)

@app.route('/getComentarios')
def dcomentario():
    try:
        comentarios_lista = comentarios.query.all()
        print(comentarios_lista)
        if comentarios_lista:
            data = [{'id': comen.id, 'content': comen.content, 'usuario_id': comen.usuario_id} for comen in comentarios_lista]
            return jsonify(data)
        else:
            return jsonify([])
    except Exception as e:
        print(f"Error en la función datos(): {str(e)}")
        return jsonify({"error": "Internal Server Error"})


@app.route('/update_likes', methods=['POST'])
def update_likes():
    try:
         # Recibimos la información del cliente
        rid = request.json.get('receta_id')
        nlike = Like.query.filter_by(receta_id=rid).first()
        nlike.likes += 1
        db.session.commit()   
        return jsonify({'id': nlike.id ,'receta_id': nlike.receta_id ,'usuario_id': nlike.usuario_id, 'likes': nlike.likes })
    except Exception as e:
        print(f"Error en la función actualizar_basede_datos(): {str(e)}")
        return jsonify({'error': 'Error interno del servidor'})
    
@app.route('/update_likes2', methods=['POST'])
def update_likes2():
    try:
         # Recibimos la información del cliente
        rid = request.json.get('receta_id')
        nlike = Like.query.filter_by(receta_id=rid).first()
        nlike.likes -=1
        db.session.commit()   
        return jsonify({'id': nlike.id ,'receta_id': nlike.receta_id ,'usuario_id': nlike.usuario_id, 'likes': nlike.likes })
    except Exception as e:
        print(f"Error en la función actualizar_basede_datos(): {str(e)}")
        return jsonify({'error': 'Error interno del servidor'})

@app.route('/update_comentarios', methods=['POST'])
def update_comen():
    try:
         # Recibimos la información del cliente
        newcomen = request.json.get('comentario')
        if newcomen:
            comen = comentarios(content=newcomen,usuario_id=current_user.id)
            db.session.add(comen)
            db.session.commit()   
            return jsonify({'id': comen.id ,'content': comen.content ,'usuario_id': comen.usuario_id})
        else:
            return jsonify({'error': 'El comentario no puede estar vacío o contener solo espacios en blanco'})
    except Exception as e:
        print(f"Error en la función actualizar_basede_datos(): {str(e)}")
        return jsonify({'error': 'Error interno del servidor'})
    

@app.route('/feed/editartarea/<id>', methods=['GET','POST'])
@login_required
def edit(id):
    try:
        old_receta = recetas.query.filter_by(id=int(id)).first()
        new_titulo = request.form['titulo']
        new_ingredientes = request.form['ingredientes']
        new_receta = request.form['receta']
        new_autor = request.form['autor']
        if new_titulo and new_receta:
            old_receta.titulo = new_titulo
            old_receta.ingredientes = new_ingredientes
            old_receta.receta = new_receta
            old_receta.autor = new_autor
            db.session.add(old_receta)
            db.session.commit()
            return redirect(url_for('feed', id=current_user.id))
    except TypeError:
        return render_template('editar.html')

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
@login_required
def eliminarreceta(id):
    receta = recetas.query.filter_by(id=int(id)).first()
    post_like = Like.query.filter_by(receta_id=int(id)).first()           
    if current_user.id == receta.usuario_id:
        db.session.delete(receta)
        db.session.delete(post_like)
        db.session.commit()
        return redirect(url_for('feed', id=current_user.id))
    return redirect(url_for('feed', id=current_user.id))

@app.route('/eliminarcomentario', methods=['POST'])
def updatedbelim():
    try:
        id = request.json.get('id')
        if id:
            coment = comentarios.query.get(id)
            if coment:
                db.session.delete(coment)
                db.session.commit()
                return jsonify({'message': 'hecho usuario eliminado'})
            else:
                return jsonify({'error': 'Usuario no encontrado'})
    except Exception as e:
        print(f"Error en la función actualizar_basede_datos(): {str(e)}")
        return jsonify({'error': 'Error interno del servidor'})
    
@app.route('/editar/<id>')
@login_required
def editarreceta(id):
    receta = recetas.query.filter_by(id=int(id)).first()
    return render_template('editar.html', recetas = receta, id = receta.id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)