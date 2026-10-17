"""Örnek yönetici, öğrenci ve kitap verisi yükler."""

from datetime import datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models.admin import Admin
from app.models.book import Book
from app.models.loan import Loan, LoanStatus
from app.models.student import Student
from app.security import hash_password

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        if not db.query(Admin).filter(Admin.username == "admin").first():
            db.add(
                Admin(
                    username="admin",
                    full_name="Kütüphane Yöneticisi",
                    email="admin@universite.edu.tr",
                    password_hash=hash_password("admin123"),
                )
            )

        student = db.query(Student).filter(Student.email == "ogrenci@universite.edu.tr").first()
        if not student:
            student = Student(
                student_number="2024001",
                full_name="Ayşe Yılmaz",
                email="ogrenci@universite.edu.tr",
                password_hash=hash_password("ogrenci123"),
                department="Bilgisayar Mühendisliği",
            )
            db.add(student)
            db.flush()

        books_data = [
            ("9780134685991", "Effective Java", "Joshua Bloch", "Yazılım", 3),
            ("9780201633610", "Design Patterns", "Gang of Four", "Yazılım", 2),
            ("9780132350884", "Clean Code", "Robert C. Martin", "Yazılım", 4),
            ("9780262033848", "Introduction to Algorithms", "Cormen et al.", "Algoritma", 2),
        ]
        for isbn, title, author, cat, copies in books_data:
            if not db.query(Book).filter(Book.isbn == isbn).first():
                db.add(
                    Book(
                        isbn=isbn,
                        title=title,
                        author=author,
                        category=cat,
                        total_copies=copies,
                        available_copies=copies,
                    )
                )

        db.commit()

        student = db.query(Student).filter(Student.email == "ogrenci@universite.edu.tr").first()
        book = db.query(Book).filter(Book.isbn == "9780134685991").first()
        if student and book and not db.query(Loan).filter(Loan.student_id == student.id, Loan.book_id == book.id).first():
            book.available_copies = max(0, book.available_copies - 1)
            db.add(
                Loan(
                    student_id=student.id,
                    book_id=book.id,
                    borrowed_at=datetime.utcnow() - timedelta(days=20),
                    due_date=datetime.utcnow() - timedelta(days=6),
                    status=LoanStatus.OVERDUE,
                )
            )
            db.commit()
        print("Seed tamamlandı.")
        print("  Yönetici: admin@universite.edu.tr / admin123")
        print("  Öğrenci: ogrenci@universite.edu.tr / ogrenci123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
