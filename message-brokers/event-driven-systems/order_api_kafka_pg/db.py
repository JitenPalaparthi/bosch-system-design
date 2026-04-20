
import os
import decimal
import psycopg2
import psycopg2.extras

DDL = """
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    item TEXT NOT NULL,
    price NUMERIC(12,2) NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

def _conn_params():
    return dict(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        user=os.getenv("PGUSER", "app"),
        password=os.getenv("PGPASSWORD", "app"),
        dbname=os.getenv("PGDATABASE", "app"),
    )

def get_conn():
    return psycopg2.connect(**_conn_params())

def init_db():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(DDL)
        conn.commit()

def insert_order(order):
    price = decimal.Decimal(order["price"]).quantize(decimal.Decimal("0.01"))
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """INSERT INTO public.orders (id, name, item, price, quantity)
            VALUES (%(id)s, %(name)s, %(item)s, %(price)s, %(quantity)s)
            RETURNING id, name, item, price, quantity, created_at""", 
            {**order, "price": price}
        )
        row = cur.fetchone()
        conn.commit()
        return dict(row)
