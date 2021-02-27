


function string:split(sep)
    local sep, fields = sep or ":", {}
    local pattern = string.format("([^%s]+)", sep)
    self:gsub(pattern, function(c) fields[#fields + 1] = c end)
    return fields
end







class 'ScorecardBaseServer'
local NavGrid = require('__shared/NavGrid')
local botsManager = require("BotsManager")
local scorecardServer = require("ScorecardServer")

require('ScorecardServerSettings')



-- Hooks:Install('EntityFactory:CreateFromBlueprint', 100, function(hookCtx, blueprint, transform, variation, parentRepresentative)
--     local createdBus = hookCtx:Call()
--     -- Do something with createdBus.
--     -- print("Loaded blueprint with ".. #createdBus.entities .." entities")
--     for _, entity in pairs(createdBus.entities) do
--         if entity:Is("GameEntity") then
--             local g = GameEntity(entity)
--             
--             NavGrid.AddCache(
--                 g,
--                 AxisAlignedBox(
--                     g.transform * g.aabb.min,
--                     g.transform * g.aabb.max
--                 )
--             )
--         end
--     end
-- end)

-- SoldierEntity : DamageInfo : (DamageGiverInfo | nil)
Hooks:Install('Soldier:Damage', 1, function(hook, soldier, info, giverInfo)
    if soldier ~= nil then
        local bot = botsManager:GetBotFromSoldier(soldier)
        if bot ~= nil and giverInfo ~= nil then
            if giverInfo.giver ~= nil then
                bot.requested_target_id = giverInfo.giver.id
                bot.requested_order = 3
                bot.requested_action = 2
            end
        end
    end
end)
-- 
-- Hooks:Install('BulletEntity:Collision', 1, function(hook, entity, hit, giverInfo)
--     -- hook:Call()
--     -- TODO: need to find a way to get the bots to apply damage, without workarounds like this.
--     -- I don't think you can call engine events
--     --print(entity)
--     if (hit.rigidBody) then
--         --print(hit.rigidBody)
--     end
--     local bdata = BulletEntityData(entity.data)
--     --print('serverProjectileDisabled: '..tostring(bdata.serverProjectileDisabled))
--     bdata:MakeWritable()
--     bdata.serverProjectileDisabled = false
--     bdata.instantHit = true
--     bdata.impactImpulse = 5.0
--     -- hook:Pass(entity, hit, giverInfo)
--     if entity ~= nil then
--         local bullet = SpatialEntity(entity)
--         local bullet_data = BulletEntityData(entity.data)
--         local start_damage = bullet_data.startDamage
--         if hit ~= nil then
--             if hit.rigidBody then
-- 
--                 if giverInfo.giver ~= nil then
--                     local hitPlayer = botsManager:GetNearestPlayer(hit.position, giverInfo.giver.teamId, false)
--                     if botsManager:IsABot(giverInfo.giver) and hitPlayer and hitPlayer.soldier.transform.trans:Distance(hit.position) < 2.0 then
--                         local soldier = hitPlayer.soldier
--                         if soldier.health - start_damage <= 0.0 then
--                             local giver = PlayerManager:GetPlayerById(giverInfo.giver.id)
--                             local victim = PlayerManager:GetPlayerById(soldier.player.id)
--                             -- local giver = botsManager:GetBotThatTargets(victim)
--                             if giver ~=nil then
--                                 -- giver = giver.player_controller
--                                 -- Events:Dispatch("Player:Killed", victim, giver, bullet.transform.trans, "test", false, false, false, giverInfo)
--                                 -- print("Dispatched event ")
--                                 -- giver.kills = giver.kills + 1
--                                 print("victim ".. tostring(victim))
--                                 print("giver ".. tostring(giver))
--                                 print('giverInfo '.. tostring(giverInfo.giver.name))
--                                 print('firing event')
--                                 local event = ServerPlayerEvent('ManDown',giver, false, false, false, false, false, false, giver.teamId)
--                                 victim.soldier:FireEvent(event)
--                                 print('fired eevnt')
--                             else
--                                 -- print("giver is invalid!! ")
--                                 -- print("victim".. victim)
--                             end
--                         else
--                             soldier.health = soldier.health - start_damage
--                             --local info = DamageInfo()
--                             --info.position = soldier.transform.trans
--                             --info.direction = Vec3(0,0,0)
--                             --info.origin = giverInfo.giver.soldier.transform.trans
--                             --info.damage = 20
--                             --info.isBulletDamage = true
--                             --info.isClientDamage = false
--                             --info.shouldForceDamage = true
--                             --info.includesChildren = true
-- --
--                             --soldier:ApplyDamage(
--                             --    info
--                             --)
--                         end
--                         
--                     end
--                 end
--             end
--         end
--     end
--     
-- end)

-- Hooks:Install('EntityFactory:CreateFromBlueprint', 100, function(hookCtx, blueprint, transform, variation, parentRepresentative)
--     hookCtx:Call()
--     print("create bp")
--     print(blueprint, blueprint.typeInfo.name, variation)
-- end)



Events:Subscribe('Soldier:ManDown', function(soldier, inflictor)
    -- Do stuff here.
    print("man down")
    print(soldier)
    print(inflictor)
end)