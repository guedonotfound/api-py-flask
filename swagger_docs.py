USERS_ROUTE_DOCS = {
    'tags': ['users'],
    'description': 'Get all users or one user if parameter is given',
    'parameters': [
        {
            'name': 'code',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'User code (optional)'
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'info': {'$ref': '#/definitions/User'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    },
    'definitions': {
        'User': {
            'type': 'object',
            'properties': {
                'code': {'type': 'string'},
                'name': {'type': 'string'},
                'permission': {'type': 'string'}
                # Adicione outras propriedades do usuário conforme necessário
            }
        }
    }
}

VERIFY_USER_CODE_ROUTE_DOCS = {
    'tags': ['users'],
    'description': 'Verify if a user code exists in the database',
    'parameters': [
        {
            'name': 'code',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Code of the user to be verified'
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'info': {'$ref': '#/definitions/UserVerification'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        },
        '400': {
            'description': 'User code not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'info': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    },
    'definitions': {
        'UserVerification': {
            'type': 'object',
            'properties': {
                'code': {'type': 'string'},
                'name': {'type': 'string'},
                'access': {'type': 'string'}
            }
        }
    }
}

SEND_MESSAGE_PASSWORD_ROUTE_DOCS = {
    'tags': ['users'],
    'description': 'Send a password recovery message to the user via Telegram',
    'parameters': [
        {
            'name': 'code',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'User code for password recovery'
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        },
        '500': {
            'description': 'User code not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    }
}

VERIFY_LOGIN_ROUTE_DOCS = {
    'tags': ['users'],
    'description': 'Verify user login credentials',
    'parameters': [
        {
            'name': 'user',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'example': {
                    'code': '123',
                    'password': 'senha123'
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'info': {'$ref': '#/definitions/User'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        },
        '400': {
            'description': 'Invalid user credentials',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    },
    'definitions': {
        'User': {
            'type': 'object',
            'properties': {
                'code': {'type': 'string'},
                'name': {'type': 'string'},
                'role': {'type': 'string'}
            }
        }
    }
}

CHANGE_PASSWORD_ROUTE_DOCS = {
    'tags': ['users'],
    'description': 'Change user password',
    'parameters': [
        {
            'name': 'user',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'example': {
                    'code': '123',
                    'password': 'nova_senha'
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    }
}

ALTER_PERMISSION_ROUTE_DOCS = {
    'tags': ['users'],
    'description': 'Alter user permission',
    'parameters': [
        {
            'name': 'user',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string'},
                    'permission': {'type': 'string'}
                },
                'example': {
                    'code': '123',
                    'permission': 'Admin'
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    }
}

PARTS_ROUTE_DOCS = {
    'tags': ['parts'],
    'description': 'Get all parts or one part (if parameter is given)',
    'parameters': [
        {
            'name': 'serial_number',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Serial number of the part (optional)'
        },
        {
            'name': 'role',
            'in': 'query',
            'type': 'string',
            'required': False,
            'enum': ['Inspetor', 'Supervisor'],
            'description': 'Role of the employee to list parts that need inspection (optional)'
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'info': {'$ref': '#/definitions/Part'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    },
    'definitions': {
        'Part': {
            'type': 'object',
            'properties': {
                'serie': {'type': 'string'},
                'model': {'type': 'string'},
                'situation': {'type': 'string'},
                'date': {'type': 'string'},
                'codeInspector': {'type': 'string'},
                'codeSupervisor': {'type': 'string'},
                'finalCheck': {'type': 'string'},
                'inspector': {'type': ['string', 'null']}
            }
        }
    }
}

CHECK_CODE_ROUTE_DOCS = {
    'tags': ['parts'],
    'description': 'Check the validity of a code',
    'parameters': [
        {
            'name': 'code',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Code of the part to be checked'
        }
    ],
    'responses': {
        '200': {
            'description': 'Valid code',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        },
        '501': {
            'description': 'Invalid code',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    }
}

GET_MISPLACED_PARTS_ROUTE_DOCS = {
    'tags': ['parts'],
    'description': 'Get information about misplaced parts',
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'info': {'$ref': '#/definitions/MisplacedPart'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        },
        '500': {
            'description': 'No misplaced parts found',
            'schema': {
                'type': 'object',
                'properties': {
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    },
    'definitions': {
        'MisplacedPart': {
            'type': 'object',
            'properties': {
                'serial_number': {'type': 'string'},
                'status': {'type': 'string'},
                'datetime_verif': {'type': 'string'}
            }
        }
    }
}

COUNT_PARTS_ROUTE_DOCS = {
    'tags': ['parts'],
    'description': 'Count the number of approved, disapproved, and misplaced parts',
    'parameters': [
        {
            'name': 'initialDate',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Initial date for filtering parts (optional)'
        },
        {
            'name': 'finalDate',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Final date for filtering parts (optional)'
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'info': {'$ref': '#/definitions/PartsCount'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        },
        '404': {
            'description': 'No parts found in the specified period',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    },
    'definitions': {
        'PartsCount': {
            'type': 'object',
            'properties': {
                'column': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'prefixo': {'type': 'string'},
                            'aprovados': {'type': 'integer'},
                            'reprovados': {'type': 'integer'}
                        }
                    }
                },
                'pizza': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'aprovados': {'type': 'integer'},
                            'reprovados': {'type': 'integer'},
                            'extraviados': {'type': 'integer'}
                        }
                    }
                }
            }
        }
    }
}

UPDATE_STATUS_ROUTE_DOCS = {
    'tags': ['parts'],
    'description': 'Update the status of a part',
    'parameters': [
        {
            'name': 'codigo_de_barras',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'codigo_de_barras': {'type': 'string'},
                    'status': {'type': 'integer'}
                },
                'example': {
                    'codigo_de_barras': '123456',
                    'status': 0
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        },
        '500': {
            'description': 'Error',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    }
}

VALIDATE_MISPLACED_PART_ROUTE_DOCS = {
    'tags': ['parts'],
    'description': 'Validate or disapprove a misplaced part',
    'parameters': [
        {
            'name': 'part',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'serial_number': {'type': 'string'},
                    'model': {'type': 'string'},
                    'action': {'type': 'string', 'enum': ['approved', 'disapproved']}
                },
                'example': {
                    'serial_number': 'ABC123',
                    'model': 'MyModel',
                    'action': 'approved'
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    }
}

VALIDATE_PART_ROUTE_DOCS = {
    'tags': ['parts'],
    'description': 'Validate or inspect a part',
    'parameters': [
        {
            'name': 'part',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'serie': {'type': 'string'},
                    'situation': {'type': 'string'},
                    'codeInspector': {'type': 'string'},
                    'codeSupervisor': {'type': ['string', 'null']},
                    'finalCheck': {'type': 'string'},
                    'inspector': {'type': ['string', 'null']}
                },
                'example': {
                    'serie': '123456',
                    'situation': 'S',
                    'codeInspector': '123',
                    'codeSupervisor': '456',
                    'finalCheck': 'Aprovado',
                    'inspector': 'João'
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    }
}

MODEL_ROUTE_DOCS = {
    'tags': ['model'],
    'description': 'Get information about models of parts',
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'info': {'$ref': '#/definitions/ModelPart'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    },
    'definitions': {
        'ModelPart': {
            'type': 'object',
            'properties': {
                'prefix': {'type': 'string'},
                'model': {'type': 'string'}
            }
        }
    }
}

MODEL_SAVE_ROUTE_DOCS = {
    'tags': ['model'],
    'description': 'Save a new model',
    'parameters': [
        {
            'name': 'model',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'prefix': {'type': 'string'},
                    'model': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        },
        '500': {
            'description': 'Error',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    }
}

DELETE_MODEL_ROUTE_DOCS = {
    'tags': ['model'],
    'description': 'Delete a model by prefix',
    'parameters': [
        {
            'name': 'prefix',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Prefix of the model to be deleted'
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        },
        '500': {
            'description': 'Error',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'statusCode': {'type': 'integer', 'format': 'int32'}
                }
            }
        }
    }
}
