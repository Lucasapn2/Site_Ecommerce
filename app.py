from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, current_user, login_user, UserMixin, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
import logging
import os
from urllib.parse import quote



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
    return render_template('index.html', produtos=produtos, user=current_user)


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

@app.route('/formulario-compra', methods=['GET'])
@login_required
def formulario_compra():
    carrinho = session.get('carrinho', [])
    total_compra = request.args.get('total', default=0, type=float)
    produtos_selecionados = []

    for item in carrinho:
        produto_id = item.get('produto_id')
        produto = Produto.query.get(produto_id)
        if produto:
            produtos_selecionados.append(produto)

    return render_template('formulario_compra.html', produtos_selecionados=produtos_selecionados, total_compra=total_compra, user=current_user)

@app.route('/enviar-compra', methods=['POST'])
@login_required
def enviar_compra():
    if request.method == 'POST':
        # Obter informações do formulário
        nome_comprador = request.form['customerName']
        email_comprador = request.form['customerEmail']
        endereco_entrega = request.form['customerAddress']

        # Obter o valor total da compra do campo oculto 'total_compra'
        total_compra = float(request.form['total_compra'])

        # Obter informações do carrinho da sessão
        carrinho = session.get('carrinho', [])
        produtos_comprados = []

        for item in carrinho:
            produto_id = item.get('produto_id')
            produto = Produto.query.get(produto_id)
            if produto:
                produtos_comprados.append(produto)

        # Construir a mensagem para enviar via WhatsApp
        mensagem_whatsapp = f'Olá, {nome_comprador}!\nVocê finalizou a compra com sucesso.\n' \
                           f'Aqui estão os detalhes da sua compra:\n\n'

        for produto in produtos_comprados:
            mensagem_whatsapp += f'Produto: {produto.nome}\nPreço: R$ {produto.preco:.2f}\n\n'

        mensagem_whatsapp += f'Total da compra: R$ {total_compra:.2f}\n'
        mensagem_whatsapp += f'Nome do comprador: {nome_comprador}\n'
        mensagem_whatsapp += f'E-mail do comprador: {email_comprador}\n'
        mensagem_whatsapp += f'Endereço de entrega: {endereco_entrega}\n'
        mensagem_whatsapp += 'Obrigado pela preferência!\n'

        # Substituir SEU_NUMERO_WHATSAPP pelo seu número de WhatsApp com o DDD (exemplo: 55123456789)
        numero_whatsapp = 'SEU_NUMERO_WHATSAPP'
        link_whatsapp = f'https://api.whatsapp.com/send?phone={5521973992437}&text={quote(mensagem_whatsapp)}'

        # Redirecionar para o link do WhatsApp
        return redirect(link_whatsapp)

@app.route('/comprar', methods=['POST'])
@login_required
def comprar_produto():
    if request.method == 'POST':
        # Obtenha os detalhes do produto selecionado do formulário
        produto_id = request.form['produto_id']
        produto_nome = request.form['produto_nome']
        produto_imagem = request.form['produto_imagem']
        produto_preco = float(request.form['produto_preco'])

        # Obtenha o carrinho da sessão ou crie um carrinho vazio
        carrinho = session.get('carrinho', [])

        # Adicione os detalhes do produto ao carrinho
        carrinho.append({
            'produto_id': produto_id,
            'produto_nome': produto_nome,
            'produto_imagem': produto_imagem,
            'produto_preco': produto_preco
        })

        # Atualize o carrinho na sessão
        session['carrinho'] = carrinho

        # Calcule o valor total da compra
        total_compra = sum(item.get('produto_preco', 0) for item in carrinho)

        # Redirecione para a página do formulário de compra passando o valor total como parâmetro
        return redirect(url_for('formulario_compra', total_compra=total_compra))


# Adicione uma nova rota para atualizar o carrinho de compras
@app.route('/update-cart', methods=['POST'])
@login_required
def update_cart():
    if request.method == 'POST':
        carrinho = request.json.get('carrinho', [])
        session['carrinho'] = carrinho

    return '', 204



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
