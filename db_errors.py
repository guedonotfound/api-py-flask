# db_errors.py

class DBErrors:
    ERROR_MAP = {
        1048: "Erro ao adicionar ou atualizar o registro. Não é permitido valor nulo em uma coluna obrigatória.",
        1049: "Erro ao conectar ao banco de dados. O banco de dados especificado não existe.",
        1050: "Erro ao criar a tabela. A tabela especificada já existe no banco de dados.",
        1051: "Erro ao executar a operação. A tabela especificada não existe no banco de dados.",
        1054: "Erro ao executar a operação. Alguma coluna referenciada não existe.",
        1060: "Erro ao criar a tabela. Nome duplicado encontrado para uma coluna.",
        1062: "Erro ao adicionar ou atualizar o registro. Já existe um registro com os mesmos valores únicos.",
        1064: "Erro ao executar a consulta. Verifique a sintaxe SQL.",
        1136: "Erro ao executar a operação. O número de valores fornecidos não corresponde ao número de colunas.",
        1142: "Erro ao acessar a tabela. Permissões insuficientes para realizar a operação.",
        1146: "Erro ao executar a operação. A tabela especificada não existe no banco de dados.",
        1216: "Erro ao adicionar ou atualizar o registro. Violação de chave estrangeira. Verifique as relações entre as tabelas.",
        1217: "Erro ao excluir ou atualizar o registro. Violação de chave estrangeira. Verifique as relações entre as tabelas.",
        1264: "Erro ao executar a operação. Valor fornecido com formato incorreto.",
        1265: "Erro ao adicionar ou atualizar o registro. Dados truncados para a coluna, excedendo o comprimento máximo.",
        1364: "Erro ao adicionar o registro. A coluna não possui um valor padrão e não pode ser deixada em branco.",
        1366: "Erro ao adicionar ou atualizar o registro. Valor incorreto para um tipo de dados inteiro.",
        1451: "Erro ao excluir ou atualizar o registro. Ação restrita devido a uma chave estrangeira.",
        1452: "Erro ao adicionar ou atualizar o registro. A referência a uma chave estrangeira não existe.",
        1692: "Erro ao adicionar ou atualizar o registro. Dados muito longos para a coluna, excedendo o comprimento máximo.",
        2002: "Erro ao conectar ao servidor MySQL. Verifique se o servidor está em execução.",
        2013: "Erro ao conectar ao servidor MySQL. Conexão perdida com o servidor.",
    }


    @staticmethod
    def handle_error(e):
        error_info = {
            "error_type": "GenericError",
            "error_message": str(e),
            "error_code": e.args[0]
        }

        error_info["error_description"] = DBErrors.ERROR_MAP.get(e.args[0], f"Erro Genérico para Código {e.args[0]}")

        return error_info
