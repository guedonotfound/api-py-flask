import mysql.connector
import datetime
from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
import hashlib
import re


'''mydb = mysql.connector.connect(
    host='containers-us-west-27.railway.app',
    port=5883,
    user='root',
    password='DeqoFQzH6cjAb63vfoCa',
    database='railway',
)'''

mydb = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='root',
    database='bdteste',
)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers = ["Content-Type"])

## LISTA USUÁRIOS
@app.route('/users', methods=['GET'])
def get_users():
    mycursor = mydb.cursor()
    query = "SELECT * FROM users"
    mycursor.execute(query)
    users_db = mycursor.fetchall()
    mycursor.close()
    list_users = list()
    for user in users_db:
        list_users.append(
            {
                'code': user[0],
                'name': user[1],
                'permission': user[3]
            }
        )

    return make_response(
        jsonify(
            info=list_users,
            statusCode=200
        )
    )

## LISTA UM USUÁRIO
@app.route('/user/', methods=['GET'])
def get_one_user():
    code = request.args.get('code')
    mycursor = mydb.cursor()
    query = "SELECT * FROM users WHERE code = %s"
    values = [code,]
    mycursor.execute(query, values)
    users_db = mycursor.fetchall()
    mycursor.close()
    for user in users_db:
        list_user = {
                'code': user[0],
                'name': user[1],
                'permission': user[3]
            }

    return make_response(
        jsonify(
            info=list_user,
            statusCode=200
        )
    )

## LISTA PEÇAS
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
        if part[5] != None:
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

## LISTA UMA PEÇA
@app.route('/part/', methods=['GET'])
def get_one_part():
    serial_number = request.args.get('serial_number')
    mycursor = mydb.cursor()
    query = "SELECT * FROM parts p, model_parts m WHERE p.model_prefix = m.prefix and serial_number = %s"
    values = [serial_number[2:5],]
    mycursor.execute(query, values)
    part_db = mycursor.fetchall()
    if part_db[0][5] != None:
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

## LISTA MODEL
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

## INSERE MODEL
@app.route('/model/save', methods=['POST'])
def delete_model():
    model = request.json
    mycursor = mydb.cursor()
    query = 'SELECT * FROM model_parts WHERE prefix = %s OR model = %s'
    values = [model['prefix'],model['model']]
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

## DELETA MODEL
@app.route('/delete-model/', methods=['DELETE'])
def new_model():
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

## VALIDA MODEL
@app.route('/check-code/', methods=['GET'])
def validate_model():
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
                statusCode = 501
            )
        )
    else:
        return make_response(
            jsonify(
                message="Prefixo não validado",
                statusCode=500
            )
        )


## VALIDA PEÇA
@app.route('/parts/validate', methods=['PUT'])
def validate_part():
    part = request.json
    mycursor = mydb.cursor()
    if part['codeSupervisor'] == None:
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


## VALIDA LOGIN
@app.route('/users/login', methods=['POST'])
def verify_login():
    user = request.json
    ##user['password'] = hashlib.sha256((user['password']).encode('utf-8')).hexdigest()
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

## LIBERA USUÁRIO (VERIFICA CÓDIGO)
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

## ALTERA PERMISSÃO
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

## ALTERAR SENHA
@app.route('/users/change-password', methods=['PUT'])
def change_password():
    user = request.json
    mycursor = mydb.cursor()
    if len(user['password']) <= 32 or len(user['password']) >= 8:    
        if not (re.search(r'.{8,}', user['password']) and
                re.search(r'[A-Z]', user['password']) and
                re.search(r'\d', user['password']) and
                re.search(r'[!@#$%^&*]', user['password'])):
            return make_response(
                jsonify(
                    message='Senha precisa ter pelo menos um número, ' + 
                        'um caracter especial, uma letra maiúscula e uma minúscula.',
                    statusCode=400
                )
            )
        else:
            user['password'] = hashlib.sha256(
            (user['password']).encode('utf-8')).hexdigest()
            query = "UPDATE users SET password = %s WHERE code = %s"
            values = (user['password'], user['code'])
            mycursor.execute(query, values)
            mydb.commit()
            return make_response(
                jsonify(
                    message = 'Senha alterada com sucesso',
                    statusCode=200
                )
            )
    else:
        return make_response(
            jsonify(
                message='Senha precisa ter entre 8 e 32 caracteres.',
                statusCode=400
            )
        )

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
##app.run(host='0.0.0.0', port=5000)
