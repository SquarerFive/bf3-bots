class 'BotActions'


function BotActions:__init()
    self.NONE = 1
    self.ATTACK = 2
    self.DEFEND = 3
    self.DESTROY = 4
    self.GOTO = 5
    self.GET_IN = 6
    self.GET_OUT = 7
    self.PROVIDE = 8
end

if not g_BotActions then
    g_BotActions = BotActions()
end
return g_BotActions