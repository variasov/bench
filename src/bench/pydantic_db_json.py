import time
from uuid import UUID

import psycopg
from classic.db_tools import Engine
from pydantic import BaseModel, Field, TypeAdapter

from .utils import load_dotenv


class Order(BaseModel):
    id: UUID
    field_a: int
    field_b: int
    lines: list = Field(default_factory=list)


class OrderLine(BaseModel):
    id: UUID
    product_id: int
    quantity: int


QUERY = '''
WITH orders AS (
    SELECT o.id, o.fielda, o.fieldb
    FROM "Order" o
),
lines AS (
    SELECT l.orderid, l.id, l.productid, l.quantity
    FROM orderlines l
)
SELECT json_agg(
    json_build_object(
        'id', o.id,
        'field_a', o.fielda,
        'field_b', o.fieldb,
        'lines', coalesce(
            (SELECT json_agg(json_build_object(
                'id', l.id,
                'product_id', l.productid,
                'quantity', l.quantity
            ) ORDER BY l.id)
            FROM lines l
            WHERE l.orderid = o.id),
            '[]'
        )
    )
    ORDER BY o.id
)::text
FROM orders o
'''


def run(iterations: int = 100) -> float:
    load_dotenv()
    engine = Engine(psycopg)
    query = engine.query(QUERY, static=True)
    adapter = TypeAdapter(list[Order])

    adapter.validate_json(query.scalar())

    start = time.perf_counter()
    for _ in range(iterations):
        adapter.validate_json(query.scalar())
    elapsed = time.perf_counter() - start

    return elapsed


def main() -> None:
    iterations = 100
    elapsed = run(iterations)
    print(f'{iterations} iterations: {elapsed:.3f}s '
          f'({elapsed / iterations * 1000:.3f} ms/iter)')


if __name__ == '__main__':
    main()
