from flask import Flask, render_template, redirect, request, url_for
from datetime import datetime
from config.database import SupabaseConnection
from dao.funcionario_dao import FuncionarioDAO
from models.funcionario import Funcionario

app = Flask(__name__)

client = SupabaseConnection().client
funcionario_dao = FuncionarioDAO(client)

@app.route("/")
def index():
    return render_template("index.html", title="TABELA", app_name="TABELA DE FUNCIONÁRIOS", funcionarios=funcionario_dao.read_all())

@app.template_filter('format_cpf')
def format_cpf(cpf):
    if not cpf or len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"

@app.route("/funcionario/<string:pk>/<int:id>")
def details(pk, id):
    funcionario = funcionario_dao.read(pk, id)
    return render_template("details.html", funcionario=funcionario, datetime=datetime)

@app.route('/funcionario/novo', methods=['GET', 'POST'])
def create():

    #Se for metodo POST no form
    if request.method == "POST":
        
        #Objeto do tipo Funcionario
        new_employee = Funcionario(
                _cpf = request.form["cpf"],
                _pnome = request.form["pnome"],
                _unome = request.form["unome"],
                _data_nasc = request.form["data_nasc"],
                _salario = request.form["salario"],
                _endereco = request.form["endereco"],
                _sexo = request.form["sexo"]
            )

        #Linha que vai criar o novo funcionario
        create = funcionario_dao.create(new_employee)

        #Se funcionario de certo, ele irá enviar de volta para o index
        if create:
            return redirect(url_for('index'))
    
    #Se for metodo GET
    return render_template('create.html', datetime=datetime)

@app.route('/funcionario/edit/<string:pk>', methods=['GET', 'POST'])
def update(pk):
    #Se for metodo POST
    if request.method == 'POST':
        dat = request.form
        
        current_employee = funcionario_dao.read('cpf', pk)
        
        from datetime import datetime as dt
        
        data_nasc = current_employee.data_nasc
        if dat.get('data_nasc'):
            try:
                data_nasc = dt.strptime(dat['data_nasc'], '%Y-%m-%d').date()
            except:
                pass
        
        salario = current_employee.salario
        try:
            salario = float(dat.get('salario', salario))
        except:
            pass
        
        num_depto = dat.get('numero_departamento')
        numero_departamento = None
        if num_depto and num_depto.strip():
            try:
                numero_departamento = int(num_depto)
            except:
                numero_departamento = current_employee.numero_departamento
        
        cpf_supervisor = dat.get('cpf_supervisor')
        if cpf_supervisor and cpf_supervisor.strip():
            cpf_supervisor = cpf_supervisor.replace('.', '').replace('-', '')
            if len(cpf_supervisor) != 11:
                cpf_supervisor = None
        else:
            cpf_supervisor = None
        
        #Objeto do tipo funcionario para atualizar
        updated_employee = Funcionario(
            _cpf = pk,
            _pnome = dat.get('pnome', current_employee.pnome),
            _unome = dat.get('unome', current_employee.unome),
            _data_nasc = data_nasc,
            _endereco = dat.get('endereco', current_employee.endereco),
            _salario = salario,
            _sexo = dat.get('sexo', current_employee.sexo),
            _cpf_supervisor = cpf_supervisor,
            _numero_departamento = numero_departamento,
            _created_at = current_employee.created_at
        )
        
        #Linha que faz o update
        update = funcionario_dao.update('cpf', pk, updated_employee)
        
        #Se o update de certo ele vai fazer isso aqui
        if update:
            return redirect(url_for('index'))
    
    #Lendo o funcionario
    funcionario = funcionario_dao.read('cpf', pk)
    
    return render_template('edit.html', funcionario=funcionario, datetime=datetime)

@app.route('/funcionario/delete/<string:pk>', methods=['GET', 'POST'])
def delete(pk):
    #Se o metodo for POST
    if request.method == 'POST':
        #Linha resposavel por apagar o funcionario 
        delete = funcionario_dao.delete('cpf', pk)
        
        #Se ele conseguir deletar o funcionario vai acontecer isso aqui
        if delete:
            return redirect(url_for('index'))
    
    #Lê o funcionario
    funcionario = funcionario_dao.read('cpf', pk)
        
    return render_template('delete.html', funcionario=funcionario, datetime=datetime)