from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from app.models.book import Book
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.security import require_admin

router = APIRouter(prefix="/books", tags=["Kitaplar"])


@router.get("", response_model=list[BookRead])
def search_books(
    q: str | None = Query(None, description="Başlık, yazar, ISBN veya kategori"),
    db: Session = Depends(get_db),
):
    query = db.query(Book)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Book.title.ilike(term),
                Book.author.ilike(term),
                Book.isbn.ilike(term),
                Book.category.ilike(term),
            )
        )
    return query.order_by(Book.title).all()


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")
    return book


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(body: BookCreate, db: Session = Depends(get_db), _: Admin = Depends(require_admin)):
    if db.query(Book).filter(Book.isbn == body.isbn).first():
        raise HTTPException(status_code=400, detail="ISBN zaten kayıtlı")
    book = Book(
        isbn=body.isbn,
        title=body.title,
        author=body.author,
        category=body.category,
        description=body.description,
        total_copies=body.total_copies,
        available_copies=body.total_copies,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.patch("/{book_id}", response_model=BookRead)
def update_book(
    book_id: int,
    body: BookUpdate,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")

    data = body.model_dump(exclude_unset=True)
    if "total_copies" in data:
        new_total = data["total_copies"]
        borrowed = book.total_copies - book.available_copies
        if new_total < borrowed:
            raise HTTPException(status_code=400, detail="Toplam kopya, ödünçte olanlardan az olamaz")
        book.total_copies = new_total
        book.available_copies = new_total - borrowed
        data.pop("total_copies")

    for key, value in data.items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book
