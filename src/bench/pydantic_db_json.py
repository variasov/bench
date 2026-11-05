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
    SELECT l.orderid,
           json_agg(json_build_array(
               l.id, l.productid, l.quantity
           ) ORDER BY l.id) AS arr
    FROM orderlines l
    GROUP BY l.orderid
)
SELECT json_agg(
    json_build_array(o.id, o.fielda, o.fieldb, coalesce(l.arr, '[]'))
    ORDER BY o.id
)::text
FROM orders o
LEFT JOIN lines l ON l.orderid = o.id
'''


def run(iterations: int = 100) -> float:
    load_dotenv()
    engine = Engine(psycopg)
    query = engine.query(QUERY, static=True)
    adapter = TypeAdapter(list[tuple[UUID, int, int, list]])

    def parse(text: str) -> list[Order]:
        return [
            Order(id=row[0], field_a=row[1], field_b=row[2], lines=row[3])
            for row in adapter.validate_json(text)
        ]

    parse(query.scalar())

    start = time.perf_counter()
    for _ in range(iterations):
        parse(query.scalar())
    elapsed = time.perf_counter() - start

    return elapsed


def main() -> None:
    iterations = 100
    elapsed = run(iterations)
    print(f'{iterations} iterations: {elapsed:.3f}s '
          f'({elapsed / iterations * 1000:.3f} ms/iter)')


if __name__ == '__main__':
    main()
