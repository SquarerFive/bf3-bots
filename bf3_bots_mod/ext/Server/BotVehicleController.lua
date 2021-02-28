local VecLib = require('__shared/VecLib')

class("BotVehicleController")
function BotVehicleController:__init()
    self.yaw = 0.0
    self.momentum = 0.0
    self.deltaTime = 0.0
    self.reversing = false
    self.moving = true
    self.old_momentum = 0.0
    self.old_yaw = 0.0
    -- config
    self.intensity = 2.0
    self.power = 1.0
    self.alpha = 0.0
end

function BotVehicleController:Update(newYaw, newMomentum, deltaTime)
    self.deltaTime = deltaTime
    local delta = (self.deltaTime^ self.power)*self.intensity
    self.yaw = VecLib:CosineInterpolation(self.old_yaw, newYaw, self.alpha)
    self.momentum = VecLib:CosineInterpolation(self.old_momentum, newMomentum, self.alpha)
    self.alpha = self.alpha + delta

    if self.alpha >= 1.0 then
        self.alpha = 0.0
        self.old_yaw = self.yaw
        self.old_momentum = self.momentum
    end
end

function BotVehicleController.Create()
    local self = BotVehicleController()
    return self
end

if g_BotVehicleController == nil then
    g_BotVehicleController = BotVehicleController()
end

return g_BotVehicleController