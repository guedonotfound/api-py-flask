import mysql.connector
from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
import hashlib
import re


mydb = mysql.connector.connect(
    host='containers-us-west-27.railway.app',
    port=5883,
    user='root',
    password='DeqoFQzH6cjAb63vfoCa',
    database='railway',
)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app, resources={r"/*": {"origins": "*"}})

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
                'id': user[0],
                'code': user[1],
                'name': user[2],
                'password': user[3],
                'role': user[4]
            }
        )

    return make_response(
        jsonify(
            info=list_users,
            statusCode=200
        )
    )

## LISTA CARGOS
@app.route('/roles', methods=['GET'])
def get_roles():
    mycursor = mydb.cursor()
    query = "SELECT * FROM roles"
    mycursor.execute(query)
    roles_db = mycursor.fetchall()

    list_roles = list()
    for role in roles_db:
        list_roles.append(
            {
                'id': role[0],
                'description': role[1]
            }
        )

    return make_response(
        jsonify(
            info=list_roles,
            statusCode=200
        )
    )

## LISTA PEÇAS
@app.route('/parts', methods=['GET'])
def get_parts():
    mycursor = mydb.cursor()
    query = "SELECT * FROM parts"
    mycursor.execute(query)
    parts_db = mycursor.fetchall()

    list_parts = list()
    for role in parts_db:
        list_parts.append(
            {
                'id': role[0],
                'description': role[1]
            }
        )

    return make_response(
        jsonify(
            info=list_parts,
            statusCode=200
        )
    )

## VALIDA PEÇAS
@app.route('/parts/validate', methods=['PUT'])
def validate_part():
    part = request.json
    mycursor = mydb.cursor()
    if part['supervisor'] == "Y":
        query = "UPDATE parts SET validation_date = %s AND validation = '%s' AND supervisor = '%s'"
        values = (part['validation_date'], part['validation'], part['supervisor'])
        mycursor.execute(query, values)
        mydb.commit()
        return make_response(
            jsonify(
                info=part,
                statusCode=200
            )
        )
    else:
        query = "UPDATE parts SET inspection_date = %s AND inspection = '%s' AND inspector = '%s'"
        values = (part['inspection_date'], part['inspection'], part['inspector'])
        mycursor.execute(query, values)
        mydb.commit()
        return make_response(
            jsonify(
                info=part,
                statusCode=200
            )
        )


## VALIDA LOGIN
@app.route('/users/login', methods=['POST'])
def verify_login():
    user = request.json
    user['password'] = hashlib.sha256(
        (user['password']).encode('utf-8')).hexdigest()
    mycursor = mydb.cursor()
    query = "SELECT * FROM users WHERE code = %s"
    values = (user['code'],)
    mycursor.execute(query, values)
    user_db = mycursor.fetchall()
    if len(user_db) != 0:
        if user_db[0][5] == "S":
            if user_db[0][3] == user['password']:
                user_json = {
                    "id": user_db[0][0],
                    "code": user_db[0][1],
                    "name": user_db[0][2],
                    "role": user_db[0][4]
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
            "code": user_db[0][1],
            "name": user_db[0][2],
            "access": user_db[0][5]
        }
        return make_response(
            jsonify(
                info=user_json,
                statusCode=200
            )
        )

## LIBERA USUÁRIO (VERIFICA SENHA)
@app.route('/users/verify-password', methods=['GET'])
def verify_password():
    password = request.args.get('password')
    if len(password) <= 32 or len(password) >= 8:
        if not (re.search(r'.{8,}', password) and
                re.search(r'[A-Z]', password) and
                re.search(r'\d', password) and
                re.search(r'[!@#$%^&*]', password)):
            return make_response(
                jsonify(
                    message='Senha precisa ter pelo menos um número, ' + 
                        'um caracter especial, uma letra maiúscula e uma minúscula.',
                    statusCode=400
                )
            )
        else:
            return make_response(
                jsonify(
                    info=password,
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

## LIBERA USUÁRIO (LIBERA/REVOGA ACESSO)
@app.route('/users/validate', methods=['PUT'])
def validate_user():
    user = request.json
    mycursor = mydb.cursor()
    user['password'] = hashlib.sha256(
        (user['password']).encode('utf-8')).hexdigest()
    if user['access'] == "S":
        query = "UPDATE users SET access = %s AND password = %s WHERE code = %s"
        values = ('S', user['password'], user['code'])
        mycursor.execute(query, values)
        mydb.commit()
        return make_response(
            jsonify(
                message='Acesso liberado.',
                info=user,
                statusCode=200
            )
        )

    else:
        return make_response(
            jsonify(
                message='Acesso não liberado.',
                statusCode=400
            )
        )

## REMOVE ACESSO
@app.route('/users/remove-access', methods=['PUT'])
def remove_access():
    user = request.json
    mycursor = mydb.cursor()
    query = "UPDATE users SET access = %s WHERE code = %s"
    values = ('N', user['code'])
    mycursor.execute(query, values)
    mydb.commit()
    return make_response(
        jsonify(
            message='Acesso removido.',
            info=user,
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

##VERIFICA PEÇA##
@app.route('/parts/verify-prefix', methods=['GET'])
def verify_part_code():
    prefix = request.args.get('prefix')
    mycursor = mydb.cursor()
    query = "SELECT * FROM model_parts WHERE prefix = %s"
    values = (prefix,)
    mycursor.execute(query, values)
    prefix_db = mycursor.fetchall()
    if len(prefix_db) == 0:
        make_response(
            jsonify(
                message = "Modelo não cadastrado",
                statusCode = 400
            )
        )
    else:
        make_response(
            jsonify(
                info = prefix,
                statusCode = 200
            )
        )

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
##app.run(host='0.0.0.0', port=5000)
