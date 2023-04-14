import mysql.connector
from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
import re
import json


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

## LISTA USUÁRIOS##


@app.route('/usuarios', methods=['GET'])
def get_users():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM usuarios")
    usuarios_bd = mycursor.fetchall()
    mycursor.close()
    lista_usuarios = list()
    for usuario in usuarios_bd:
        lista_usuarios.append(
            {
                'id': usuario[0],
                'code': usuario[1],
                'name': usuario[2],
                'password': usuario[3],
                'role': usuario[4]
            }
        )

    return make_response(
        jsonify(
            info=lista_usuarios,
            statusCode=200
        )
    )

## LISTA CARGOS##


@app.route('/cargos', methods=['GET'])
def get_cargos():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cargos")
    cargos_bd = mycursor.fetchall()

    lista_cargos = list()
    for cargo in cargos_bd:
        lista_cargos.append(
            {
                'id': cargo[0],
                'description': cargo[1]
            }
        )

    return make_response(
        jsonify(
            info=lista_cargos,
            statusCode=200
        )
    )

## VALIDA LOGIN##


@app.route('/usuarios/login', methods=['POST'])
def verifica_login():
    user = request.json
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT * FROM usuarios WHERE codigo = '{user['code']}'")
    usuario = mycursor.fetchall()
    if len(usuario) != 0:
        if usuario[0][3] == user['password']:
            user_json = {
                "id": usuario[0][0],
                "code": usuario[0][1],
                "name": usuario[0][2],
                "password": usuario[0][3],
                "role": usuario[0][4]
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
                    message="Senha incorreta",
                    statusCode=400
                )
            )
    else:
        return make_response(
            jsonify(
                message="Usuário incorreto",
                statusCode=400
            )
        )

## CRIA USUÁRIO##


@app.route('/usuarios/novo', methods=['POST'])
def create_user():
    user = request.json
    user['name'] = user['name'].upper()
    mycursor = mydb.cursor()
    query = "SELECT * FROM usuarios WHERE codigo = %s"
    values = (user['code'])
    mycursor.execute(query, values)
    user_bd = mycursor.fetchall()
    a = int(len(user['password']))
    print(len(user['password']))

    if len(user_bd) != 0:
        return make_response(
            jsonify(
                message="Já existe usuário com esse código",
                statusCode=400
            )
        )
    elif int(len(user['password'])) > 16 or int(len(user['password'])) < 8:
        return make_response(
            jsonify(
                message='Senha precisa ter entre 8 e 16 caracteres.',
                statusCode=400
            )
        )
    elif not (re.search(r'.{8,}', user['password']) and
              re.search(r'[A-Z]', user['password']) and
              re.search(r'\d', user['password']) and
              re.search(r'[!@#$%^&*]', user['password'])):
        return make_response(
            jsonify(
                message=
                    'Senha precisa ter pelo menos um número, uma letra maiúscula, uma letra minúscula e um caracter especial.',
                statusCode=400
            )
        )
    else:
        query = "INSERT INTO usuarios (codigo, nome, senha, cargo) VALUES (%s, %s, %s, %s)"
        values = (user['code'], user['name'], user['password'], user['role'])
        mycursor.execute(query, values)
        mydb.commit()
        return make_response(
            jsonify(
                message='Usuário cadastrado com sucesso.',
                info=user,
                statusCode=200
            )
        )

## CRIA CARGO##


@app.route('/cargos/novo', methods=['POST'])
def create_cargo():
    cargo = request.json
    cargo['description'] = cargo['description'].upper()
    mycursor = mydb.cursor()
    query = "SELECT * FROM cargos WHERE descricao = %s"
    values = (cargo['description'],)
    mycursor.execute(query, values)
    cargo_bd = mycursor.fetchall()
    if len(cargo_bd) != 0:
        return make_response(
            jsonify(
                message="Já existe cargo com essa descrição",
                statusCode=400
            )
        )

    else:
        query = "INSERT INTO cargos (descricao) VALUES (%s)"
        values = (cargo['description'])
        mycursor.execute(query, values)
        mydb.commit()
        return make_response(
            jsonify(
                message='Cargo cadastrado com sucesso.',
                info=cargo,
                statusCode=200
            )
        )

## APAGA USUÁRIO##


@app.route('/usuarios/delete', methods=['DELETE'])
def delete_user():
    user = request.json
    mycursor = mydb.cursor()
    query = "SELECT * INTO usuarios WHERE codigo = %s"
    values = (user['code'],)
    mycursor.execute(query, values)
    user_bd = mycursor.fetchall
    if user_bd[0][1] == user['code']:
        query = "DELETE FROM usuarios WHERE id = %s"
        values = user['id']
        mycursor.execute(query, values)
        mydb.commit()
        return make_response(
            jsonify(
                mensagem='Usuário deletado com sucesso.',
                info=user_bd,
                statusCode=200
            )
        )
    else:
        return make_response(
            jsonify(
                mensagem='Não existe usuário com esse código.',
                statusCode=400
            )
        )

## APAGA CARGO##


@app.route('/cargos/delete', methods=['DELETE'])
def delete_cargo():
    cargo = request.json
    mycursor = mydb.cursor()
    query = f"SELECT * FROM cargos WHERE descricao = '{cargo['description']}'"
    values = (cargo['description'],)
    mycursor.execute(query)
    cargo_bd = mycursor.fetchall()
    query = "SELECT * FROM usuarios WHERE cargo = %s"
    values = (cargo_bd[0][0])
    mycursor.execute(query, values)
    user_bd = mycursor.fetchall()
    if int(len(cargo_bd)) != 0:
        if int(len(user_bd)) != 0:
            return make_response(
                jsonify(
                    mensagem='Não é possível apagar o cargo pois possuem usuários vinculados a ele',
                    info=user_bd,
                    statusCode=400
                )
            )

        else:
            query = "DELETE FROM cargos WHERE id = %s"
            values = cargo_bd[0][0]
            mycursor.execute(query, values)
            mydb.commit()
            return make_response(
                jsonify(
                    mensagem='Cargo deletado com sucesso.',
                    info=cargo_bd,
                    statusCode=200
                )

            )
    else:
        return make_response(
            jsonify(
                mensagem='Não existe cargo com essa descrição.',
                statusCode=400
            )
        )


app.run(host='0.0.0.0', port=5000)
