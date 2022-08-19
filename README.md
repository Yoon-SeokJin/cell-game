# play.py

game play test file.

# Todo List

## PG_coord_list1

RL: policy gredient

input: [num of cells, *(cell0.info), *(cell1.info), ..., *(cell50.info)]

cell.info = [cell.pos.x, cell.pos.y, cell.velocity.x, cell.velocity.y, cell.radius, *(cell.type)]

cell.type = one-hot vector (vital cell, dead cell)

input shape = (351,)

output shape = (360,) (logit value)


## PG_coord_list2

RL: policy gredient

input: [cell where (x, y) position . info, ...]

cell.info = [cell.velocity.x, cell.velocity.y, cell.radius, *(cell.type)]

cell.type = one-hot vector (vital cell, dead cell)

input shape = (1280, 720, 5)

CNN?


## PG_sensor

RL: policy gredient

input: [object where x degree . info]

cell.info = [cell.pos.x, cell.pos.y, cell.velocity.x, cell.velocity.y, cell.radius, *(cell.type)]

cell.type = one-hot vector (cell, wall)

pos is relative value.

input shape = (360, )

circular CNN?