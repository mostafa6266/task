from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Book
from ..extensions import db

books_bp = Blueprint('books', __name__)

@books_bp.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    current_user = get_jwt_identity()
    books = Book.query.filter((Book.is_public == True) | (Book.user_id == current_user)).all()
    
    books_list = [
        {
            'id': book.id, 
            'title': book.title, 
            'author': book.author, 
            'published_date': book.published_date, 
            'is_public': book.is_public
        }
        for book in books
    ]
    
    return jsonify(books_list)


@books_bp.route('/books', methods=['POST'])
@jwt_required()
def add_book():
    current_user = get_jwt_identity()
    data = request.get_json()

    # Check if a book with the same title already exists
    existing_book = Book.query.filter_by(title=data['title']).first()
    if existing_book:
        return jsonify({'message': 'A book with this title already exists'}), 400

    # If no book with the same title exists, create a new book
    new_book = Book(
        title=data['title'], 
        author=data['author'], 
        published_date=data['published_date'], 
        is_public=data.get('is_public', True), 
        user_id=current_user
    )
    db.session.add(new_book)
    db.session.commit()

    return jsonify({'message': 'Book added successfully'}), 201
