import os
import time
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Uuid, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    selectinload,
)

from .utils import load_dotenv


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = 'Order'
    __table_args__ = {'quote': True}

    id: Mapped[UUID] = mapped_column('id', Uuid, primary_key=True)
    field_a: Mapped[int] = mapped_column('fielda', Integer)
    field_b: Mapped[int] = mapped_column('fieldb', Integer)
    lines: Mapped[list['OrderLine']] = relationship(
        back_populates='order', order_by='OrderLine.id',
    )


class OrderLine(Base):
    __tablename__ = 'orderlines'

    id: Mapped[UUID] = mapped_column('id', Uuid, primary_key=True)
    order_id: Mapped[UUID] = mapped_column('orderid', Uuid, ForeignKey('Order.id'))
    product_id: Mapped[int] = mapped_column('productid', Integer)
    quantity: Mapped[int] = mapped_column('quantity', Integer)
    order: Mapped[Order] = relationship(back_populates='lines')


def run(iterations: int = 100) -> float:
    load_dotenv()
    url = (
        f"postgresql+psycopg://{os.environ['PGUSER']}:"
        f"{os.environ['PGPASSWORD']}@{os.environ['PGHOST']}:"
        f"{os.environ['PGPORT']}/{os.environ['PGDATABASE']}"
    )
    engine = create_engine(url)

    query = select(Order).options(selectinload(Order.lines))

    with Session(engine) as session:
        session.scalars(query).all()

    start = time.perf_counter()
    for _ in range(iterations):
        with Session(engine) as session:
            session.scalars(query).all()
    elapsed = time.perf_counter() - start

    return elapsed


def main() -> None:
    iterations = 100
    elapsed = run(iterations)
    print(f'{iterations} iterations: {elapsed:.3f}s '
          f'({elapsed / iterations * 1000:.3f} ms/iter)')


if __name__ == '__main__':
    main()
