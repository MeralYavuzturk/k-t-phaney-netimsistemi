# Online Kütüphane Yönetim Sistemi

Üniversite öğrencilerinin kitap arayabildiği, ödünç alıp iade edebildiği; yöneticilerin stok takibi, kitap ekleme ve gecikme raporu alabildiği web tabanlı kütüphane uygulaması.

## Teknolojiler

- **Backend:** Python 3.12+ (önerilen; 3.14 ile pydantic wheel uyumsuzluğu olabilir), FastAPI, SQLAlchemy, JWT kimlik doğrulama
- **Veritabanı:** SQLite (geliştirme); PostgreSQL için `DATABASE_URL` ile uyumlu
- **Frontend:** Vanilla HTML, CSS, JavaScript

## Kurulum ve çalıştırma

```powershell
cd library-management-system\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Tarayıcı: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
API dokümantasyonu: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Demo hesaplar

| Rol | E-posta | Şifre |
|-----|---------|-------|
| Öğrenci | ogrenci@universite.edu.tr | ogrenci123 |
| Yönetici | admin@universite.edu.tr | admin123 |

## API uç noktaları (özet)

| Metot | Yol | Açıklama |
|-------|-----|----------|
| POST | `/api/auth/register` | Öğrenci kaydı |
| POST | `/api/auth/login` | Giriş (`as_admin: true` yönetici) |
| GET | `/api/books?q=` | Kitap arama |
| POST | `/api/books` | Kitap ekle (yönetici) |
| PATCH | `/api/books/{id}` | Kitap güncelle (yönetici) |
| GET | `/api/loans/me` | Öğrencinin ödünçleri |
| POST | `/api/loans/borrow` | Ödünç al |
| POST | `/api/loans/{id}/return` | İade |
| GET | `/api/loans/reports/overdue` | Gecikme raporu (yönetici) |

## UML teslim dosyaları

Sınıf, nesne, paket ve dağıtım diyagramları: [docs/UML_DIYAGRAMLARI.md](docs/UML_DIYAGRAMLARI.md)

## İş kuralları

- Varsayılan ödünç süresi: 14 gün (`LOAN_DAYS_DEFAULT` / `config.py`)
- Öğrenci başına en fazla 5 aktif ödünç
- Stok: `available_copies` ödünç/iade ile güncellenir
- Vadesi geçen kayıtlar `overdue` olarak işaretlenir ve yönetici raporunda listelenir
