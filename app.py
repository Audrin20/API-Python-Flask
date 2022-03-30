from bdb import Breakpoint
from itertools import count
from lib2to3.pgen2.token import OP
from typing import Optional
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

server = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='Live de Python')
spec.register(server)
database = TinyDB('database.json')
c = count()

class QueryPessoa(BaseModel):
    id: Optional[int]
    nome: Optional[str]
    idade: Optional[int]

class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=next(c))
    nome: str
    idade: int

class Pessoas(BaseModel):
    pessoas: list[Pessoa]
    count: int


### DEFINIÇÃO DOS VERBOS ###

### GET ###

@server.get('/pessoas') # Precisa conhecer o get, e assim você declara
@spec.validate(query=QueryPessoa, resp=Response(HTTP_200=Pessoas)) # 
def buscar_pessoas():
    query = request.context.query.dict(exclude_none=True)
    todas_as_pessoas = database.search(
        Query().fragment(query)
    )
    return jsonify(
        Pessoas(
            pessoas=database.all(),
            count=len(database.all())
        ).dict())
    # return jsonify(database.all())

@server.get('/pessoas/<int:id>') # Precisa conhecer o get, e assim você declara
@spec.validate(resp=Response(HTTP_200=Pessoa)) # 
def buscar_pessoa(id):
    """ Retorna todas as pessoas da base de dados """
    try:
        pessoa = database.search(Query().id == id)[0]
    except IndexError:
        return {'message': 'Pessoa não encontrada'}, 404
    return jsonify(pessoa)


### POST ### 

@server.post('/pessoas')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_200=Pessoa))
def inserir_pessoas():
    """ Insere uma Pessoa no Banco de Dados""" # Coloca na Documentação do Swagger 
    body = request.context.body.dict()
    database.insert(body)
    return body

### PUT ###
@server.put('/pessoas/<int:id>')
@spec.validate(
    body=Request(Pessoa), resp=Response(HTTP_200=Pessoa)
)
def altera_pessoa(id):
    """ Altera dados na base de dados """
    Pessoa = Query()
    body = request.context.body.dict()
    database.update(body, Pessoa.id ==id)
    return jsonify(body)

### DELETE ###

@server.delete('/pessoas/<int:id>')
@spec.validate(resp=Response('HTTP_204'))
def deleta_pessoa(id):
    """ Deleta pessoas da base de dados """
    Pessoa = Query()
    database.remove(Pessoa.id ==id)
    return jsonify({})

server.run() # Aqui já está rodando