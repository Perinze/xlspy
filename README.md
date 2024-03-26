# xlspy

## todo list

- invoke function from top
- iterate possible types in config
- for loop invariant args

## note

### semantic

#### for loop

in current version,
for-loop can only contain one stmt,
and iter must be range(fixed_number).

### typer

#### return type of visit

visit_stmt: None

visit_expr: str (as name of this node)