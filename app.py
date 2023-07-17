from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_user, UserMixin, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
import logging
import os


app = Flask(__name__)
# Configuração do registro de log
logging.basicConfig(level=logging.DEBUG)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'fazer_login'  # Define a rota de login para redirecionamento

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    def is_active(self):
        return self.is_active

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text)
    imagem = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    produtos = Produto.query.all()
    return render_template('home.html', produtos=produtos, user=current_user)


@app.route('/carrossel')
def carrossel():
    return render_template('carrossel.html', user=current_user)

@app.route('/criar-conta', methods=['GET', 'POST'])
def criar_conta():
    message = None
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        is_admin = request.form.get('is_admin', False)

        novo_usuario = User(nome=nome, email=email, senha=senha, is_admin=is_admin)
        db.session.add(novo_usuario)
        db.session.commit()

        return render_template('criar_conta.html', success=True)

    return render_template('criar_conta.html', message=message)

@app.route('/produtos')
def produtos():
    produtos = Produto.query.all()
    return render_template('produtos.html', produtos=produtos, user=current_user)

@app.route('/adicionar-produto', methods=['GET', 'POST'])
@login_required
def adicionar_produto():
    if not current_user.is_admin:
        return redirect(url_for('produtos'))

    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        descricao = request.form['descricao']
        imagem = request.form['imagem']

        novo_produto = Produto(nome=nome, preco=preco, descricao=descricao, imagem=imagem)
        db.session.add(novo_produto)
        db.session.commit()

        return redirect(url_for('admin_panel'))

    return render_template('adicionar_produto.html', user=current_user)


@app.route('/editar_produto/<int:produto_id>', methods=['GET', 'POST'])
@login_required
def editar_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)

    if not current_user.is_admin:
        return redirect(url_for('produtos'))

    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.preco = float(request.form['preco'])
        produto.descricao = request.form['descricao']
        produto.imagem = request.form['imagem']
        db.session.commit()

        return redirect(url_for('admin_panel'))

    return render_template('editar_produto.html', produto=produto, user=current_user)

@app.route('/excluir_produto/<int:produto_id>', methods=['GET', 'POST'])
@login_required
def excluir_produto(produto_id):
    logging.debug('Solicitação de exclusão de produto recebida')
    logging.debug('Método usado: %s', request.method)

    if not current_user.is_admin:
        return redirect(url_for('produtos'))

    produto = Produto.query.get_or_404(produto_id)
    db.session.delete(produto)
    db.session.commit()

    return redirect(url_for('admin_panel'))

@app.route('/alterar-imagens-carrossel', methods=['GET', 'POST'])
@login_required
def alterar_imagens_carrossel():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Verifica se o usuário enviou 3 arquivos de imagem
        if 'image1' not in request.files or 'image2' not in request.files or 'image3' not in request.files:
            flash('Por favor, selecione 3 imagens para o carrossel')
            return redirect(request.url)

        file1 = request.files['image1']
        file2 = request.files['image2']
        file3 = request.files['image3']

        # Salva os arquivos de imagem no diretório do carrossel com os nomes fixos
        file1.save(os.path.join(app.static_folder, 'carrossel', 'image1.jpg'))
        file2.save(os.path.join(app.static_folder, 'carrossel', 'image2.jpg'))
        file3.save(os.path.join(app.static_folder, 'carrossel', 'image3.jpg'))

        flash('Imagens do carrossel alteradas com sucesso')
        return redirect(url_for('index'))

    return render_template('carrossel.html', user=current_user)








@app.route('/fazer-login', methods=['GET', 'POST'])
def fazer_login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        user = User.query.filter_by(email=email).first()

        if user and user.senha == senha:
            login_user(user)

            if user.is_admin:
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/fazer-logout', methods=['POST'])
@login_required
def fazer_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    produtos = Produto.query.all()
    return render_template('admin_panel.html', produtos=produtos, user=current_user)

if __name__ == '__main__':
    app.run(debug=True)
