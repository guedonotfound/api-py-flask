import mysql.connector
from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
import hashlib
import threading
import TelegramAPI as TG

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type"])

# Configurações de conexão com o banco de dados
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'bdteste',
}

import mysql.connector

def execute_query(query, values=None):
    mydb = None
    result = None
    try:
        mydb = mysql.connector.connect(**db_config)
        mycursor = mydb.cursor()
        if values:
            mycursor.execute(query, values)
        else:
            mycursor.execute(query)
        if query.startswith(("INSERT", "UPDATE", "DELETE")):
            mydb.commit()
        else:
            result = mycursor.fetchall()
    except mysql.connector.Error as err:
        print("Erro na consulta ou conexão com o banco de dados:", err)
    finally:
        if mydb:
            mydb.close()
    return result


def serialize_user(user):
    return {
        'code': user[0],
        'name': user[1],
        'permission': user[3]
    }


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
    role = request.args.get('role')
    if serial_number:
        query = (
            "SELECT * FROM parts p "
            "JOIN model_parts m ON p.model_prefix = m.prefix "
            "LEFT JOIN users u ON p.inspector = u.code "
            "WHERE p.model_prefix = m.prefix AND p.serial_number = %s;"
        )
        values = [serial_number[2:5]]
    else:
        values = None
        if role == "Inspetor":
            query = (
                "SELECT p.*, m.model, u.name AS inspector_name "
                "FROM parts p "
                "JOIN model_parts m ON p.model_prefix = m.prefix "
                "LEFT JOIN users u ON p.inspector = u.code "
                "WHERE p.validation IS NULL AND p.inspector IS NULL;"
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
            serial_number = part[1] + str(part[0])
            data_hora = str(part[3])
            list_parts = {
                'serie': serial_number,
                'model': part[10],
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
                'model': part[10],
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
def save_model():
    model = request.json
    prefix, model_name = model['prefix'], model['model']
    query = 'INSERT INTO model_parts (prefix, model) VALUES (upper(%s), upper(%s))'
    values = (prefix, model_name)
    try:
        execute_query(query, values)
        return make_response(
            jsonify(
                message='Modelo cadastrado com sucesso',
                statusCode=200
            )
        )
    except:
        return make_response(
            jsonify(
                message='Prefixo ou modelo já cadastrado',
                statusCode=500
            )
        )


# Rota para deletar um modelo de peça
@app.route('/delete-model/', methods=['DELETE'])
def delete_model():
    prefix = request.args.get('prefix')
    query = 'DELETE FROM model_parts WHERE prefix = %s'
    values = [prefix]
    execute_query(query, values)
    return make_response(
        jsonify(
            message='Modelo deletado com sucesso',
            statusCode=200
        )
    )

# Rota para verificar um código de modelo
@app.route('/check-code/', methods=['GET'])
def check_code():
    prefix = request.args.get('code')
    query = 'SELECT COUNT(*) FROM model_parts WHERE prefix = %s'
    values = [prefix[0:2],]
    count = execute_query(query, values)
    if count == 1:
        return make_response(
            jsonify(
                message="Prefixo validado",
                statusCode=200
            )
        )
    elif prefix[0:2] == "CR":
        return make_response(
            jsonify(
                message="Peça desviada",
                statusCode=501
            )
        )
    else:
        return make_response(
            jsonify(
                message="Prefixo não validado",
                statusCode=500
            )
        )

# Rota para validar uma peça
@app.route('/parts/validate', methods=['PUT'])
def validate_part():
    part = request.json
    query_values = None
    message = None
    if part['codeSupervisor'] is None:
        query = "UPDATE parts SET datetime_inspec = NOW(), status = %s, inspector = %s WHERE serial_number = %s"
        query_values = (part['situation'], part['codeInspector'], part['serie'][2:])
        message = "Inspeção registrada"
    else:
        query = "UPDATE parts SET datetime_valid = NOW(), validation = %s, supervisor = %s WHERE serial_number = %s"
        query_values = (part['finalCheck'], part['codeSupervisor'], part['serie'][2:])
        message = "Supervisão registrada"
    execute_query(query, query_values)
    if part['situation'] == 'N' and part['codeSupervisor'] is None:
        TG.send_denied_inspection(part['codeInspector'], part['inspector'], part['serie'])
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
    
# Rota para contabilizar peças aprovadas e reprovadas
@app.route('/parts/count', methods=['GET'])
def count_parts():
    query = """
        SELECT m.prefix,
               SUM(p.validation = 'S') AS aprovados,
               SUM(p.validation = 'N') AS reprovados
          FROM model_parts m
               LEFT JOIN parts p ON m.prefix = p.model_prefix
      GROUP BY m.prefix
    """
    results = execute_query(query)
    response = [
        {
            "prefixo": prefix,
            "aprovados": aprovados,
            "reprovados": reprovados
        }
        for prefix, aprovados, reprovados in results
    ]
    return jsonify(results=response, statusCode=200)

if __name__ == '__main__':
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000}).start()
    threading.Thread(target=TG.run_telegram_bot).start()