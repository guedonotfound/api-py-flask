import mysql.connector
import datetime
from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
import hashlib
import threading
import TelegramAPI as TG

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type"])
flask_initialized = False
telegram_bot_initialized = False

# Configurações de conexão com o banco de dados
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'bdteste',
}

mydb = mysql.connector.connect(**db_config)

def execute_query(query, values=None):
    mycursor = mydb.cursor()
    if values:
        mycursor.execute(query, values)
    else:
        mycursor.execute(query)
    return mycursor.fetchall()

def serialize_user(user):
    return {
        'code': user[0],
        'name': user[1],
        'permission': user[3]
    }

# Rota para listar usuários
@app.route('/users', methods=['GET'])
def get_users():
    query = "SELECT * FROM users"
    users_db = execute_query(query)
    list_users = [serialize_user(user) for user in users_db]
    return make_response(
        jsonify(
            info=list_users,
            statusCode=200
        )
    )

# Rota para listar um usuário
@app.route('/user/', methods=['GET'])
def get_one_user():
    code = request.args.get('code')
    query = "SELECT * FROM users WHERE code = %s"
    values = [code]
    user_db = execute_query(query, values)
    list_user = serialize_user(user_db[0]) if user_db else {}
    return make_response(
        jsonify(
            info=list_user,
            statusCode=200
        )
    )

# Rota para listar peças
@app.route('/parts/', methods=['GET'])
def get_parts():
    role = request.args.get('role')
    mycursor = mydb.cursor()
    if role == "Inspetor":
        query = "SELECT * FROM parts WHERE validation is null and inspector is null"
    else:
        query = "SELECT * FROM parts WHERE validation is null and inspector is not null"
    mycursor.execute(query)
    parts_db = mycursor.fetchall()
    list_parts = list()
    for part in parts_db:
        query = "SELECT model FROM model_parts WHERE prefix = %s"
        values = [part[1],]
        mycursor.execute(query, values)
        model = mycursor.fetchall()
        serial_number = part[1] + str(part[0])
        data_hora = str(part[3])
        if part[5] is not None:
            query = "SELECT name FROM users WHERE code = %s"
            values = [part[5],]
            mycursor.execute(query, values)
            inspector = mycursor.fetchall()
            list_parts.append(
                {
                    'serial_number': serial_number,
                    'model': model,
                    'status': part[2],
                    'datetime_verif': data_hora,
                    'inspector': inspector
                }
            )
        else:
            list_parts.append(
                {
                    'serial_number': serial_number,
                    'model': model,
                    'status': part[2],
                    'datetime_verif': data_hora,
                    'inspector': None
                }
            )

    return make_response(
        jsonify(
            info=list_parts,
            statusCode=200
        )
    )

# Rota para listar uma peça
@app.route('/part/', methods=['GET'])
def get_one_part():
    serial_number = request.args.get('serial_number')
    mycursor = mydb.cursor()
    query = "SELECT * FROM parts p, model_parts m WHERE p.model_prefix = m.prefix and serial_number = %s"
    values = [serial_number[2:5],]
    mycursor.execute(query, values)
    part_db = mycursor.fetchall()
    if part_db[0][5] is not None:
        query = "SELECT * FROM parts p, model_parts m, users u WHERE p.model_prefix = m.prefix AND serial_number = %s AND u.code = %s"
        values = [serial_number[2:], part_db[0][5]]
        mycursor.execute(query, values)
        part_db = mycursor.fetchall()
        for part in part_db:
            serial_number = part[1] + str(part[0])
            data_hora = str(part[3])
            list_part = {
                    'serie': serial_number,
                    'model': part[10],
                    'situation': part[2],
                    'date': data_hora,
                    'codeInspector': part[5],
                    'codeSupervisor': part[6],
                    'finalCheck': part[7],
                    'inspector': part[12],
                    'supervisor': None
                }
        return make_response(
            jsonify(
                info=list_part,
                statusCode=200
            )
        )
    else:
        for part in part_db:
            serial_number = part[1] + str(part[0])
            data_hora = str(part[3])
            list_part = {
                    'serie': serial_number,
                    'model': part[10],
                    'situation': part[2],
                    'date': data_hora,
                    'codeInspector': part[5],
                    'codeSupervisor': part[6],
                    'finalCheck': part[7],
                    'inspector': None,
                    'supervisor': None
                }
        return make_response(
            jsonify(
                info=list_part,
                statusCode=200
            )
        )

# Rota para listar modelos de peças
@app.route('/model-parts', methods=['GET'])
def get_models():
    mycursor = mydb.cursor()
    query = "SELECT * FROM model_parts"
    mycursor.execute(query)
    models_db = mycursor.fetchall()

    list_models = list()
    for model in models_db:
        list_models.append(
            {
                'prefix': model[0],
                'model': model[1]
            }
        )

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
    mycursor = mydb.cursor()
    query = 'SELECT * FROM model_parts WHERE prefix = %s OR model = %s'
    values = [model['prefix'], model['model']]
    mycursor.execute(query, values)
    model_db = mycursor.fetchall()
    if len(model_db) == 1:
        return make_response(
            jsonify(
                message='Prefixo ou modelo já cadastrado',
                statusCode=500
            )
        )
    else:
        query = 'INSERT INTO model_parts(prefix, model) VALUES(upper(%s), upper(%s))'
        values = [model['prefix'], model['model']]
        mycursor.execute(query, values)
        mydb.commit()
        return make_response(
            jsonify(
                message='Modelo cadastrado com sucesso',
                statusCode=200
            )
        )

# Rota para deletar um modelo de peça
@app.route('/delete-model/', methods=['DELETE'])
def delete_model():
    prefix = request.args.get('prefix')
    mycursor = mydb.cursor()
    query = 'DELETE FROM model_parts WHERE prefix = %s'
    values = [prefix,]
    mycursor.execute(query, values)
    mydb.commit()
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
    mycursor = mydb.cursor()
    query = 'SELECT * FROM model_parts WHERE prefix = %s'
    values = [prefix[0:2],]
    mycursor.execute(query, values)
    model_bd = mycursor.fetchall()
    if len(model_bd) == 1:
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
    mycursor = mydb.cursor()
    if part['codeSupervisor'] is None:
        query = "UPDATE parts SET datetime_inspec = %s, status = %s, inspector = %s WHERE serial_number = %s"
        values = (str(datetime.datetime.now())[:19], part['situation'], part['codeInspector'], part['serie'][2:])
        mycursor.execute(query, values)
        mydb.commit()
        return make_response(
            jsonify(
                message="Inspeção registrada",
                statusCode=200
            )
        )
    else:
        query = "UPDATE parts SET datetime_valid = %s, validation = %s, supervisor = %s WHERE serial_number = %s"
        values = (str(datetime.datetime.now())[:19], part['finalCheck'], part['codeSupervisor'], part['serie'][2:])
        mycursor.execute(query, values)
        mydb.commit()
        return make_response(
            jsonify(
                message="Supervisão registrada",
                statusCode=200
            )
        )

# Rota para validar o login de um usuário
@app.route('/users/login', methods=['POST'])
def verify_login():
    user = request.json
    mycursor = mydb.cursor()
    query = "SELECT * FROM users WHERE code = %s"
    values = (user['code'],)
    mycursor.execute(query, values)
    user_db = mycursor.fetchall()
    if len(user_db) != 0:
        if user_db[0][3] == "Supervisor" or user_db[0][3] == "Inspetor":
            if user_db[0][2] == user['password']:
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
            else:
                return make_response(
                    jsonify(
                        message='Senha incorreta.',
                        statusCode=400
                    )
                )
        else:
            return make_response(
                jsonify(
                    message='Acesso ainda não liberado.',
                    statusCode=400
                )
            )
    else:
        return make_response(
            jsonify(
                message='Usuário incorreto.',
                statusCode=400
            )
        )

# Rota para verificar o código de um usuário
@app.route('/users/verify-user-code', methods=['GET'])
def verify_user_code():
    code = request.args.get('code')
    mycursor = mydb.cursor()
    query = "SELECT * FROM users WHERE code = %s"
    values = (code,)
    mycursor.execute(query, values)
    user_db = mycursor.fetchall()
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
    mycursor = mydb.cursor()
    query = "UPDATE users SET permission = %s WHERE code = %s"
    values = (user['permission'], user['code'])
    mycursor.execute(query, values)
    mydb.commit()
    return make_response(
        jsonify(
            message='Permissão alterada',
            statusCode=200
        )
    )

# Rota para alterar a senha de um usuário
@app.route('/users/change-password', methods=['PUT'])
def change_password():
    user = request.json
    mycursor = mydb.cursor()
    user['password'] = hashlib.sha256((user['password']).encode('utf-8')).hexdigest()
    query = "UPDATE users SET password = %s WHERE code = %s"
    values = (user['password'], user['code'])
    mycursor.execute(query, values)
    mydb.commit()
    return make_response(
        jsonify(
            message='Senha alterada com sucesso',
            statusCode=200
        )
    )

def main():
    global flask_initialized

    if not flask_initialized:
        flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
        flask_thread.start()
        flask_initialized = True

    telegram_thread = threading.Thread(target=TG.run_telegram_bot)
    telegram_thread.start()

if __name__ == '__main__':
    main()