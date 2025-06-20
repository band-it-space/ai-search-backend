# FastAPI + Milvus Demo

This project demonstrates a FastAPI application with Milvus vector database.

## Features

- Upload of `.xls` and `.xlsx` Excel files with product data
- Embedding generation and insertion into Milvus
- Vector similarity search
- Request logging
- Swagger documentation at `/docs`

## Quick Start

```bash
docker-compose up --build
```

## API Usage

1. Open [http://localhost:8000/docs](http://localhost:8000/docs)
2. Use `POST /api/v1/upload/` to upload Excel
3. Use `GET /api/v1/search/` to find similar items

## Excel Format

Expected columns:

- `date_prihod`
- `costs`
- `costs_NDS`
- `name`
- `tovar_name`
- `name_tovar_1C`

## Dependencies

- Python 3.11
- Milvus 2.5.7
- pandas, openpyxl, xlrd==1.2.0
- PyMilvus with model support
