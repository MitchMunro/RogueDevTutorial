from entity import Entity

player = Entity(char="@", color=(224, 194, 134), name="Player", blocks_movement=True)

# Monsters
orc = Entity(char="o", color=(63, 127, 63), name="Orc", blocks_movement=True)
troll = Entity(char="T", color=(0, 127, 0), name="Troll", blocks_movement=True)
