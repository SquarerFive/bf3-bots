from enum import Enum, IntEnum


class BotOrdersEnum(IntEnum):
    WANDER = 1
    OBJECTIVE = 2
    ENEMY = 3
    FRIENDLY = 4

class BotActionEnum(IntEnum):
    NONE = 1
    ATTACK = 2
    DEFEND = 3
    DESTROY = 4
    GOTO = 5
    GET_IN = 6
    GET_OUT = 7
    PROVIDE = 8
    PROVIDE_HEALTH = 9
    PROVIDE_AMMO = 10
    VEHICLE_DISCOVERY = 11