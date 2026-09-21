BEGIN;

DROP TABLE IF EXISTS orderlines CASCADE;
DROP TABLE IF EXISTS "Order" CASCADE;

CREATE TABLE "Order" (
    Id     UUID PRIMARY KEY DEFAULT uuidv7(),
    FieldA INTEGER NOT NULL,
    FieldB INTEGER NOT NULL
);

CREATE TABLE OrderLines (
    Id        UUID PRIMARY KEY DEFAULT uuidv7(),
    OrderId   UUID NOT NULL REFERENCES "Order"(Id),
    ProductId INTEGER NOT NULL,
    Quantity  INTEGER NOT NULL
);

WITH orders AS (
    INSERT INTO "Order" (Id, FieldA, FieldB)
    SELECT uuidv7(), n % 7, n * 3
    FROM generate_series(1, 100) AS n
    RETURNING Id, FieldB
),
numbered AS (
    SELECT Id, row_number() OVER (ORDER BY FieldB) AS rn
    FROM orders
)
INSERT INTO OrderLines (Id, OrderId, ProductId, Quantity)
SELECT uuidv7(),
       o.Id,
       (n * 13) % 100 + 1,
       (n % 5) + 1
FROM generate_series(1, 1000) AS n
JOIN numbered o ON o.rn = (n - 1) / 10 + 1;

COMMIT;
