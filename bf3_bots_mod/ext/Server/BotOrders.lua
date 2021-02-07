class 'BotOrders'

function BotOrders:__init()
    -- just stand around and smell the flowers
    self.WANDER = 1
    -- go to objective
    self.OBJECTIVE = 2
    -- go to enemy
    self.ENEMY = 3
    -- go to friendly
    self.FRIENDLY = 4
end

if not g_BotOrders then
    g_BotOrders = BotOrders()
end
return g_BotOrders