from flask import Flask, request,jsonify
from itertools import count
from flask_pydantic_spec import FlaskPydanticSpec, Response,Request
from pydantic import BaseModel,Field
from tinydb import TinyDB,Query
server = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='Livraria')

spec.register(server)
database = TinyDB('livraria.json')
c = count()

class Livro(BaseModel):
    id: int = Field(default_factory=lambda: next(c))
    titulo: str
    autor: str

class Livros(BaseModel):
    livros: list[Livro]
    count: int


@server.get('/books/<int:id>')
@spec.validate(resp=Response(HTTP_200=Livro))
def get_book(id):
    '''Returns a single book from database'''
    Livro = Query()
    return jsonify(database.get(Livro.id == id))


@server.get('/books')
@spec.validate(resp=Response(HTTP_200=Livros))
def get_books():
    '''Returns all books from database'''
    return jsonify(
        Livros(
            livros = database.all(),
            count = len(database.all())
        ).dict())


@server.post('/books')
@spec.validate(body=Request(Livro),resp=Response(HTTP_200=Livro))
def insert_book():
    ''' Insert new book in Database'''
    body = request.context.body.dict()
    database.insert(body)
    return body


@server.put('/books/<int:id>')
@spec.validate(body=Request(Livro),resp=Response(HTTP_200=Livro))
def update_book(id):
    ''' Update a single book in Database'''
    Livro = Query()
    body = request.context.body.dict()
    database.update(body,Livro.id == id)
    return jsonify(body)


@server.delete('/books/<int:id>')
@spec.validate(resp=Response('HTTP_204'))
def remove_book(id):
    ''' Remove a single book from Database'''
    Livro = Query()
    database.remove(Livro.id == id)
    return jsonify({})

server.run()


