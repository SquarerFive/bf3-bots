class 'ScorecardServer'

local NavGrid = require('__shared/NavGrid')
local botsManager = require("BotsManager")

local encoded_scores = nil
local size_x = 0
local size_y = 0
local min_x = 0
local min_y = 0
local max_x = 0
local max_y = 0


function ScorecardServer:__init()
    NetEvents:Subscribe("OnScorecardEncoded", self, self.OnScorecardEncoded)
    NetEvents:Subscribe("OnScorecardError", self, self.OnScorecardError)
    NetEvents:Subscribe("OnScorecardMessage", self, self.OnScorecardMessage)
    NetEvents:Subscribe("OnScorecardCostModification", self, self.OnScorecardCostModification)
    NetEvents:Subscribe("OnScorecardRequestPath", self, self.OnScorecardRequestPath)
    NetEvents:Subscribe("OnSetActiveProject", self, self.OnSetActiveProject)
    NetEvents:Subscribe("OnUpdateBotSettings", self, self.OnScorecardUpdateBotSettings)
    Events:Subscribe('UpdateManager:Update', self, self.Tick)
    self.damageHook = nil
    self.damageInfo = nil
    self.damageGiverInfo = nil
    -- Events:Subscribe('Extension:Unloading', self, self.Destroy)
end

function ScorecardServer:OnScorecardUpdateBotSettings(player, newFiringOffset, newFiringBaseOffset, newAimWhenFire)
    print("Updating bot settings")
    for _, bot in pairs(botsManager.bots) do
        bot:UpdateAimSettings(newFiringOffset, newFiringBaseOffset, newAimWhenFire)
    end
end

function ScorecardServer:Tick(deltaTime, pass)
    -- if (self.damageHook ~= nil) then
    --     local firstPlayer = PlayerManager:GetPlayerById(0)
    --     print("valid damageHook "..firstPlayer.name)
    --     if firstPlayer.soldier ~= nil then
    --         print('applying damage')
    --         self.damageHook:Pass(firstPlayer.soldier, self.damageInfo, self.damageGiverInfo)
    --     end
    --     -- print("valid damageHook")
    -- end
end

function ScorecardServer:OnSetActiveProject(player, active_project, profile)
    botsManager.project_id = math.floor(tonumber(active_project))
    botsManager.profile = profile
end

function ScorecardServer:OnScorecardRequestPath(player, start_point, end_point)
    local path = botsManager:FindPath(start_point, end_point)
    NetEvents:SendTo("OnSetPath", player, path)
end

function ScorecardServer:OnScorecardEncoded(player, in_encoded_scores, in_size_x, in_size_y, in_min_x, in_min_y, in_max_x, in_max_y)
    print(player)
    print(#in_encoded_scores)
    encoded_scores = in_encoded_scores
    size_x = in_size_x
    size_y = in_size_y
    min_x = in_min_x
    min_y = in_min_y
    max_x = in_max_x
    max_y = in_max_y
    self:ProcessScorecardData()
end

function ScorecardServer:ProcessScorecardData()
    -- print(encoded_scores)

    local headers = {}
    local options = HttpOptions(headers, 90)
    options:SetHeader("Content-Type", "application/json")
    options:SetHeader("Content-Length", tostring(#encoded_scores))
    options:SetHeader("Size-X", tostring(size_x))
    options:SetHeader("Size-Y", tostring(size_y))
    options:SetHeader("Min-X", tostring(min_x))
    options:SetHeader("Min-Y", tostring(min_y))
    options:SetHeader("Max-X", tostring(max_x))
    options:SetHeader("Max-Y", tostring(max_y))
    options:SetHeader("name", SharedUtils:GetLevelName())


    local result = Net:PostHTTP("http://127.0.0.1:8000/pathfinding/", encoded_scores, options)
    print("Posted scores")
    if result then
        print(result.status)
        print(result.body)
    end
    local encoded_test = json.encode(Vec3(25.0, 15.0, 16.0))
    local test = Net:PostHTTP("http://127.0.0.1:8000/pathfinding/test/", encoded_test)
end

function ScorecardServer:OnScorecardError(player, error)
    print("[ERROR]:".." "..error)
end

function ScorecardServer:OnScorecardMessage(player, message)
    print(message)
end

function ScorecardServer:OnScorecardCostModification(player, recording_mode, sample_radius)
    local position = player.soldier.transform.trans
    local headers = {}
    local options = HttpOptions(headers, 32)
    options:SetHeader("Position", position.x..","..position.z)
    options:SetHeader("Elevation", tostring(position.y))
    options:SetHeader("Level-Name", SharedUtils:GetLevelName())
    options:SetHeader("Recording-Mode", tostring(recording_mode))
    options:SetHeader("Sample-Radius", tostring(sample_radius))
    local result = Net:GetHTTP("http://127.0.0.1:8000/pathfinding/modify/", options)
end

function ScorecardServer:GenerateScores(player)
    local transform = player.soldier.transform
    local s_Transform = LinearTransform(
			Vec3(-1.0, 0.0, 0.0), Vec3(0.0, 1.0, 0.0), Vec3(0.0, 0.0, 1.0),
			transform.trans
		)
    self.lastPlayer = player
    if s_Transform == nil then
       -- print("Transform is nil :(")
    end
    -- print("Server generating scores")
    local grid_ = NavGrid.Create(transform)
    grid_:UpdateScores()
    -- pseudo target test
    if c_target == nil then
        c_target = botsManager:GetNearestEnemyObjective(transform.trans, 1 )
    end 
    -- grid_:GetPathTo(transform.trans, c_target)
    -- print("Server score at 1, 1: ".. grid_.grid_scores[1][1])
    -- print("Generated path length: " .. #grid_.cached_path)
    NetEvents:SendTo("OnGeneratedScores", player, grid_.grid_scores, grid_.cached_path)
end

function ScorecardServer:Export()
    local result = Net:GetHTTP("http://127.0.0.1:8000/pathfinding/export/")
end
function ScorecardServer:Import(data_name, data_type)
    
    local headers = {}
    local options = HttpOptions(headers, 32)
    
    options:SetHeader("Level-Name", SharedUtils:GetLevelName())
    options:SetHeader("Name", tostring(data_name))
    options:SetHeader("Type", tostring(data_type))
    local result = Net:GetHTTP("http://127.0.0.1:8000/pathfinding/import/", options)
end

if g_ScorecardServer == nil then
    g_ScorecardServer = ScorecardServer()
end


Events:Subscribe('Player:Chat', function(player, recipientMask, message)
    local parts = string.lower(message):split(' ')
    local o_parts = message:split(" ")

    if parts[1] == "!fp2obj" then
        local end_point = botsManager:GetNearestEnemyObjective(player.soldier.transform.trans, player.teamId)
        local start_point =  player.soldier.transform.trans
        local path = botsManager:FindPath(start_point, end_point)
        NetEvents:SendTo("OnSetPath", player, path)

    end

    if parts[1] == "!showpath" then
        local bot_index = tonumber(o_parts[2])
        NetEvents:SendTo("OnSetPath", player, botsManager.bots[bot_index].path)
    end
    if parts[1] == "!hidepath" then
        NetEvents:SendTo("OnSetPath", player, nil)
    end
    if parts[1] == '!dcollision' then
        player.soldier:FireEvent('DisableCollision')
    end
    if parts[1] == '!kill' then
        player.soldier:FireEvent('EnableCollision')
        local event = ServerDoublePlayerEvent('Kill', player, player, false, false, false, false, false, false, player.teamId)
        player.soldier:FireEvent(event)
    end

    if parts[1] == '!mandown' then
        -- local event = ServerDoublePlayerEvent('ManDown', player, player, false, false, false, false, false, player.teamId)
        -- player.soldier:FireEvent(event)
        -- player.soldier:FireEvent('ManDown')
        local event = ServerPlayerEvent('ManDown', player, false, false, false, false, false, false, player.teamId)
        player.soldier:FireEvent(event)
    end

    if parts[1] == "!get_kit" then
        local kit_iguid = player.selectedKit.instanceGuid:ToString("D")
        local kit_pguid = player.selectedKit.partitionGuid
        local sl_guid = player.soldier.data.instanceGuid:ToString("D")
        -- print(kit_iguid)
        print(sl_guid)
        print(ResourceManager:SearchForInstanceByGuid(Guid(sl_guid)))
        print(ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2')))
        local sl_bguid = player.soldier.bus.data.instanceGuid:ToString("D")
        print('bus : ', sl_bguid)

        -- if kit_pguid ~= nil then
        --     print(kit_pguid:ToString("D"))
        -- end
    end

    if parts[1] == "!path" then
        print(g_ScorecardServer.m_name)
        -- botsManager.debug_target = player
        botsManager:CreateBot("SquarerSix", TeamId.Team1, SquadId.Squad1)
    end
    if parts[1] == "!add_bots" then
        local count = tonumber(o_parts[2])
        if count ~= nil then
            local t1count = 0
            local t2count = 0
            for i=0, count do
                local team = TeamId.Team1
                local bestcount = t1count
                if i % 2 == 0 then
                    team = TeamId.Team2
                    bestcount = t2count
                    t2count = t2count + 1
                else
                    t1count = t1count + 1
                end
                local squad = math.ceil(bestcount/4)+1
                botsManager:CreateBot("SquarerSix", team, squad)
            end
        end
    end
    if parts[1] == "!spobj" then
        -- botsManager:SpawnBotsAtObjectives()
        botsManager:SpawnBotsAroundTransform(player.soldier.transform)
    end
    if parts[1] == "!spawnallbotsatobj" then
        botsManager:SpawnBotsAtObjectives(1, true)
    end
    if parts[1] == "!spawnmyteam" then
        botsManager:SpawnBotsAtObjectives(player.teamId, false)
    end
    if parts[1] == "!findobj" then
        entityName = o_parts[2]
        print("Finding: "..entityName)
        EntityManager:TraverseAllEntities(function(entity)
            if entity.typeInfo.name == entityName then
                print("Found entity: ".. entity.typeInfo.name)
            end
        end)
    end

    if parts[1] == "get_in" then
        if player.attachedControllable ~= nil then
            print("attachedControllable: "..player.attachedControllable.typeInfo.name)
            botsManager:EmitAction(player.id, 6, 4)
        end
        if player.controlledControllable ~= nil then
            print("controlledControllable: "..player.controlledControllable.typeInfo.name)
        end
    end

    if parts[1] == "get_out" then
        if player.attachedControllable ~= nil then
            print("attachedControllable: "..player.attachedControllable.typeInfo.name)
            botsManager:EmitAction(player.id, 7, 2)
        end
        if player.controlledControllable ~= nil then
            print("controlledControllable: "..player.controlledControllable.typeInfo.name)
        end
    end

    if parts[1] == "!scorecard" and encoded_scores ~= nil then
        g_ScorecardServer:ProcessScorecardData()
    end
    if parts[1] == "!scorecard" and encoded_scores == nil then
        local entityType = o_parts[2]
        local stepSize = 32
        EntityManager:TraverseAllEntities(function(entity)
            if entity:Is(entityType) then
                local entity_bounds = SpatialEntity(entity).aabb
                local min_point = entity_bounds.min
                local max_point = entity_bounds.max
                print("Min Point: "..min_point.x.." "..min_point.y.." "..min_point.z)
                print("Max Point: "..max_point.x.." "..max_point.y.." "..max_point.z)
                min_point = Vec3(
		        	math.ceil(min_point.x),
		        	math.ceil(min_point.y),
		        	math.ceil(min_point.z)
		        )
		        max_point = Vec3(
		        	math.ceil(max_point.x),
		        	math.ceil(max_point.y),
		        	math.ceil(max_point.z)
                )
                while max_point.x % 32 ~= 0 do
                    max_point = Vec3(max_point.x+1, max_point.y, max_point.z)
                end 
                while max_point.z % 32 ~= 0 do
                    max_point = Vec3(max_point.x, max_point.y, max_point.z+1)
                end
                local num_x = math.ceil((max_point.x - min_point.x)/3.0)
                
                local num_z = math.ceil((max_point.z - min_point.z)/3.0)

                while num_x % 32 ~= 0 do
                    num_x = num_x + 1
                end 
                while num_z % 32 ~= 0 do
                    num_z = num_z + 1
                end
                NetEvents:SendTo("OnRequestScorecardGrid", player, num_x, num_z, min_point, max_point)
                
            end
        end)
    end
    if parts[1] == "!scorecard_bounds" then
        local min_x = o_parts[2]
        local min_y = o_parts[3]
        local min_z = o_parts[4]
        local max_x = o_parts[5]
        local max_y = o_parts[6]
        local max_z = o_parts[7]
        local cell_size = 1.0
        local steps = 32
        local min_point = Vec3(
            math.ceil(min_x),
            math.ceil(min_y),
            math.ceil(min_z)
        )
        local max_point = Vec3(
            math.ceil(max_x),
            math.ceil(max_y),
            math.ceil(max_z)
        )
        while max_point.x % steps ~= 0 do
            max_point = Vec3(max_point.x+1, max_point.y, max_point.z)
        end 
        while max_point.z % steps ~= 0 do
            max_point = Vec3(max_point.x, max_point.y, max_point.z+1)
        end
        local num_x = math.ceil((max_point.x - min_point.x)/cell_size)
        
        local num_z = math.ceil((max_point.z - min_point.z)/cell_size)

        while num_x % steps ~= 0 do
            num_x = num_x + 1
        end 
        while num_z % steps ~= 0 do
            num_z = num_z + 1
        end
        NetEvents:SendTo("OnRequestScorecardGrid", player, num_x, num_z, min_point, max_point)

    end

    if parts[1] == "!scorecard_export" then
        g_ScorecardServer:Export()
    end

    if parts[1] == "!scorecard_import" then
        local data_name = o_parts[2]
        local data_type = o_parts[3]
        g_ScorecardServer:Import(data_name, data_type)
    end

    if parts[1] == "!find_path" then
        local start_x = o_parts[2]
        local start_z = o_parts[3]
        local end_x = o_parts[4]
        local end_z = o_parts[5]

        local path = botsManager:FindPathGrid(start_x, start_z, end_x, end_z)
        NetEvents:SendTo("OnSetPath", player, path)

    end

    if parts[1] == "!getobj" then
        entityType = o_parts[2]
        print("Searching for: "..entityType)
        EntityManager:TraverseAllEntities(function(entity)
            -- Do something with entity.
            
            if entity:Is(entityType) then
                local entity_bounds = SpatialEntity(entity).aabb
               -- if entity_bounds.max:Distance(entity_bounds.min) > 1000 then
                    print(entityType .." ".. entity.typeInfo.name .. " ".. entity_bounds.min.x
                    .. " ".. entity_bounds.min.y .. " ".. entity_bounds.min.z
                    .. " ".. entity_bounds.max.x .. " ".. entity_bounds.max.y .. " ".. entity_bounds.max.z)
                    local min_point = entity_bounds.min
                    local max_point = entity_bounds.max
                    min_point = Vec3(
		            	math.ceil(min_point.x),
		            	math.ceil(min_point.y),
		            	math.ceil(min_point.z)
		            )
		            max_point = Vec3(
		            	math.ceil(max_point.x),
		            	math.ceil(max_point.y),
		            	math.ceil(max_point.z)
                    )
                    local num_x = (max_point.x - min_point.x)/3.0
		            local num_z = (max_point.z - min_point.z)/3.0
		            print("Min Point: "..min_point.x.." "..min_point.y.." "..min_point.z)
		            print("Max Point: "..max_point.x.." "..max_point.y.." "..max_point.z)
		            print("Num Boxes: ".." "..num_x.." "..num_z)

                --end
            end
            -- if entity.typeInfo.name == "ServerTeamEntity" then
            --     local teamdata = TeamEntityData(entity.data)
            --     local teamid = teamdata.id
            --     print(teamid)
            --     print("Entity: " .. entity.typeInfo.name)
            -- end
            -- if entity.typeInfo.name == "ServerTeamFilterEntity" then
            --     local teamdata = TeamFilterEntityData(entity.data)
            --     local teamid = teamdata.team
            --     print(teamid)
            --     print("Entity: " .. entity.typeInfo.name)
            -- end
            -- if entity.typeInfo.name == "ServerCapturePointEntity" then
            --     print("Objective Entity!")
            --     local data = CapturePointEntityData(entity.data)
            --     local teamid = data.areaValue
            --     print("Capture: "..teamid)
            -- end

            
          end)

        
    end

    if parts[1] == '!strafe' then
        local player_id = math.floor(tonumber(parts[2]))
        local value = tonumber(parts[3])
        local player = PlayerManager:GetPlayerById(player_id)
        if (player ~= nil) then
            player.input:SetLevel(EntryInputActionEnum.EIAStrafe, value)
        end
    end

end)

return g_ScorecardServer