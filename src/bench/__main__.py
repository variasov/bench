import time
from . import (
    dataclasses_dbtools,
    msgspec_db_json,
    msgspec_db_json_array,
    msgspec_db_json_array_fast,
    msgspec_db_json_array_fast_text,
    msgspec_db_json_array_nosort,
    msgspec_db_json_lateral,
    msgspec_dbtools,
    pydantic_db_json,
    pydantic_db_json_dataclass,
    sqlalchemy_orm,
    sqlalchemy_orm_join,
)


BENCHES = (
    ('dataclasses + dbtools', dataclasses_dbtools.run),
    ('msgspec + dbtools', msgspec_dbtools.run),
    ('msgspec + json (object)', msgspec_db_json.run),
    ('msgspec + json (array)', msgspec_db_json_array.run),
    ('msgspec + json (array, fast)', msgspec_db_json_array_fast.run),
    ('msgspec + json (array, fast text)', msgspec_db_json_array_fast_text.run),
    ('msgspec + json (array, nosort)', msgspec_db_json_array_nosort.run),
    ('msgspec + json (lateral)', msgspec_db_json_lateral.run),
    ('pydantic + json (array, fast text)', pydantic_db_json.run),
    ('pydantic dataclass + json (array, fast text)', pydantic_db_json_dataclass.run),
    ('sqlalchemy ORM', sqlalchemy_orm.run),
    ('sqlalchemy ORM (join)', sqlalchemy_orm_join.run),
)


def main() -> None:
    iterations = 100
    for name, run in BENCHES:
        elapsed = run(iterations)
        print(f'{name}: {elapsed:.3f}s '
              f'({elapsed / iterations * 1000:.3f} ms/iter)')


if __name__ == '__main__':
    main()
