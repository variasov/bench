import time
from uuid import UUID

import msgspec
import psycopg
from classic.db_tools import Engine

from .utils import load_dotenv


class Order(msgspec.Struct, array_like=True):
    id: UUID
    field_a: int
    field_b: int
    lines: list = msgspec.field(default_factory=list)


class OrderLine(msgspec.Struct, array_like=True):
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
           )) AS arr
    FROM orderlines l
    GROUP BY l.orderid
)
SELECT json_agg(
    json_build_array(o.id, o.fielda, o.fieldb, coalesce(l.arr, '[]'))
)::text
FROM orders o
LEFT JOIN lines l ON l.orderid = o.id
'''


def run(iterations: int = 100) -> float:
    load_dotenv()
    engine = Engine(psycopg)
    query = engine.query(QUERY, static=True)
    decoder = msgspec.json.Decoder(list[Order])

    decoder.decode(query.scalar())

    start = time.perf_counter()
    for _ in range(iterations):
        decoder.decode(query.scalar())
    elapsed = time.perf_counter() - start

    return elapsed


def main() -> None:
    iterations = 100
    elapsed = run(iterations)
    print(f'{iterations} iterations: {elapsed:.3f}s '
          f'({elapsed / iterations * 1000:.3f} ms/iter)')


if __name__ == '__main__':
    main()
