from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
import pymysql
from pymysql import IntegrityError
import hashlib
import threading
import TelegramAPI as TG
from config import db_config
from db_errors import DBErrors

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type"])

def execute_query(query, values=None):
    result = None
    rows = 0
    try:
        with pymysql.connect(**db_config) as mydb:
            mycursor = mydb.cursor()
            if values:
                mycursor.execute(query, values)
            else:
                mycursor.execute(query)
            if query.upper().startswith(("INSERT", "UPDATE", "DELETE")):
                rows = mycursor.rowcount
                mydb.commit()
            else:
                result = mycursor.fetchall()
        return result, rows
    except pymysql.Error as e:
        DBErrors.handle_error(e)

def serialize_user(user):
    return {
        'code': user[0],
        'name': user[1],
        'permission': user[3]
    }

# Rota para listar usuários
@app.route('/users', methods=['GET'])
def get_user_or_users():
    code = request.args.get('code')
    query = "SELECT * FROM users"
    if code:
        query += " WHERE code = %s"
        values = [code]
    else:
        values = None
    users_db = execute_query(query, values)
    if code:
        list_users = serialize_user(users_db[0]) if users_db else {}
    else:
        list_users = [serialize_user(user) for user in users_db]
    return make_response(
        jsonify(
            info=list_users,
            statusCode=200
        )
    )

# Rota para listar peças
@app.route('/parts', methods=['GET'])
def get_parts_or_part():
    serial_number = request.args.get('serial_number')
    if serial_number:
        query = (
            "SELECT * FROM parts p "
            "JOIN model_parts m ON p.model_prefix = m.prefix "
            "LEFT JOIN users u ON p.inspector = u.code "
            "WHERE p.model_prefix = m.prefix AND p.serial_number = %s;"
        )
        values = [serial_number[2:]]
    else:
        role = request.args.get('role')
        values = None
        if role == "Inspetor":
            query = (
                "SELECT p.*, m.model, u.name AS inspector_name "
                "FROM parts p "
                "JOIN model_parts m ON p.model_prefix = m.prefix "
                "LEFT JOIN users u ON p.inspector = u.code "
                "WHERE p.inspector IS NULL;"
            )
        else:
            query = (
                "SELECT p.*, m.model, u.name AS inspector_name "
                "FROM parts p "
                "JOIN model_parts m ON p.model_prefix = m.prefix "
                "LEFT JOIN users u ON p.inspector = u.code "
                "WHERE p.validation IS NULL AND p.inspector IS NOT NULL;"
            )
    parts_db = execute_query(query, values)
    if serial_number:
        for part in parts_db:
            serial_number = part[1] + part[0]
            data_hora = str(part[3])
            list_parts = {
                'serie': serial_number,
                'model': part[9],
                'situation': part[2],
                'date': data_hora,
                'codeInspector': part[5],
                'codeSupervisor': part[6],
                'finalCheck': part[7],
                'inspector': part[12] if part[5] is not None else None,
                'supervisor': None
            }
    else:
        list_parts = []
        for part in parts_db:
            serial_number = part[1] + str(part[0])
            data_hora = str(part[3])
            part_info = {
                'serial_number': serial_number,
                'model': part[9],
                'status': part[2],
                'datetime_verif': data_hora,
                'inspector': part[10] if part[5] is not None else None
            }
            list_parts.append(part_info)

    return make_response(
        jsonify(
            info=list_parts,
            statusCode=200
        )
    )

# Rota para listar modelos de peças
@app.route('/model-parts', methods=['GET'])
def get_models():
    query = "SELECT prefix, model FROM model_parts"
    models_db = execute_query(query)
    list_models = [{"prefix": prefix, "model": model} for prefix, model in models_db]
    return make_response(
        jsonify(
            info=list_models,
            statusCode=200
        )
    )

# Rota para salvar um modelo de peça
@app.route('/model/save', methods=['POST'])
def save_model(prefix=None, model_name=None):
    model = {}
    if not (prefix and model_name):
        model = request.json
    else:
        model['prefix'] = prefix
        model['model'] = model_name
    query = 'INSERT INTO model_parts (prefix, model) VALUES (upper(%s), upper(%s))'
    values = (model['prefix'], model['model'])
    
    result = execute_query(query, values)
    print(result)
    
    if result is not None:
        message = 'Modelo cadastrado com sucesso'
        status_code = 200
    else:
        message = 'Erro ao cadastrar o modelo'
        status_code = 500

    if not (prefix and model_name):
        return make_response(
            jsonify(
                message=message,
                statusCode=status_code
            )
        )

# Rota para deletar um modelo de peça
@app.route('/delete-model/', methods=['DELETE'])
def delete_model():
    prefix = request.args.get('prefix')
    query = 'DELETE FROM model_parts WHERE prefix = %s'
    values = [prefix]
    rows = execute_query(query, values)
    print(rows)
    message = 'Modelo deletado com sucesso'
    status_code = 200
    return make_response(
        jsonify(
            message=message,
            statusCode=status_code
        )
    )

# Rota para verificar um código de modelo
@app.route('/check-code/', methods=['GET'])
def check_code():
    serial_number = request.args.get('code')
    query = 'SELECT * FROM model_parts WHERE prefix = %s'
    values = [serial_number[:2],]
    data = execute_query(query, values)
    if data:
        return make_response(
            jsonify(
                message="Prefixo validado",
                statusCode=200
            )
        )
    else:
        query = 'INSERT INTO misplaced_parts (serial_number, model_prefix, datetime_verif, status) VALUES (%s, %s, NOW(), null'
        values = (serial_number[2:], serial_number[:2])
        execute_query(query, values)
        TG.send_misplaced_part(serial_number)
        return make_response(
            jsonify(
                message="Peça desviada",
                statusCode=501
            )
        )

# Rota para inserir uma nova peça da esteira
@app.route('/update-status', methods=['POST'])
def insert_new_part():
    part = request.json
    status = 'S' if part['status'] == 0 else 'N'
    query = "INSERT INTO parts (serial_number, model_prefix, status, datetime_verif) VALUES (upper(%s), upper(%s), upper(%s), NOW())"
    values = (part['codigo_de_barras'][2:], part['codigo_de_barras'][:2], status)
    result = execute_query(query, values)
    if result is not None:  # Verifica se a consulta foi bem-sucedida
        return make_response(
            jsonify(
                message="Peça cadastrada",
                statusCode=200
            )
        )
    else:
        return make_response(
            jsonify(
                message="Erro ao cadastrar a peça",
                statusCode=500
            )
        )

# Rota para validar uma peça
@app.route('/parts/validate', methods=['PUT'])
def validate_part():
    part = request.json
    values = None
    message = None
    if part['codeSupervisor'] is None:
        query = "UPDATE parts SET datetime_inspec = NOW(), status = %s, inspector = %s WHERE serial_number = %s"
        values = (part['situation'], part['codeInspector'], part['serie'][2:])
        message = "Inspeção registrada"
    else:
        query = "UPDATE parts SET datetime_valid = NOW(), validation = %s, supervisor = %s WHERE serial_number = %s"
        values = (part['finalCheck'], part['codeSupervisor'], part['serie'][2:])
        message = "Supervisão registrada"
    execute_query(query, values)
    if part['situation'] == 'N' and part['codeSupervisor'] is None:
        TG.send_denied_inspec(part['codeInspector'], part['inspector'], part['serie'])
    return make_response(
        jsonify(
            message=message,
            statusCode=200
        )
    )

# Rota para validar o login de um usuário
@app.route('/users/login', methods=['PUT'])
def verify_login():
    user = request.json
    query = "SELECT * FROM users WHERE code = %s"
    values = (user['code'],)
    user_db = execute_query(query, values)
    if not user_db:
        return make_response(
            jsonify(
                message='Usuário incorreto.',
                statusCode=400
            )
        )
    if user_db[0][3] not in ("Supervisor", "Inspetor"):
        return make_response(
            jsonify(
                message='Acesso ainda não liberado.',
                statusCode=400
            )
        )
    if user_db[0][2] != hashlib.sha256((user['password']).encode('utf-8')).hexdigest():
        return make_response(
            jsonify(
                message='Senha incorreta.',
                statusCode=400
            )
        )
    user_json = {
        "code": user_db[0][0],
        "name": user_db[0][1],
        "role": user_db[0][3]
    }
    return make_response(
        jsonify(
            info=user_json,
            statusCode=200
        )
    )

# Rota para verificar o código de um usuário
@app.route('/users/verify-user-code', methods=['GET'])
def verify_user_code():
    code = request.args.get('code')
    query = "SELECT * FROM users WHERE code = %s"
    values = (code,)
    user_db = execute_query(query, values)
    if len(user_db) == 0:
        return make_response(
            jsonify(
                message='Código ainda não cadastrado no banco de dados.',
                info=code,
                statusCode=400
            )
        )
    else:
        user_json = {
            "code": user_db[0][0],
            "name": user_db[0][1],
            "access": user_db[0][3]
        }
        return make_response(
            jsonify(
                info=user_json,
                statusCode=200
            )
        )

# Rota para alterar a permissão de um usuário
@app.route('/users/permission', methods=['PUT'])
def alter_permission():
    user = request.json
    query = "UPDATE users SET permission = %s WHERE code = %s"
    values = (user['permission'], user['code'])
    execute_query(query, values)
    return make_response(
        jsonify(
            message='Permissão alterada',
            statusCode=200
        )
    )

# Rota para alterar a senha de um usuário (envia mensagem pelo bot)
@app.route('/users/forgot-password/', methods=['GET'])
def send_message_password():
    user_code = request.args.get('code')
    user_db = execute_query("SELECT * FROM users WHERE code = %s", [user_code])
    if user_db:
        TG.send_password_message(user_db[0][4], user_code)
        message = 'Procedimento enviado no seu Telegram'
        status_code = 200
    else:
        message = 'Matrícula não encontrada'
        status_code = 500
    return make_response(
        jsonify(
            message=message,
            statusCode=status_code
        )
    )

# Função para alterar senha de um usuário
@app.route('/users/change-password', methods=['PUT'])
def change_password(password=None, code=None):
    if password and code:
        password = hashlib.sha256((password).encode('utf-8')).hexdigest()
        values = (password, code)
    else:
        user = request.json
        user['password'] = hashlib.sha256((user['password']).encode('utf-8')).hexdigest()
        values = (user['password'], user['code'])
    query = "UPDATE users SET password = %s WHERE code = %s"
    execute_query(query, values)
    if not (password and code):
        return make_response(
            jsonify(
                message="Senha alterada",
                statusCode=200
            )
        )

#Rota para listar peças extraviadas
@app.route('/parts/misplaced', methods=['GET'])
def get_misplaced_parts():
    query = "SELECT * FROM misplaced_parts WHERE status IN ('S', 'N')"
    parts_db = execute_query(query)
    if parts_db:
        list_parts = []
        for part in parts_db:
            serial_number = part[1] + str(part[0])
            data_hora = str(part[3])
            part_info = {
                'serial_number': serial_number,
                'status': part[2],
                'datetime_verif': data_hora
            }
            list_parts.append(part_info)
        return make_response(
            jsonify(
                info=list_parts,
                statusCode=200
            )
        )
    else:
        return make_response(
            jsonify(
                statusCode=500
            )
        )

#Rota para aprovar/reprovar peça extraviada
@app.route('/parts/misplaced/action', methods=['POST'])
def validate_misplaced_part():
    part = request.json
    if part['action'] == 'disapproved':
        query = "UPDATE misplaced_parts SET status = 'Extraviado' WHERE serial_number = %s"
        values = (part['serial_number'][2:])
        execute_query(query, values)
        return make_response(
            jsonify(
                message='Peça revogada',
                statusCode=200
            )
        )
    else:
        save_model(part['serial_number'][:2], part['model'])
        query = "DELETE FROM misplaced_parts WHERE model_prefix = %s"
        values = (part['serial_number'][:2])
        execute_query(query, values)
        return make_response(
            jsonify(
                message= 'Prefixo cadastrado e peça aprovada para inspeção',
                statusCode=200
            )
        )

# Rota para contabilizar peças aprovadas e reprovadas
@app.route('/parts/count', methods=['GET'])
def count_parts():
    values = None
    initial_date = request.args.get('initialDate')
    final_date = request.args.get('finalDate')
    query = """
        SELECT 
            m.prefix,
            SUM(p.validation = 'S') AS aprovados,
            SUM(p.validation = 'N') AS reprovados
        FROM model_parts m
        LEFT JOIN parts p ON m.prefix = p.model_prefix
    """
    query_misplaced_parts = "SELECT COUNT(*) FROM misplaced_parts"
    if initial_date and final_date:
        values = (initial_date + " 00:00:00", final_date + " 23:59:59")
        query += " WHERE datetime_valid >= %s AND datetime_valid <= %s"
        query_misplaced_parts += " WHERE datetime_verif >= %s AND datetime_verif <= %s AND status IN ('Aprovado', 'Reprovado')"
    query += " GROUP BY m.prefix WITH ROLLUP"
    misplaced_parts = execute_query(query_misplaced_parts)
    results = execute_query(query, values)
    if not results:
        return make_response(
            jsonify(
                message="Nenhuma peça no período informado",
                statusCode=404
            )
        )
    else:
        response = {
            "column": [
                {
                    "prefixo": prefix,
                    "aprovados": aprovados,
                    "reprovados": reprovados
                }
                for prefix, aprovados, reprovados in results
                if prefix is not None
            ],
            "pizza": [
                {
                    "aprovados": results[-1][1] if results and results[-1][1] is not None else 0,
                    "reprovados": results[-1][2] if results and results[-1][2] is not None else 0,
                    "extraviados": str(misplaced_parts[0][0]) if misplaced_parts else 0
                }
            ]
        }
        return make_response(
            jsonify(
                info=response,
                statusCode=200
            )
        )



if __name__ == '__main__':
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000}).start()
    threading.Thread(target=TG.run_telegram_bot).start()
