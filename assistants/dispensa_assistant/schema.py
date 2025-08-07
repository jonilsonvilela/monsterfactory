# assistants/dispensa_assistant/schema.py
# Contém a definição da estrutura (schema) para os formulários do assistente de dispensa.

def get_schema(form_type: str):
    """
    Retorna o esquema de campos para um determinado tipo de súmula.
    """
    
    schema_comum = {
        "data_publicacao": {"type": "STRING", "description": "Data em que a decisão foi publicada."},
        "prazo_fatal": {"type": "STRING", "description": "Data final para a interposição do recurso."},
        "npj": {"type": "STRING", "description": "Número do NPJ."},
        "contrato_lide": {"type": "STRING", "description": "Número do contrato ou objeto da lide."},
        "operacao_numero": {"type": "STRING", "description": "Número da operação."},
        "data_vencimento_operacao": {"type": "STRING", "description": "Data de vencimento da operação."},
        "autor_es": {"type": "STRING", "description": "Nome(s) do(s) autor(es)."},
        "reu_s": {"type": "STRING", "description": "Nome(s) do(s) réu(s)."},
        "tipo_acao": {"type": "STRING", "description": "Tipo da ação judicial (ex: Busca e Apreensão)."},
        "numero_processo": {"type": "STRING", "description": "Número completo do processo."},
        "orgao_tramitacao": {"type": "STRING", "description": "Vara, Comarca e Estado de tramitação."},
        "valor_causa": {"type": "STRING", "description": "Valor da causa."},
        "valor_pretendido": {"type": "STRING", "description": "Valor pretendido na ação."},
        "valor_condenacao": {"type": "STRING", "description": "Valor total da condenação."},
        "descricao_sucinta": {"type": "STRING", "description": "Relatório detalhado dos fatos, pedido do autor, teor das decisões, e se a obrigação de fazer já foi cumprida."},
        "liminar_deferida": {"type": "STRING", "description": "Responder 'Sim' ou 'Não'."},
        "liminar_cumprida": {"type": "STRING", "description": "Responder 'Sim' ou 'Não'."},
        "cominacao_multa": {"type": "STRING", "description": "Responder 'Sim' ou 'Não'."},
        "multa_valor_diario": {"type": "STRING", "description": "Valor da multa diária, se houver."},
        "multa_limite": {"type": "STRING", "description": "Limite da multa, se houver."},
        "litispendencia_coisa_julgada": {"type": "STRING", "description": "Responder 'Sim' ou 'Não'."},
        "documentos_anexados_check": {"type": "STRING", "description": "Responder 'Sim' ou 'Não'."},
        "escritorio_advogado_contato": {"type": "STRING", "description": "Nome do Escritório, UF, nome completo do Advogado, OAB, e-mail e telefone de contato."},
    }

    if form_type == 'autodispensa':
        autodispensa_schema = schema_comum.copy()
        autodispensa_schema.update({
            "recurso_objeto": {"type": "STRING", "description": "Tipo de recurso objeto da autodispensa (ex: Apelação, Recurso Inominado)."},
            "decisao_objeto_autodispensa": {"type": "STRING", "description": "Especificar qual a decisão objeto da autodispensa e seu número de rastreamento no sistema."},
            "materias_discutidas": {"type": "STRING", "description": "Principais teses jurídicas discutidas no processo."},
            "fundamento_autodispensa": {"type": "STRING", "description": "Apontar o item exato do Manual/Política Recursal que justifica a autodispensa (ex: 'Conforme 13.1.3 Anexo I, inciso II...')."},
            "andamento_registrado": {"type": "STRING", "description": "Código do andamento que será registrado no sistema (ex: 677 ou 703)."},
            "fundamentacao_relatorio": {"type": "STRING", "description": "Breve relato processual com os pleitos da petição inicial e o teor das decisões proferidas."},
            "parecer_fundamentado_autodispensa": {"type": "STRING", "description": "Parecer jurídico elaborado pelo advogado que ampara a autodispensa, enquadrando o caso concreto no item específico do Manual."},
        })
        return autodispensa_schema

    elif form_type in ['dispensa', 'autorizacao']:
        shared_schema = schema_comum.copy()
        shared_schema.update({
            "tipo_recurso": {"type": "STRING", "description": "Tipo de recurso objeto do pedido (ex: Recurso Especial, Agravo de Instrumento)."},
            "solicitado_subsidio": {"type": "STRING", "description": "Responder 'Sim' ou 'Não'."},
            "subsidio_atendido": {"type": "STRING", "description": "Responder 'Sim' ou 'Não'."},
            "subsidio_descricao": {"type": "STRING", "description": "Descrição do subsídio que foi enviado."},
            "subsidio_rastreamento": {"type": "STRING", "description": "Número de rastreamento do subsídio."},
            "subsidio_utilizado_defesa": {"type": "STRING", "description": "Responder 'Sim' ou 'Não'."},
            "subsidio_nao_utilizado_justificativa": {"type": "STRING", "description": "Justificativa para a não utilização do subsídio, se aplicável."},
            "teses_defesa": {"type": "STRING", "description": "Principais teses jurídicas abordadas na defesa do banco."},
            "precedente_materia_julgados": {"type": "STRING", "description": "Responder 'Não' ou 'Sim, julgado Nº XXXXX, de DD/MM/AA'."},
            "obrigacao_fazer_cumprida_descricao": {"type": "STRING", "description": "Responder 'Sim' ou 'Não' e incluir a descrição detalhada da obrigação e seu status de cumprimento."},
            "valor_custas_recursais": {"type": "STRING", "description": "Valor das custas para interposição do recurso."},
        })
        
        if form_type == 'dispensa':
            shared_schema['fundamentacao_dispensa'] = {"type": "STRING", "description": "Citar as circunstâncias peculiares da demanda ou óbices processuais que não recomendam a interposição do recurso."}
        else: # autorizacao
            shared_schema['fundamentacao_autorizacao'] = {"type": "STRING", "description": "Expor os motivos para interpor o recurso, especialmente se a matéria for de autodispensa. Demonstrar prequestionamento e repercussão geral, se aplicável a recurso especial/extraordinário."}
        
        return shared_schema
    
    return None