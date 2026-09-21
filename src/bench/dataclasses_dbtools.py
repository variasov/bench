import time
from dataclasses import dataclass, field
from uuid import UUID

import psycopg
from classic.db_tools import Append, Engine, Entity, Value

from .utils import load_dotenv


@dataclass
class Order:
    id: UUID
    field_a: int
    field_b: int
    lines: list = field(default_factory=list)


@dataclass
class OrderLine:
    id: UUID
    product_id: int
    quantity: int


QUERY = '''
SELECT o.id AS order__id,
       o.fielda AS order__field_a,
       o.fieldb AS order__field_b,
       l.id AS orderline__id,
       l.productid AS orderline__product_id,
       l.quantity AS orderline__quantity
FROM "Order" o
LEFT JOIN orderlines l ON l.orderid = o.id
ORDER BY o.id, l.id
'''


def run(iterations: int = 100) -> float:
    load_dotenv()
    engine = Engine(psycopg)
    query = engine.query(QUERY, static=True).map_to(
        Order, 'order',
        order=Entity(Order, 'id', lines=Append(OrderLine)),
        orderline=Value(OrderLine),
    )

    query.all()

    start = time.perf_counter()
    for _ in range(iterations):
        query.all()
    elapsed = time.perf_counter() - start

    return elapsed


def main() -> None:
    iterations = 100
    elapsed = run(iterations)
    print(f'{iterations} iterations: {elapsed:.3f}s '
          f'({elapsed / iterations * 1000:.3f} ms/iter)')


if __name__ == '__main__':
    main()
