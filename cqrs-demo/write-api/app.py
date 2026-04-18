import os
from decimal import Decimal
from typing import Optional

import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "appdb"),
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASSWORD", "apppass"),
}

app = FastAPI(title="CQRS Write API", version="1.0.0")


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    category: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = None


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


@app.get("/health")
def health():
    return {"status": "ok", "service": "write-api"}


@app.post("/products")
def create_product(product: ProductCreate):
    sql = """
        INSERT INTO public.products (name, description, price, category)
        VALUES (%s, %s, %s, %s)
        RETURNING id, name, description, price, category, created_at, updated_at
    """
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (product.name, product.description, product.price, product.category),
                )
                row = cur.fetchone()
        return {
            "message": "written to postgres",
            "product": {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": float(row[3]),
                "category": row[4],
                "created_at": row[5].isoformat(),
                "updated_at": row[6].isoformat(),
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate):
    updates = []
    values = []

    for field in ["name", "description", "price", "category"]:
        value = getattr(product, field)
        if value is not None:
            updates.append(f"{field} = %s")
            values.append(value)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    values.append(product_id)
    sql = f"""
        UPDATE public.products
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING id, name, description, price, category, created_at, updated_at
    """

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="Product not found")
        return {
            "message": "updated in postgres",
            "product": {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": float(row[3]),
                "category": row[4],
                "created_at": row[5].isoformat(),
                "updated_at": row[6].isoformat(),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM public.products WHERE id = %s RETURNING id",
                    (product_id,),
                )
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "deleted from postgres", "id": row[0]}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
