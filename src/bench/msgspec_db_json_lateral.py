import time
from uuid import UUID

import msgspec
import psycopg
from classic.db_tools import Engine

from .utils import load_dotenv


class Order(msgspec.Struct):
    id: UUID
    field_a: int
    field_b: int
    lines: list = msgspec.field(default_factory=list)


class OrderLine(msgspec.Struct):
    id: UUID
    product_id: int
    quantity: int


QUERY = '''
SELECT (SELECT json_agg(
    json_build_object(
        'id', o.id,
        'field_a', o.fielda,
        'field_b', o.fieldb,
        'lines', l.lines
    )
    ORDER BY o.id
)
FROM "Order" o
LEFT JOIN LATERAL (
    SELECT coalesce(json_agg(json_build_object(
        'id', x.id,
        'product_id', x.productid,
        'quantity', x.quantity
    ) ORDER BY x.id), '[]') AS lines
    FROM orderlines x
    WHERE x.orderid = o.id
) l ON TRUE)::text
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
