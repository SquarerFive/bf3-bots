

local VecLib = require('__shared/VecLib')
local NavGrid = require('__shared/NavGrid')
local Orders = require("BotOrders")
local Actions = require("BotActions")
local BotVehicleController = require('BotVehicleController')


class("Bot")

function Bot:__init()
    self.player_controller = nil
    self.soldier = nil
    self.__input = nil
    --
    self.order = Orders.WANDER
    self.action = Actions.ATTACK
    self.requested_order = -1
    self.requested_action = Actions.ATTACK
    self.requested_target_id = -2
    --

    self.alive = false
    self.yaw = 0.0
    self.pitch = 0.0
    self.nav_grid = nil
    --
    self.objective = nil -- Entity (SpatialEntity | GameEntity or whatever inherits SpatialEntity)
    self.target = nil -- Entity (Player) | (ControllableEntity) -- or a vehicle.. whatever can result in dealing damage to the enemy
    -- 
    self.path_step = 1
    self.path = {}
    self.lock = false
    self.destination = nil
    --
    self.bot_index = nil
    --
    self.last_position_check_time = 0
    self.last_long_position_check_time = 0
    --
    self.last_position = Vec3(0.0, 0.0, 0.0)
    self.long_last_position = Vec3(0.0, 0.0, 0.0)
    --
    self.set_unlocks = false
    --
    self.requested_respawn = true
    --
    self.in_vehicle = false
    --
    self.throttle = false
    --
    self.jumping = false
    --
    self.sprinting = false
    --
    self.lock_path = false
    --
    self.cached_destination = Vec3(0.0, 0.0, 0.0)
    --
    self.firing = false

    self.aiming = false
    --
    self.stopMoving = false
    --
    self.crouching = false
    --
    self.firingOffset = Vec3(0.0000, 0.001, 0.000) -- local offset when firing, -+
    self.firingBaseOffset = Vec3(0.001, 0.001, 0.00)
    self.aimWhenFire = true
    self.fireProbabilityPerTick = 70
    -- reset the path after some time
    self.last_path_reset_time = 0.0
    -- bot will attempt to destroy whatever is obstructing it
    self.knifing = false
    self.knifingGate = false
    --
    self.selected_kit = nil
    --
    self.provides_ammo = false
    self.provides_ammo_slot = -1
    --
    self.provides_health = false
    self.provides_health_slot = -1
    --
    self.delta_time = 0.0
    --
    self.is_providing = false
    self.botVehicleController = BotVehicleController.Create()
    self.is_secondary = false
    --
    self.last_request_ammo_request = 0
    self.last_request_health_request = 0
    -- Events:Subscribe("UpdateManager:Update", self, self.InternalTick)
    self.spawned = false
    self.soldierBP = nil
    self.target_vehicle = nil
end

function Bot:UpdateAimSettings(newFiringOffset, newFiringBaseOffset, newAimWhenFire)
    self.firingOffset = newFiringOffset
    self.firingBaseOffset = newFiringBaseOffset
    self.aimWhenFire = newAimWhenFire
end

function Bot:EncodeAsJSON()
    local data = "{ "
    if self.player_controller.hasSoldier then
        data = data..'"transform": '..json.encode(self.player_controller.soldier.transform)..', "health": '..self.player_controller.soldier.health
    else
        data = data..'"transform": '..'{"forward": {"x": 0, "y": 0, "z": 1}, "right": {"x": 1, "y": 0, "z": 0}, "up": {"x": 0, "y": 1, "z": 0}, "trans": {"x": 0, "y": 1, "z": 0}}'..', "health": 0.0'
    end
    data = data .. ', "team": '..self.player_controller.teamId..
        ', "name": '..'"'..self.player_controller.name..'"'..
        ', "action": '..self.action..
        ', "order": '..self.order..
        ', "player_id":'..self.player_controller.id..
        ', "in_vehicle": false'..
        ', "bot_index": '..self.bot_index..
        ', "alive": '..tostring(self.player_controller.alive)..
        ', "requested_order": '..tostring(self.requested_order)..
        ', "requested_action": '..tostring(self.requested_action)..
        ', "squad": '..tostring(self.player_controller.squadId)..
        ', "requested_target_id": '..tostring(self.requested_target_id)
    data = data .. " }"
    return data
end

function Bot:EncodeAsJSONConcat()
    -- print("concat bot")
    local keys = {'name', 'team', 'action', 'order', 'player_id', 'bot_index', 'in_vehicle', 'transform', 'health', 'alive', 'requested_order', 'requested_action', 'squad', 'requested_target_id'}
    local values = {'"'..self.player_controller.name..'"', self.player_controller.teamId, self.action, self.order, self.player_controller.id, self.bot_index,
                        tostring(self.in_vehicle)}
    local buffer = {"{ "}
    if self.player_controller.hasSoldier and self.player_controller.soldier ~= nil then
        table.insert(values, json.encode(self.player_controller.soldier.transform))
        table.insert(values, tostring(self.player_controller.soldier.health))
    else
        --table.insert(values, json.encode(LinearTransform(1.0)))
        table.insert(values, '{"forward": {"x": 0, "y": 0, "z": 1}, "right": {"x": 1, "y": 0, "z": 0}, "up": {"x": 0, "y": 1, "z": 0}, "trans": {"x": 0, "y": 1, "z": 0}}')
        table.insert(values, '0.0')
    end

    table.insert(values, tostring(self.player_controller.alive))
    table.insert(values, tostring(self.requested_order))
    table.insert(values, tostring(self.requested_action))
    table.insert(values, tostring(self.player_controller.squadId))
    table.insert(values, tostring(self.requested_target_id))
    for idx, key in pairs(keys) do
        if idx == 1 then
            buffer[#buffer+1] = '"'..key..'":'..values[idx]
        else
            buffer[#buffer+1] = ', "'..key..'":'..values[idx]
        end
    end
    buffer[#buffer+1] = " }"
    return table.concat(buffer)
end

function Bot:PathPointToVec3(point)
    return Vec3(point.x, point.y, point.z)
end

function Bot:IsOutOfAmmo()
    if self.player_controller.alive and self.player_controller.soldier ~= nil then
        local soldier = self.player_controller.soldier
        if (soldier.weaponsComponent) then
            if soldier.weaponsComponent.currentWeapon ~= nil then
                return soldier.weaponsComponent.currentWeapon.secondaryAmmo <= 1
            end
        end
    end
    return false
end

function Bot:IsLowHealth()
    if self.player_controller.alive and self.player_controller.soldier ~= nil then
        return self.player_controller.soldier.health <= 30
    end
    return false
end

function Bot:DropProvider()
    if self.player_controller.alive and self.player_controller.soldier ~= nil then
        self.is_providing = true
        self.firing = false
        self.aiming = false
        self.crouching = false
        self.jumping = false
        self.knifing = false
    end
end

function Bot:GetLocalOffsetTransform(transform)
    local tc = transform:Clone()
    -- print(self.firingOffset)
    tc:Translate(
        tc.left * self.firingBaseOffset.x
    )
    tc:Translate(
        tc.up * self.firingBaseOffset.y
    )
    tc:Translate(
        tc.forward * self.firingBaseOffset.z
    )

    tc:Translate(
        tc.left * (math.random(-1, 1)*self.firingOffset.x)
    )
    tc:Translate(
        tc.up * (math.random(-1, 1)*self.firingOffset.y)
    )
    tc:Translate(
        tc.forward * (math.random(-1, 1)*self.firingOffset.z)
    )
    return tc
end

function Bot:IsAtDestination()
    -- print("IsAtDestination?")
    if self.path_step+1 > #self.path then
        return true, true
    end
    if self.player_controller.soldier ~= nil then
        if self.player_controller.soldier.transform.trans:Distance(
            self.path[self.path_step]:Clone()
            -- self:PathPointToVec3(self.path[self.path_step])
        ) <= 2 then
            return true, false
        end
    end
    return false, false
end

function Bot:StepPath()
    local finished = false
    if #self.path > 0 then
        if not (self.path_step >= #self.path) then
            -- local pos = self.path[self.path_step]:Clone()
                -- self:PathPointToVec3(self.path[self.path_step])
            self.destination = self.path[self.path_step]:Clone()
            local is_at_destination, is_outside_path = self:IsAtDestination()
            if is_at_destination and not is_outside_path then
                --print("Stepping path + 1")
                self.path_step  = self.path_step + 1
                self.lock_path = false
            end
            if math.abs(self.destination.y - self.player_controller.soldier.transform.trans.y) > 2 then
                self.destination = Vec3(self.destination.x, self.player_controller.soldier.transform.trans.y, self.destination.z)
            end
            if self.destination:Distance(self.player_controller.soldier.transform.trans) > 5 then
                self.sprinting = true
            else
                self.sprinting = false
            end
            -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAThrottle, 1)
            self.throttle = true
            if (SharedUtils:GetTime() - self.last_position_check_time) > 0.5 then
                local myXYTrans = Vec3(self.player_controller.soldier.transform.trans.x, 1.0, self.player_controller.soldier.transform.trans.z)
                if  myXYTrans:Distance(Vec3(self.last_position.x, 1.0, self.last_position.z)) < 1.0 then
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAJump, 1.0)
                    self.jumping = true
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIASprint, 1.0)
                    self.sprinting = true 

                    -- remove this if crash
                    self.lock_path = false
                    -- something might be in the way
                    self.knifing = true
                    --
                    self.requested_target_id = -1
                    self.crouching = false

                else
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAJump, 0.0)
                    self.jumping = false
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIASprint, 0.0)
                    self.sprinting = false
                    -- 
                    self.knifing = false
                end
                self.last_position = self.player_controller.soldier.transform.trans:Clone()
                self.last_position_check_time = SharedUtils:GetTime()
            
            end
            if (SharedUtils:GetTime() - self.last_long_position_check_time) > 5.0 then
                local myXYTrans = Vec3(self.player_controller.soldier.transform.trans.x, 1.0, self.player_controller.soldier.transform.trans.z)
                if myXYTrans:Distance(Vec3(self.long_last_position.x, 1.0, self.long_last_position.z)) < 2.0 then
                    -- self.path = {}
                    -- self.path_step = 1
                    self.path_step = math.huge
                    self.lock_path = false
                    self.destination = nil
                    self.throttle = false
                    self.target = nil
                    self.requested_target_id = -1
                    self.jumping = false
                    self.knifing = false
                    self.crouching = false
                end
                self.last_position = self.player_controller.soldier.transform.trans:Clone()
                self.last_long_position_check_time = SharedUtils:GetTime()
            end
            

            
        elseif self.path_step >= #self.path then
            -- print("Nullifying path")
            self.path = {}
            self.path_step = 1
            -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAThrottle, 0)
            self.throttle = false
            self.destination = nil
            self.lock_path = false
            self.jumping = false
            finished = true
        end

    end

    return finished
end

function Bot:StepPathNew()
    local finished = false

    if #self.path > 0 and self.path ~= nil and not (self.path_step >= #self.path) then
        if self.path[self.path_step] ~= nil then
            self.destination = self.path[self.path_step]:Clone()
            local is_at_path, is_outside_path = self:IsAtDestination()
            if is_at_path and not is_outside_path then
                self.path_step = self.path_step + 1
                self.lock_path = false
            end
            self.throttle = true
            self.sprinting = true
        end
        
        
    elseif self.path_step >= #self.path then
        self.path = {}
        self.path_step = 1
        self.throttle = false
        self.sprinting = false
        finished = true
    else
        self.throttle = false
        self.sprinting = false
        self.path_step = 1
    end
    return finished
end

function Bot:GetClosestPathPoint(point)
    local min_distance = 98999
    local min_point = nil
    for _, path_point in pairs(self.path) do
        local dist = path_point:Distance(point)
        if (dist < min_distance) then
            min_distance = dist
            min_point = path_point
        end
    end
    return min_point, min_distance
end

function Bot:StepPathVehicle()
    local front_probe_entity = self.player_controller.controlledControllable
    local reverse = false
    local yaw = 0.0
    local momentum = 0.7
    if (front_probe_entity ~= nil) then
        local front_probe = front_probe_entity.transform.trans + (front_probe_entity.transform.forward * 4)
        local back_probe = front_probe_entity.transform.trans + (front_probe_entity.transform.forward * -3)
        local front_probe_left = front_probe + (front_probe_entity.transform.left * 3)
        -- get nearest path point
        local nearest_point, nearest_point_distance = self:GetClosestPathPoint(front_probe)
        local nearest_point_left, nearest_point_left_distance = self:GetClosestPathPoint(front_probe_left)
        local nearest_point_back, nearest_point_back_distance = self:GetClosestPathPoint(back_probe)
        
        local steady_momentum = 0.2
        local steer_momentum = 2
        local invert_steer = false
        
        local forwardLevelEnum = EntryInputActionEnum.EIAThrottle
        
        if (nearest_point ~= nil and nearest_point_left ~= nil) then
            self.botVehicleController.moving = true
            -- print('nearest point valid. '..nearest_point_distance..' '..nearest_point_left_distance..' '..nearest_point_back_distance)
            if nearest_point_back_distance  < nearest_point_distance and nearest_point_distance > 10 then
                -- momentum = -1.0
                -- steady_momentum = -0.8
                reverse = true
                invert_steer = true
                -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAThrottle, 0)
                forwardLevelEnum = EntryInputActionEnum.EIABrake
                self.botVehicleController.reversing = true
            else
                -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIABrake, 0)
                self.botVehicleController.reversing = false
            end
            if nearest_point_distance < nearest_point_left_distance then
                -- self.player_controller.input:SetLevel(forwardLevelEnum, momentum)
                
                if invert_steer then
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAYaw, (nearest_point_distance/-steer_momentum))
                    yaw = nearest_point_distance/-steer_momentum
                else
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAYaw, (nearest_point_distance/steer_momentum))
                    yaw = nearest_point_distance/steer_momentum
                end
            elseif nearest_point_distance < 0.6 then
                -- self.player_controller.input:SetLevel(forwardLevelEnum, steady_momentum)
                momentum = steady_momentum
                --self.player_controller.input:SetLevel(EntryInputActionEnum.EIAYaw, 0)
                yaw = 0
            else
                -- self.player_controller.input:SetLevel(forwardLevelEnum, momentum)
                if invert_steer then
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAYaw, (nearest_point_distance/steer_momentum))
                    yaw = nearest_point_distance/steer_momentum
                else
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAYaw, (nearest_point_distance/-steer_momentum))
                    yaw = nearest_point_distance/-steer_momentum
                end
            end
            
        else
            self.botVehicleController.moving = false
            -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAThrottle, 0)
            -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAYaw, 0)
            -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIABrake, 0)
        end

    end

    if self.botVehicleController.moving == false then
        self.player_controller.input:SetLevel(EntryInputActionEnum.EIAThrottle, 0)
        self.player_controller.input:SetLevel(EntryInputActionEnum.EIAYaw, 0)
        self.player_controller.input:SetLevel(EntryInputActionEnum.EIABrake, 0)
    else
        if self.botVehicleController.reversing then
            self.player_controller.input:SetLevel(EntryInputActionEnum.EIABrake, self.botVehicleController.momentum)
            self.player_controller.input:SetLevel(EntryInputActionEnum.EIAThrottle, 0)
        else
            self.player_controller.input:SetLevel(EntryInputActionEnum.EIAThrottle, self.botVehicleController.momentum)
            self.player_controller.input:SetLevel(EntryInputActionEnum.EIABrake, 0)
        end
    end

    self.botVehicleController:Update(yaw, momentum, self.delta_time)

end

function Bot:GetAvailableSlotsForVehicle(_VehicleEntity) 
    -- cast
    local controllable = ControllableEntity(_VehicleEntity)
    local available = {}
    for s=0, controllable.entryCount do
        if controllable:GetPlayerInEntry(s) == nil then
            table.insert(available, s)
        end
    end

    return available
end

function Bot:InternalTick(deltaTime, pass)
    if pass ~= UpdatePass.UpdatePass_PostFrame then
		return
	end
    self.delta_time = deltaTime
    if self.player_controller ~= nil then
        if self.alive and self.player_controller.soldier ~= nil then
            self.player_controller.soldier:SingleStepEntry(self.player_controller.controlledEntryId)


            if self.throttle then
                self.player_controller.input:SetLevel(EntryInputActionEnum.EIAThrottle, 1.0)
            else
                self.player_controller.input:SetLevel(EntryInputActionEnum.EIAThrottle, 0.0)
            end
            if self.sprinting then
                self.player_controller.input:SetLevel(EntryInputActionEnum.EIASprint, 1.0)
            else
                self.player_controller.input:SetLevel(EntryInputActionEnum.EIASprint, 0.0)
            end
            if self.jumping then
                if math.random(0, 100) > 75 then
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAJump, 1.0)
                else
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAJump, 0.0)
                end
            else
                self.player_controller.input:SetLevel(EntryInputActionEnum.EIAJump, 0.0)
            end
            if self.firing then
                if self.aimWhenFire then
                    self.aiming = true
                end
                if math.random(100) > self.fireProbabilityPerTick then
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 1)
                else
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 0)
                end
            else
                self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 0)
                if self.aimWhenFire then
                    self.aiming = false
                end
            end

            if self.aiming then
                self.player_controller.input:SetLevel(EntryInputActionEnum.EIAZoom, 1)
            else
                self.player_controller.input:SetLevel(EntryInputActionEnum.EIAZoom, 0)
            end

            if self.crouching then
                self.player_controller.input:SetLevel(EntryInputActionEnum.EIAClutch, 1)
            else
                self.player_controller.input:SetLevel(EntryInputActionEnum.EIAClutch, 0)
            end

            if self.is_providing then
                self:SetActiveWeaponSlot(3)
            else
                if self.is_secondary then
                    self:SetActiveWeaponSlot(0)
                else
                    self:SetActiveWeaponSlot(-1)
                end
            end
            
            if (SharedUtils:GetTime() - self.last_path_reset_time) >= 5.0 then
                self.lock_path = false
                self.last_path_reset_time = SharedUtils:GetTime()
            end

            if (self.player_controller.attachedControllable ~= nil) then
                if self.player_controller.attachedControllable:Is("SoldierEntity") then
                    self.in_vehicle = false
                end
            else
                self.in_vehicle = false
            end

            if (self.knifing) then
                if math.random(10) > 5 then
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIASelectWeapon7, 1.0)
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIASelectWeapon1, 0.0)
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIASelectWeapon2, 0.0)
                    self:SetActiveWeaponSlot(6)
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 1)
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAQuicktimeFastMelee, 1);
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAMeleeAttack, 1);
                    --print("Knifing..")

                else
                   -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIASelectWeapon7, 0.0)
                   -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIASelectWeapon0, 1.0)
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 0)
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAQuicktimeFastMelee, 0);
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAMeleeAttack, 0);
                end
                self.knifingGate = true
            else
                if self.knifingGate then
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAMeleeAttack, 0.0)
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIASelectWeapon7, 0.0)
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIASelectWeapon1, 1)
                    self:SetActiveWeaponSlot(0)
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 0)
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAQuicktimeFastMelee, 0);
                    self.player_controller.input:SetLevel(EntryInputActionEnum.EIAMeleeAttack, 0);
                    self.knifingGate = false
                end
            end


            -- if self.target ~= nil then
            --     if self.target.alive and self.action == Actions.ATTACK then
            --         self:SetFocusOn(self.target.soldier.transform.trans:Clone())
            --         if self.player_controller.soldier.transform.trans:Distance(self.target.soldier.transform.trans:Clone()) < 15 then
            --             self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 1)
            --             self:SetFocusOn(self.target.soldier.transform.trans:Clone())
            --         else
            --             self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 0)
            --             if self.destination ~= nil then
            --                 if self.cached_destination ~= self.destination then
            --                     self.cached_destination = self.destination:Clone()
            --                 end
            --                 self:SetFocusOn(self.cached_destination)
            --                 
            --             end
            --         end
            --     else
            --         self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 0)
            --         if self.action == Actions.ATTACK then
            --             self.target = nil
            --         elseif self.action == Actions.GET_IN and self.destination ~= nil then
            --             if self.cached_destination ~= self.destination then
            --                 self.cached_destination = self.destination:Clone()
            --             end
            --             self:SetFocusOn(self.cached_destination)
            --         end
            --     end
            -- 
            -- elseif self.destination ~= nil then
            --     if self.cached_destination ~= self.destination then
            --         self.cached_destination = self.destination:Clone()
            --     end
            --     self:SetFocusOn(self.cached_destination)
            --     
            -- end
        end
    end

    -- self:Tick(deltaTime, pass)
    self:NewTick(deltaTime, pass)
end

function Bot:SetActiveWeaponSlot(slot)
    local offset = slot + 16
    local slots = {16, 17, 18, 19, 20, 21, 22, 23, 24}
    for _, slotIndex in pairs(slots) do
        if slotIndex == offset then
            self.player_controller.input:SetLevel(slotIndex, 1.0)
        else
            self.player_controller.input:SetLevel(slotIndex, 0.0)
        end
    end
end

function Bot:NewTick(delta_time, pass)
    if self.player_controller ~= nil then
        if self.alive and self.player_controller.alive and self.player_controller.soldier ~= nil then
            if self.action == Actions.ATTACK then
                if not self.in_vehicle then
                    self:StepPathNew()
                    if self.destination ~= nil then
                        self:SetFocusOn(self.destination)
                        -- print('Focusing on: '..self.destination.x..' '..self.destination.y..' '..self.destination.z)
                    end
                else
                    self:StepPathVehicle()
                end
            elseif self.action == Actions.VEHICLE_DISCOVERY then
                local atDestination = self:StepPathNew()
                if self.destination ~= nil then
                    self:SetFocusOn(self.destination)
                end
                if atDestination and self.target_vehicle ~= nil then
                    self.player_controller:EnterVehicle(self.target_vehicle, self.player_controller.controlledEntryId )
                    self.in_vehicle = true
                    self.requested_action = 2
                    self.requested_order = 2
                end
            end
        else
            if not self.player_controller.alive then
                self.requested_respawn = true
            end
        end
    end
end

function Bot:Tick(delta_time, pass)
    -- if pass ~= UpdatePass.UpdatePass_PostFrame then
	-- 	return
	-- end
    if self.player_controller ~= nil then
        if self.alive and self.player_controller.alive then
            if self.player_controller.soldier == nil then
                return
            end
            if (self.player_controller.id == 2) then
                if (self.in_vehicle) then
                    -- do something here
                end
            end
            self.requested_respawn = false
            if self.action == Actions.NONE then
            
            elseif self.action == Actions.PROVIDE or self.action == Actions.PROVIDE_HEALTH or self.action == Actions.PROVIDE_AMMO then
                local isAtLocation = self:StepPath()
                if isAtLocation then
                    self:DropProvider()
                    self.requested_order = 2
                    self.requested_action = 2
                end

            elseif self.action == Actions.GET_IN and not self.in_vehicle then
                local isAtLocation = self:StepPath()
                if self.target ~= nil then
                    if self.target.soldier == nil then
                        self.target = nil
                    end
                else
                    self.requested_action = Actions.ATTACK
                end
                if self.target ~= nil then
                    if isAtLocation or self.player_controller.soldier.transform.trans:Distance(self.target.soldier.transform.trans) < 1.5 then
                        if self.target.alive then
                            local availableSlots = self:GetAvailableSlotsForVehicle(self.target.attachedControllable)
                            if #availableSlots > 0 and not self.in_vehicle then
                                local vehicleData = VehicleEntityData(self.target.attachedControllable.data)
                                self.player_controller:EnterVehicle(self.target.attachedControllable, self.player_controller.controlledEntryId )-- availableSlots[math.random(1, #availableSlots)])--vehicleData.maxPlayersInVehicle))
                                print("Enter Vehicle. "..vehicleData.maxPlayersInVehicle.. " "..self.target.attachedControllable.typeInfo.name)
                                self.requested_action = 2
                                self.requested_order = 2
                                self.action = 2
                                self.order = 2
                                self.in_vehicle = true
                            else
                                self.requested_action = Actions.ATTACK
                                if not self.in_vehicle then
                                    self.target = nil
                                end
                            end
                        end 
                    end
                end
            
            elseif self.action == Actions.GET_OUT then
                self.player_controller:ExitVehicle(true, true)
                -- self.requested_action = Actions.ATTACK
                self.target = nil
                self.in_vehicle = false
                self.requested_action = 2
                self.requested_order = 2

            elseif self.action == Actions.ATTACK and not self.in_vehicle then
                if not self.stopMoving then
                    local isAtLocation = self:StepPath()
                end
                if (self.player_controller.id == 2) then
                   -- print("bot moving")
                end

            elseif self.action == Actions.ATTACK and self.in_vehicle then
                self:StepPathVehicle()
            end

            if self.target ~= nil and not self.in_vehicle and self.action == Actions.ATTACK then
                if self.target.alive and self.action == Actions.ATTACK then
                    if self.target.soldier.transform.trans:Distance(self.target.soldier.transform.trans:Clone()) > 30 then
                        self.target = nil
                        self.firing = false
                        self.knifing = false
                        return
                    end
                    local focus = self:GetLocalOffsetTransform(self.target.soldier.transform)
                    local shouldStop = self.player_controller.soldier.transform.trans:Distance(self.target.soldier.transform.trans:Clone()) > 3 and math.random(0, 100) > 15

                    -- self:SetFocusOn(focus.trans)

                    if self.player_controller.soldier.transform.trans:Distance(self.target.soldier.transform.trans:Clone()) < 15 and not shouldStop then
                        -- self.knifing = false
                        self.firing = true
                        self.crouching = false
                        self.stopMoving = false
                        -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 1)
                        self:SetFocusOn(self.cached_destination)

                    elseif self.player_controller.soldier.transform.trans:Distance(self.target.soldier.transform.trans:Clone()) < 15 and shouldStop then
                        self.knifing = false
                        self.firing = true
                        self.throttle = false
                        self.sprinting = false
                        self.crouching = true
                        self.stopMoving = true
                        self:SetFocusOn(focus.trans)
                        
                    else
                        self.firing = false
                        self.crouching = false
                        self.stopMoving = false
                        -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 0)
                        if self.destination ~= nil then
                            if self.cached_destination ~= self.destination then
                                self.cached_destination = self.destination:Clone()
                            end
                            self:SetFocusOn(self.cached_destination)
                        end
                    end
                else
                    -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIAFire, 0)
                    self.firing = false
                    self.stopMoving = false
                    self.crouching = false
                    if self.action == Actions.ATTACK then
                        self.target = nil
                    elseif self.action == Actions.GET_IN and self.destination ~= nil then
                        if self.cached_destination ~= self.destination then
                            self.cached_destination = self.destination:Clone()
                        end
                        self:SetFocusOn(self.cached_destination)
                    end
                end
            
            elseif self.destination ~= nil then
                if self.cached_destination ~= self.destination then
                    self.cached_destination = self.destination:Clone()
                end
                if ((not self.firing) or self.target == nil) then
                    self:SetFocusOn(self.cached_destination)
                end
                
            end
        else
            self.requested_respawn = true
        end

        -- if not self.player_controller.alive then
        --     self.requested_respawn = true
        -- end
    end
end

function Bot:SetFocusOnEntity(TargetEntity)
    local bot_trans = self.player_controller.soldier.transform.trans
    local bot_transform = self.player_controller.soldier.transform
    bot_transform:LookAtTransform(bot_trans, 
        Vec3(
            TargetEntity.transform.trans.x,
            TargetEntity.transform.trans.y,
            TargetEntity.transform.trans.z
        )
    )
    self.player_controller.soldier.transform = bot_transform
end

function Bot:SetFocusOnTransform(TargetTransform)
    local bot_trans = self.player_controller.soldier.transform.trans
    local bot_transform = self.player_controller.soldier.transform
    bot_transform:LookAtTransform(bot_trans, 
        Vec3(
            TargetTransform.trans.x,
            TargetTransform.trans.y,
            TargetTransform.trans.z
        )
    )
    self.player_controller.soldier.transform = bot_transform
end

function Bot:SetFocusOn(Target)
    local bot_trans = self.player_controller.soldier.transform.trans
    local bot_transform = self.player_controller.soldier.transform:Clone()
    bot_transform:LookAtTransform(bot_trans, 
        Target
    )
    self.player_controller.soldier.transform = bot_transform
end

function Bot:Destroy()
    self.__input = nil
    self.soldier = nil
    self:Reset()
    self:Kill()
    PlayerManager:DeletePlayer(self.player_controller)
end

function Bot.createBot(manager, name, team, squad)
    local self = Bot()
    self.bot_index = (#manager.bots) + 1
    self.player_controller = PlayerManager:CreatePlayer("ImABot"..tostring(self.bot_index), team, squad)
    
    -- this will be moved to the player controller
    self.__input = EntryInput()
    self.__input.deltaTime = 1.0 / SharedUtils:GetTickrate()
    -- self.__input.flags = EntryInputFlags.AuthoritativeMovement
    -- self.__input.flags = EntryInputFlags.AuthoritativeAiming
    self.player_controller.input = self.__input
    
    -- keep track of our bot
    
    table.insert(manager.bots, self)

    return self

end

function Bot:KillNullSoldier()
    local soldierIterator = EntityManager:GetIterator('SoldierEntity')

    local soldierEntity = (soldierIterator:Next())
    while soldierEntity ~= nil do
        soldierEntity = SoldierEntity(soldierEntity)
        print('iterating soldiers... '..tostring(soldierEntity.player.name))
        if soldierEntity.player == nil then
            soldierEntity:ForceDead()
            if soldierEntity.isAlive or soldierEntity ~= nil then
                soldierEntity:Kill()
            end
            print("Destroying soldier with NULL player")
        elseif soldierEntity.player then
            if soldierEntity.player.id == self.player_controller.id then
                soldierEntity:ForceDead()
                if soldierEntity.isAlive or soldierEntity ~= nil then
                    soldierEntity:Kill()
                end
                self.soldier = nil
                print("Destroying soldier with player")
            end
        end
        soldierIterator:Next()
    end
    
end


function Bot:SpawnBot(transform, pose, soldierBP, inKit, unlocks, spawnEntity)
    local kit = ''

    -- soldierBlueprint = ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))
    -- soldierKit = ResourceManager:SearchForInstanceByGuid(Guid('A15EE431-88B8-4B35-B69A-985CEA934855'))
    if transform == nil then
        print("transform is nil")
    elseif pose == nil then
        print("pose is nil")
        return
    elseif soldierBP == nil then
        print("soldierBP is nil")
        -- return
        if self.soldierBP == nil then
            self.soldierBP = ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))
        end
        soldierBP = self.soldierBP
    elseif kit == nil then
        print("kit is nil")
    elseif unlocks == nil then
        print("unlocks is nil")
    end

    -- print("Checking if soldier is alive")
    if self.player_controller.soldier ~= nil then
        print("destroying soldier as it exists...")
        self.player_controller.soldier:Kill()
        if self.player_controller.soldier then
            self.player_controller.soldier:Destroy()
        end
        self.soldier =  nil
        self.alive = false
    end

    self.lock = true

    --print("Setting unlockAssets")
    local customization  = CustomizeSoldierData()
    if self.set_unlocks == false then
        -- self.selected_kit = nil
        if self.selected_kit ~= nil then
            local primaryWeapon = nil
            local primaryWeaponAttachments = {}
            if self.selected_kit.primary_weapon ~= nil then
                -- print('adding primary weapon: '..self.selected_kit.primary_weapon.path)
                primaryWeapon = ResourceManager:SearchForDataContainer(self.selected_kit.primary_weapon.path)
                if #self.selected_kit.primary_weapon.children > 0 then
                    for _, child in pairs(self.selected_kit.primary_weapon.children) do
                        local attachment = ResourceManager:SearchForDataContainer(child.path)
                        if attachment == nil then
                            print("Nil primary attachment: "..child.path)
                        else
                            if attachment:Is("UnlockAssetBase") then
                                table.insert(
                                    primaryWeaponAttachments, UnlockAssetBase(attachment)
                                )
                            end
                        end
                    end
                end
            end
            local secondaryWeapon = nil
            local secondaryWeaponAttachments = {}
            if self.selected_kit.secondary_weapon ~= nil then
                secondaryWeapon = ResourceManager:SearchForDataContainer(self.selected_kit.secondary_weapon.path)
                if #self.selected_kit.secondary_weapon.children > 0 then
                    for _, child in pairs(self.selected_kit.secondary_weapon.children) do
                        local attachment = ResourceManager:SearchForDataContainer(child.path)
                        if attachment == nil then
                            print("Nil secondary attachment: "..child.path)
                        else
                            if attachment:Is("UnlockAssetBase") then
                                table.insert(
                                    secondaryWeaponAttachments, UnlockAssetBase(attachment)
                                )
                            end
                        end
                    end
                end
            end
            local primaryGadget = nil
            if self.selected_kit.primary_gadget ~= nil then
                primaryGadget = ResourceManager:SearchForDataContainer(self.selected_kit.primary_gadget.path)
                if self.selected_kit.primary_gadget.name == 'U_Ammobag' then
                    self.provides_ammo = true
                    self.provides_ammo_slot = 4
                elseif self.selected_kit.primary_gadget.name == 'U_Medkit' then
                    self.provides_health = true
                    self.provides_health_slot = 4
                end
            end
            local secondaryGadget = nil
            if self.selected_kit.secondary_gadget ~= nil then
                secondaryGadget = ResourceManager:SearchForDataContainer(self.selected_kit.secondary_gadget.path)
                if self.selected_kit.secondary_gadget.name == 'U_Ammobag' then
                    self.provides_ammo = true
                    self.provides_ammo_slot = 5
                elseif self.selected_kit.secondary_gadget.name == 'U_Medkit' then
                    self.provides_health = true
                    self.provides_health_slot = 5
                end
            end
            local melee = nil
            if self.selected_kit.melee ~= nil then
                melee = ResourceManager:SearchForDataContainer(self.selected_kit.melee.path)
            end
            if (self.selected_kit.unlocks ~= nil) then
                unlocks = ResourceManager:SearchForDataContainer(self.selected_kit.unlocks.path)
            end
            if (self.selected_kit.kit_asset ~= nil) then
                kit = ResourceManager:SearchForDataContainer(self.selected_kit.kit_asset.path)
            end

            

            -- now mount these weapons
            if primaryWeapon ~= nil then
                local primaryWeaponSlot = UnlockWeaponAndSlot()
                primaryWeaponSlot.slot = 0
                primaryWeaponSlot.weapon = SoldierWeaponUnlockAsset(primaryWeapon)
                local pUnlocks = {}
                for _, uA in pairs(primaryWeaponAttachments) do
                    primaryWeaponSlot.unlockAssets:add(uA)
                    table.insert(pUnlocks, uA)
                end
                customization.weapons:add(primaryWeaponSlot)

                self.player_controller:SelectWeapon(
                    WeaponSlot.WeaponSlot_0,  primaryWeapon, pUnlocks
                )
                print("Successfully set primary weapon")
            end
            if secondaryWeapon ~= nil then
                local secondaryWeaponSlot = UnlockWeaponAndSlot()
                secondaryWeaponSlot.slot = 1
                secondaryWeaponSlot.weapon = SoldierWeaponUnlockAsset(secondaryWeapon)
                local sUnlocks = {}
                for _, uA in pairs(secondaryWeaponAttachments) do
                    secondaryWeaponSlot.unlockAssets:add(uA)
                    table.insert(sUnlocks, uA)
                end
                
                customization.weapons:add(secondaryWeaponSlot)
                self.player_controller:SelectWeapon(
                    WeaponSlot.WeaponSlot_1,  secondaryWeapon, sUnlocks
                )
                print("Successfully set secondary weapon")
            end
            if primaryGadget ~= nil then
                local primaryGadgetSlot = UnlockWeaponAndSlot()
                if self.provides_health and self.provides_health == 4 or self.provides_ammo and self.provides_ammo_slot == 4 then
                    primaryGadgetSlot.slot = 4
                else
                    primaryGadgetSlot.slot = 2
                end
                primaryGadgetSlot.weapon = SoldierWeaponUnlockAsset(primaryGadget)
                customization.weapons:add(primaryGadgetSlot)
            end
            if secondaryGadget ~= nil then
                local secondaryGadgetSlot = UnlockWeaponAndSlot()
                secondaryGadgetSlot.slot = 5
                secondaryGadgetSlot.weapon = SoldierWeaponUnlockAsset(secondaryGadget)
                customization.weapons:add(secondaryGadgetSlot)
            end
            if melee ~= nil then
                local meleeSlot = UnlockWeaponAndSlot()
                meleeSlot.slot = 7
                meleeSlot.weapon = SoldierWeaponUnlockAsset(melee)
                customization.weapons:add(meleeSlot)
            end

            if (kit ~= nil and unlocks ~= nil) then
                print("kit and unlocks valid: "..self.selected_kit.kit_asset.path..' '..self.selected_kit.unlocks.path .. tostring(kit))
                self.player_controller:SelectUnlockAssets(kit, {unlocks})
            end
        else
        --     
        --     local weapon = ResourceManager:SearchForInstanceByGuid(Guid('96FC0A67-DEA2-4061-B955-E173A8DBB00D'))
        --     
        --     local weapon0    = ResourceManager:SearchForDataContainer('Weapons/M416/U_M416')
	    --     local weaponAtt0 = ResourceManager:SearchForDataContainer('Weapons/M416/U_M416_ACOG')
        --     local weaponAtt1 = ResourceManager:SearchForDataContainer('Weapons/M416/U_M416_Silencer')
        --     
	    --     local weapon1    = ResourceManager:SearchForDataContainer('Weapons/XP1_L85A2/U_L85A2')
	    --     local weaponAtt2 = ResourceManager:SearchForDataContainer('Weapons/XP1_L85A2/U_L85A2_RX01')
        --     local weaponAtt3 = ResourceManager:SearchForDataContainer('Weapons/XP1_L85A2/U_L85A2_Silencer')
        --     
        --     local weaponSlotAssetPrimary = UnlockWeaponAndSlot()
        --     weaponSlotAssetPrimary.slot = 0
        --     weaponSlotAssetPrimary.weapon = SoldierWeaponUnlockAsset(weapon0)
        --     -- weaponSlotAssetPrimary.unlockAssets = { weaponAtt0, weaponAtt1 }
-- 
        --     local weaponSlotAssetSecondary = UnlockWeaponAndSlot()
        --     weaponSlotAssetSecondary.slot = 0
        --     weaponSlotAssetSecondary.weapon = SoldierWeaponUnlockAsset(weapon0)
        --     -- weaponSlotAssetSecondary.unlockAssets = { weaponAtt0, weaponAtt1 }
        --     
        --     customization.weapons:add(weaponSlotAssetPrimary)
        --     customization.weapons:add(weaponSlotAssetSecondary)
        --     local myPlayer = PlayerManager:GetPlayerById(0)
        --     -- self.player_controller:SelectUnlockAssets(kit, myPlayer.visualUnlocks)
        --     -- self.player_controller:SelectWeapon(
        --     --     WeaponSlot.WeaponSlot_0, weapon0, {weaponAtt0, weaponAtt1}
        --     -- )
        --     -- self.player_controller:SelectWeapon(
        --     --     WeaponSlot.WeaponSlot_1, weapon1, {weaponAtt2, weaponAtt3}
        --     -- )
        --     print(myPlayer.selectedUnlocks[2])
        --     print(myPlayer.weapons[2])
            return nil
        end
        self.set_unlocks = false
        

    end 

    self:Reset()

   -- print("Creating soldier")
    local soldier = self.player_controller:CreateSoldier(soldierBP, transform)
    if soldier == nil then
        print("Soldier failed to create "..tostring(self.player_controller.name))
        self.requested_respawn = true
        -- self:KillNullSoldier()
        if self.soldier then
            self.soldier:Kill()
        end
        if self.player_controller.soldier then
            self.player_controller.soldier:ForceDead()
            self.player_controller.soldier:Kill()
            
        end
        self.soldier = nil
        return nil
    else
        print("Spawning soldier for ".. tostring(self.player_controller.name))
        --print("Attaching Soldier")
        
        if spawnEntity ==  nil then
            self.player_controller:SpawnSoldierAt(soldier, transform, pose)
        else
            self.player_controller:Spawn(spawnEntity, true)
        end
        self.player_controller:AttachSoldier(soldier)
        
        -- self.player_controller.input:SetLevel(EntryInputActionEnum.EIASelectWeapon3, 1)
        self.alive = true
        self.soldier = soldier 
        self.player_controller.soldier:ApplyCustomization(customization)
        self.player_controller.input:SetLevel(EntryInputActionEnum.EIASelectWeapon1, 1)

        self.player_controller.soldier.detailedCollisionEnabled = true
        self.player_controller.soldier.physicsEnabled = true
        local data = SoldierEntityData(self.player_controller.soldier.data)
        -- if (data.humanPlayerControlled) then
        --     print("Is Soldier Human Controlled? ", data.humanPlayerControlled)
        -- end
        -- if (data.collisionEnabled) then
        --     print("Is Soldier Collision Enabled? ", data.collisionEnabled)
        -- end
        -- if (data.physicsControlled) then
        --     print("Is Soldier PhysicsControlled? ", data.physicsControlled)
        -- end
        data:MakeWritable()
        data.humanPlayerControlled = false
        data.collisionEnabled = true
        data.physicsControlled = true
        if self.player_controller.soldier == nil then
            print("Failed to attach, killing...")
            self.alive = false
            self.soldier:Kill()
            self.soldier = nil
            return nil
        end
        -- Events:Dispatch('Player:Respawn', self.player_controller.soldier)
    end
    
    
    -- if self.nav_grid == nil then
    --     self.nav_grid = NavGrid.Create(self.soldier.transform)
    --     self.nav_grid:UpdateScores()
    --     if self.order == Orders.ATTACK_OBJECTIVE and self.objective ~= nil then
    --         self.nav_grid:GetPathTo(self.player_controller.soldier.transform.trans, self.objective.transform.trans)
    --     elseif self.order == Orders.ATTACK_ENEMIES and self.target ~= nil then
    --         self.nav_grid:GetPathTo(self.player_controller.soldier.transform.trans, self.target.transform.trans)
    --     end
    --     self.path_step = 1
    -- end
    self.spawned = true
    return self.soldier
end

function Bot:Reset()
    self.target = nil
    self.sprinting = false
    self.jumping = false
    self.firing = false
    self.aiming = false
    self.crouching = false
    self.knifing = false
    self.path = {}
    self.requested_action = Actions.ATTACK
    self.requested_order = Orders.ENEMY
    self.in_vehicle = false
    self.stopMoving = false
    self.action = Actions.ATTACK
    self.order = Orders.ENEMY
end

function Bot:Kill()
    if self.player_controller.soldier ~= nil then
        self.player_controller.soldier:Kill()        
        self.soldier =  nil
        self.alive = false
        self:Reset()
    end
end


if g_Bot == nil then
    g_Bot = Bot()
end

return g_Bot