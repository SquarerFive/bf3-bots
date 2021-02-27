local VecLib = require('__shared/VecLib')

class("BotVehicleController")
function BotVehicleController:__init()
    self.yaw = 0.0
    self.momentum = 0.0
    self.deltaTime = 0.0
    self.reversing = false
    self.moving = true

    -- config
    self.intensity = 8.0
    self.power = 2.0
end

function BotVehicleController:Update(newYaw, newMomentum, deltaTime)
    self.deltaTime = deltaTime
    self.yaw = VecLib:CosineInterpolation(self.yaw, newYaw, (self.deltaTime^ self.power)*self.intensity)
    self.momentum = VecLib:CosineInterpolation(self.momentum, newMomentum, (self.deltaTime^ self.power)*self.intensity)
end

function BotVehicleController.Create()
    local self = BotVehicleController()
    return self
end

if g_BotVehicleController == nil then
    g_BotVehicleController = BotVehicleController()
end

return g_BotVehicleController