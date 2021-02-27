class 'BotsManager'
local bot_ = require("Bot")
local Actions = require("BotActions")
local Orders = require('BotOrders')
local VecLib = require('__shared/VecLib')

function BotsManager:__init()
    self.bots = {}
    self.objectives = {}
    self.vehicles = {}
    Events:Subscribe("UpdateManager:Update", self, self.Tick)
    Events:Subscribe("Level:Loaded", self, self.OnLevelLoaded)
    Events:Subscribe('Extension:Unloading', self, self.Destroy)
    Events:Subscribe('Player:Created', self, self.OnPlayerCreated)
    Events:Subscribe('Player:Left', self, self.OnPlayerLeft)
    Events:Subscribe('Player:Destroyed', self, self.OnPlayerLeft)
    Events:Subscribe('Player:Authenticated', self, self.OnPlayerCreated)
    
        
    self.debug_target = nil
    self.should_update = true
    self.last_update_time = 0
    self.update_coroutine = nil
    self.data = nil
    self.data_step = 1
    self.bot_update_step = 1
    self.should_step_through_bots = false
    --
    self.bot_update_interval = 1
    self.bot_update_tickrate = 0.01
    self.last_bot_stream_update_time = 0.0
    self.bot_stream_update_tickrate = 1250
    --
    self.last_bot_update_time = 0.0

    self.players = {}
    self.sorted_players = {}

    self.project_id = -1
    self.profile = {}
    self.level_id = -1
    self.use_spawn_points = false
    self.friendly_spawn_points = {} -- Vec3[]
    self.enemy_spawn_points = {} -- Vec3[]
    self.soldierBlueprint = ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))

    self.lock_respawn = false
end

function BotsManager:AssignVehicles()
    self.vehicles = {}
    EntityManager:TraverseAllEntities(function(entity)
        -- Do something with entity.

        if entity.typeInfo.name == "ServerVehicleEntity" then
            -- print("Vehicle Entity!")
            -- local data = VehicleEntityData(entity.data)
            table.insert(self.vehicles, ControllableEntity(entity))
            -- print("X: ".. SpatialEntity(entity).transform.trans.x)
        end    
    end)
end

function BotsManager:InitialiseHeartbeatSettings()
    local initialHeartbeatData = self:GetManager('/initialise-heartbeat/')
    print("Initializing heartbeat...")
    if (initialHeartbeatData.body ~= nil) then
        
        print(initialHeartbeatData.body)
        local data = json.decode(initialHeartbeatData.body)
        self.use_spawn_points = data.use_spawn_points
        self.friendly_spawn_points = {}
        if self.use_spawn_points then
            for _, p in pairs(data.spawn_points_friendly) do
                table.insert(self.friendly_spawn_points, Vec3(p.x, p.y, p.z))
            end
            for _, p in pairs(data.spawn_points_enemy) do
                table.insert(self.enemy_spawn_points, Vec3(p.x, p.y, p.z))
            end
        end
        print("Loading objectives...")
        self.objectives = {}
        EntityManager:TraverseAllEntities(function(entity)
            -- Do something with entity.

            if entity.typeInfo.name == "ServerCapturePointEntity" then
                print("Objective Entity!")
                local data = CapturePointEntityData(entity.data)
                local teamid = data.areaValue
                print("Capture: "..teamid.." capture type: "..data.capturableType)
                --if data.capturableType ~= CapturableType.CTUnableToChangeTeam then
                    table.insert(self.objectives, CapturePointEntity(entity))
                --end 
                print("X: ".. SpatialEntity(entity).transform.trans.x)
            end    
        end)
        self:AssignVehicles()
    end
end

function BotsManager:OnPlayerCreated(player)
    table.insert(self.players, player)
    self.players = PlayerManager:GetPlayers()
    self:UpdateSortedPlayersTable()
end

function BotsManager:OnPlayerLeft(player)
    local idx = -1
    for g, pl in pairs(self.players) do
        if pl.ip == player.ip then
            idx = g
            break
        end
    end
    print('removing player at: '..idx)
    table.remove(self.players, idx)
    -- self.players = PlayerManager:GetPlayers()
    self:UpdateSortedPlayersTable()
end

function BotsManager:UpdateSortedPlayersTable()
    self.sorted_players = {}
    for _, player in pairs(self.players) do
        self.sorted_players[player.id] = player
    end
    self.players = PlayerManager:GetPlayers()

end

function BotsManager:GetPlayerJSON(player)
    local data = '{'
    data = data.. 
        '"player_id": '..player.id..
        ', "online_id":'..player.onlineId..
        ', "name": '..'"'..player.name..'"'..
        ', "alive":'..tostring(player.alive)..
        ', "is_squad_leader": '..tostring(player.isSquadLeader)..
        ', "is_squad_private": '..tostring(player.isSquadPrivate)
    if player.hasSoldier and player.alive and player.soldier ~= nil then
        data = data..', "health": '..tostring(player.soldier.health)
        data = data..', "transform": '..json.encode(player.soldier.transform)
    else
        data = data..', "health": 0.0'
        data = data..', "transform": '..'{"forward": {"x": 0, "y": 0, "z": 1}, "right": {"x": 1, "y": 0, "z": 0}, "up": {"x": 0, "y": 1, "z": 0}, "trans": {"x": 0, "y": 1, "z": 0}}'
    end
    data = data..
        ', "has_soldier": '..tostring(player.hasSoldier)..
        ', "team": '..tostring(player.teamId)..
        ', "squad": '..tostring(player.squadId)
    data = data .. ', "in_vehicle": false'
    data = data.. " }"
    return data
end

-- @Params
-- vehicle : ControllableEntity [server]
function BotsManager:GetVehicleJSON(vehicle)
    local data = '{'
    data = data .. 
    '"instance": '.. tostring(vehicle.uniqueId) ..
    ', "max_passenger_count": '.. tostring(VehicleEntityData(vehicle.data).maxPlayersInVehicle) ..
    ', "transform": '.. json.encode(vehicle.transform)
    data = data .. ' }'
    return data
end

function BotsManager:GetPlayerJSONConcat(player)
    local keys = {'name', 'team', 'player_id','transform', 'health', 'alive', 'squad', 'online_id', 'is_squad_leader', 'is_squad_private', 'has_soldier', 'in_vehicle'}
    local values = {'"'..player.name..'"', player.teamId, player.id}
    local buffer = {"{ "}
    if player.hasSoldier and player.soldier ~= nil then
        table.insert(values, json.encode(player.soldier.transform))
        table.insert(values, tostring(player.soldier.health))
    else
        --table.insert(values, json.encode(LinearTransform(1.0)))
        table.insert(values, '{"forward": {"x": 0, "y": 0, "z": 1}, "right": {"x": 1, "y": 0, "z": 0}, "up": {"x": 0, "y": 1, "z": 0}, "trans": {"x": 0, "y": 1, "z": 0}}')
        table.insert(values, '0.0')
    end

    table.insert(values, tostring(player.alive))
    table.insert(values, tostring(player.squadId))
    table.insert(values, tostring(player.onlineId))
    table.insert(values, tostring(player.isSquadLeader))
    table.insert(values, tostring(player.isSquadPrivate))
    table.insert(values, tostring(player.hasSoldier))
    table.insert(values, 'false')
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

function BotsManager:GetPlayersJSON()
    local players = PlayerManager:GetPlayers()
    local data = '['
    if #players > 0 then
        for idx, player in pairs(players) do
            if player ~= nil then
                if idx == 1 then
                    --data = data..self:GetPlayerJSON(player)
                    data = data..self:GetPlayerJSONConcat(player)
                else
                    --data = data..', '..self:GetPlayerJSON(player)
                    data = data..', '..self:GetPlayerJSONConcat(player)
                end
            end
        end
    end
    data = data..' ]'
    return data
end

function BotsManager:GetVehiclesJSON()
    self:AssignVehicles()
    local buffer = {'"vehicles": ['}
    for idx, vehicle in pairs(self.vehicles) do
        if idx == 1 then
            buffer[#buffer+1] = self:GetVehicleJSON(vehicle)
        else
            buffer[#buffer+1] = ", "..self:GetVehicleJSON(vehicle)
        end
    end
    buffer[#buffer+1] = ' ]'
    return table.concat(buffer)
end

function BotsManager:FindPath(Start, End)
    -- in theory, json.decode should convert this back to a table of Vec3
    local url = "http://127.0.0.1:8000/pathfinding/find-path/" -- ..Start.x..","..Start.z.."/"..End.x..","..End.z.."/"
    local headers= {}
    local options = HttpOptions(headers, 90)
    options:SetHeader("Start", tostring(Start.x)..","..tostring(Start.z))
    options:SetHeader("Level-Name", SharedUtils:GetLevelName())
    options:SetHeader("End", tostring(End.x)..","..tostring(End.z))
    options:SetHeader("Grid-Space", tostring(false))
       
    local result = Net:GetHTTP(url, options)
    if result then
        print(result.body)
        local data = json.decode(result.body)
        local path = {}
        for i, d in pairs(data) do
            path[i] = Vec3(d.x, d.y, d.z)
        end
        return path
    end
    return nil 
end

function BotsManager:FindPathGrid(Start_X, Start_Y, End_X, End_Y)
    -- in theory, json.decode should convert this back to a table of Vec3
    local url = "http://127.0.0.1:8000/pathfinding/find-path/" -- ..Start.x..","..Start.z.."/"..End.x..","..End.z.."/"
    local headers= {}
    local options = HttpOptions(headers, 90)
    options:SetHeader("Start", tostring(Start_X)..","..tostring(Start_Y))
    options:SetHeader("Level-Name", SharedUtils:GetLevelName())
    options:SetHeader("End", tostring(End_X)..","..tostring(End_Y))
    options:SetHeader("Grid-Space", tostring(true))
       
    local result = Net:GetHTTP(url, options)
    if result then
        print(result.body)
        local data = json.decode(result.body)
        local path = {}
        for i, d in pairs(data) do
            path[i] = Vec3(d.x, d.y, d.z)
        end
        return path
    end
    return nil 
end

function BotsManager:GetObjectiveJSON(obj, idx)
    local objData = CapturePointEntityData(obj.data)
    data = "{"
    data = data..
    '"index": '..tostring(idx)..
    ', "team": '..tostring(obj.team)..
    ', "name": '..'"'..tostring(obj.name)..'"'..
    ', "attackingTeam": '..tostring(obj.attackingTeam)..
    ', "transform": '..tostring(json.encode(obj.transform))..
    ', "controlled": '..tostring(obj.isControlled)..
    ', "capturable": '..tostring(objData.capturableType ~= CapturableType.CTUnableToChangeTeam).."}"
    return data
end

function BotsManager:GetObjectivesJSON() 
    -- print("concat objectives")
    local buffer = {'"objectives": ['}
    for idx, obj in pairs(self.objectives) do
        -- local test = json.encode(obj)
        -- print(test)
        if idx == 1 then
            buffer[#buffer+1] = self:GetObjectiveJSON(obj, idx)
        else
            buffer[#buffer+1] = ", "..self:GetObjectiveJSON(obj, idx)
        end
    end
    buffer[#buffer+1] = ' ]'
    return table.concat(buffer)
end

function BotsManager:GetBotsJSON(only_alive)
    local cond = true
    if only_alive then
        local res = '"bots": ['
        if #self.bots > 0 then
            for idx, obj in pairs(self.bots) do
                
                cond = obj.alive and obj.player_controller.hasSoldier
                
                if obj.player_controller ~= nil and cond then
                    if idx == 1 then
                        res = res .. obj:EncodeAsJSON()
                    else
                        res =  res..', '.. obj:EncodeAsJSON()
                    end
                end
            end
        end
        res = res .. ' ]'
        return res
    end
    -- print("concat bots")
    local buffer = {'"bots": ['}
    local i = 1
    
    for idx, obj in pairs(self.bots) do
        if only_alive then
            cond = obj.player_controller.alive and obj.player_controller.hasSoldier and obj.spawned
        end
        if cond then
            if i == 1 then
                buffer[#buffer+1] = obj:EncodeAsJSONConcat()
            else
                buffer[#buffer+1] = ', '..obj:EncodeAsJSONConcat()
            end
        end
        i = i + 1
    end
    buffer[#buffer+1] = ' ]'
    return table.concat(buffer)
end

function BotsManager:GetPlayersJSONConcat(only_alive)
    local players = PlayerManager:GetPlayers()
    local cond = true
    if only_alive then
        local res = '"players": ['
        if #players > 0 then
            for idx, player in pairs(players) do
                
                cond = player.alive and player.hasSoldier
                
                if player ~= nil and cond then
                    if idx == 1 then
                        res = res .. self:GetPlayerJSONConcat(player)
                    else
                        res =  res..', '..self:GetPlayerJSONConcat(player)
                    end
                end
            end
        end
        res = res .. ' ]'
        return res
    end
    
    local buffer = {'"players": ['}
    
    
    if #players > 0 then
        for idx, player in pairs(players) do
            if only_alive then
                cond = player.alive and player.hasSoldier
            end
            if player ~= nil and cond then
                if idx == 1 then
                    buffer[#buffer+1] = self:GetPlayerJSONConcat(player)
                else
                    buffer[#buffer+1] = ', '..self:GetPlayerJSONConcat(player)
                end
            end
        end
    end
    buffer[#buffer+1] = ' ]'
    return table.concat(buffer)
end

function BotsManager:GetAllLevelDataJSONConcat()
    local buffer = {'{'}
    buffer[#buffer+1] = self:GetBotsJSON(false)
    buffer[#buffer+1] = ','
    buffer[#buffer+1] = self:GetPlayersJSONConcat(false)
    buffer[#buffer+1] = ','
    buffer[#buffer+1] = self:GetObjectivesJSON()
    buffer[#buffer+1] = ','
    buffer[#buffer+1] = self:GetVehiclesJSON()
    buffer[#buffer+1] = ','
    buffer[#buffer+1] = ' "level_name": '..'"'..SharedUtils:GetLevelName()..'"'
    buffer[#buffer+1] = ' }'
    return table.concat(buffer)
end

function BotsManager:GetMinimalLevelDataJSONConcat()
    local buffer = {'{'}
    buffer[#buffer+1] = self:GetBotsJSON(true)
    buffer[#buffer+1] = ','
    buffer[#buffer+1] = self:GetPlayersJSONConcat(true)
    buffer[#buffer+1] = ','
    buffer[#buffer+1] = ' "level_name": '..'"'..SharedUtils:GetLevelName()..'"'
    buffer[#buffer+1] = ' }'
    return table.concat(buffer)
end

-- will change to table.concat -- as these strings get too big and creating a new one each time is slow
function BotsManager:GetAllLevelDataJSON()
    local data = '"objectives": ['
    for idx, obj in pairs(self.objectives) do
        if idx == 1 then
            data = data .. "{"
        else
            data = data .. ", {"
        end
        
        data = data..'"index": '..tostring(idx)..', "team": '..tostring(obj.team)..', "name": '..'"'..tostring(obj.name)..'"'..', "attackingTeam": '..tostring(obj.attackingTeam)..', "transform": '..tostring(json.encode(obj.transform))
            ..', "controlled": '..tostring(obj.isControlled).."}"

    end
    data = data .. " ], "
    data = data .. '"bots": ['
    for idx, bot in pairs(self.bots) do
        if idx == 1 then
            data = data..bot:EncodeAsJSON()
        else
            data = data .. ', '..bot:EncodeAsJSON()
        end
    end
    data = data .. "], "
    data = data .. '"players":'.. self:GetPlayersJSON()..","
    data = data .. '"level_name": '..'"'..SharedUtils:GetLevelName()..'"'
    return data
end

function BotsManager:IsABot(player)
    local isABot = false
    for _, bot in pairs(self.bots) do
        if bot.player_controller == player then
            isABot = true
            break
        end
    end
    return isABot
end

function BotsManager:GetNearestPlayer(position, team, all)
    local players = PlayerManager:GetPlayers()
    local min_distance = math.huge
    local min_player = nil
    for _, player in pairs(players) do
        if player.alive and (player.teamId ~= team or all) then
            local my_distance = player.soldier.transform.trans:Distance(position)
            if my_distance < min_distance then
                min_distance = my_distance
                min_player = player
            end
        end
    end
    return min_player
end

function BotsManager:GetEnemyOf(player)
    local enemy = nil
    for _, bot in pairs(self.bots) do
        if bot.target ~= nil then
            if bot.target == player then
                enemy = bot
                break
            end
        end
    end
    return enemy
end

function BotsManager:OnLevelLoaded(levelName, gameMode, round, roundsPerMap)
    self.lock_respawn = true
    if self.project_id > -1 then
        print("Post level loaded")
        local data = {}
        data['level_name'] = SharedUtils:GetLevelName()
        local encoded_data = json.encode(data)
        local result = self:PostManager('/project/'..self.project_id..'/get-level-id/', encoded_data)
        print(result.body)
        if tostring(result.body) ~= "error" then
            if tonumber(result.body) ~= nil then
                local level_id = math.floor(tonumber(result.body))
                self:PostManager('/project/'..self.project_id..'/level/'..tostring(level_id)..'/on-level-loaded/', '{}')
                self:InitialiseHeartbeatSettings()
            end
        end
    end
    print("Killing bots")
    if #self.bots > 0 then
        for _, bot in pairs(self.bots) do
            bot:Kill()
        end
    end
    self:Destroy() -- clear
    print("Loading objectives...")
    self.objectives = {}
    EntityManager:TraverseAllEntities(function(entity)
        -- Do something with entity.
        
        if entity.typeInfo.name == "ServerCapturePointEntity" then
            print("Objective Entity!")
            local data = CapturePointEntityData(entity.data)
            local teamid = data.areaValue
            print("Capture: "..teamid.." capture type: "..data.capturableType)
            --if data.capturableType ~= CapturableType.CTUnableToChangeTeam then
                table.insert(self.objectives, CapturePointEntity(entity))
            --end 
            print("X: ".. SpatialEntity(entity).transform.trans.x)
        end    
    end)
    self.lock_respawn = false
end

function BotsManager:RawPathToVec3Path(data)
    local path = {}
    for i, p in pairs(data) do
        path[i] = Vec3(p.x, p.y, p.z)
    end
    return path
end

function utf8_from(t)
    local bytearr = {}
    for _, v in ipairs(t) do
      local utf8byte = v < 0 and (0xff + v + 1) or v
      table.insert(bytearr, string.char(utf8byte))
    end
    return table.concat(bytearr)
  end

function BotsManager:RegularBotTick()
    local socket = Net:Socket(NetSocketFamily.INET, NetSocketType.Stream)
    socket:Connect("127.0.0.1", 2929)
    local data = self:GetAllLevelDataJSONConcat() --'{ '..self:GetAllLevelDataJSON().."}"
    if socket ~= nil then
        socket:Write(tostring(#data))
        socket:Write(data)
        print("Wait")
        local dataResult, result_ = socket:Read(6)
        --print("DataResult: "..tostring(dataResult))
        local l = tonumber(dataResult)
        --print("DataResult Length: "..tostring(dataResult:len()))
        --print("Result: ".. tostring(result))

        --print("Wait")
        local result = nil
        if l ~= nil then
            local dataResult, result_ = socket:Read(l)
            result = tostring(dataResult)
            if dataResult:len() == 0 then
                result = nil
            end
            print("DataResult JSON: "..tostring(dataResult:len()))
        end

        if result ~= nil then
            local decoded = json.decode(result)
            -- print("bots: "..#decoded.bots)
            if #decoded.bots > 0 then
                for _, bot in pairs(decoded.bots) do
                    local currentBot = self.bots[bot.bot_index]
                    if currentBot then
                        if bot.path ~= nil then
                            currentBot.path = self:RawPathToVec3Path(bot.path)
                            currentBot.path_step = 1
                        end
                        if bot.target ~= -1 then
                            
                            currentBot.target = PlayerManager:GetPlayerById(bot.target)
                        else
                            currentBot.target = nil
                            currentBot.path_step = 1
                        end
                        currentBot.player_controller.name = bot.name
                        currentBot.order = bot.order
                        -- currentBot.action = bot.action
                    else
                        -- print("Invalid bot @ "..bot.bot_index)
                    end
                end
            end
        end
        --print("DataResult Length: "..tostring(dataResult:len()))
        --print("Result: ".. tostring(result))
        
        

        socket:Destroy()
    end
    -- local url = "http://127.0.0.1:8000/pathfinding/update-level/"
    -- -- local result = nil
    -- local result = Net:PostHTTP(url, data)
    -- if result ~= nil then
    --     local decoded = json.decode(result.body)
    --     -- print("bots: "..#decoded.bots)
    --     if #decoded.bots > 0 then
    --         for _, bot in pairs(decoded.bots) do
    --             local currentBot = self.bots[bot.bot_index]
    --             if currentBot then
    --                 if bot.path ~= nil then
    --                     currentBot.path = self:RawPathToVec3Path(bot.path)
    --                     currentBot.path_step = 1
    --                 end
    --                 if bot.target ~= -1 then
    --                     currentBot.target = PlayerManager:GetPlayerById(bot.target)
    --                 else
    --                     currentBot.target = nil
    --                     currentBot.path_step = 1
    --                 end
    --                 currentBot.player_controller.name = bot.name
    --                 currentBot.order = bot.order
    --                 currentBot.action = bot.action
    --             else
    --                 -- print("Invalid bot @ "..bot.bot_index)
    --             end
    --         end
    --     end
    -- end
end

function BotsManager:PostManager (url, data)
    local headers = {}
    local options = HttpOptions(headers, 30)
    options:SetHeader('Authorization', 'Token '..self.profile.token)
    options:SetHeader('Content-Type', 'application/json')
    local url = 'http://127.0.0.1:8000/v1'..url
    return Net:PostHTTP(url, data, options)
end 

function BotsManager:PostManagerAsync (url, data, context, callable)
    local headers = {}
    local options = HttpOptions(headers, 30)
    options:SetHeader('Authorization', 'Token '..self.profile.token)
    options:SetHeader('Content-Type', 'application/json')
    local url = 'http://127.0.0.1:8000/v1'..url
    return Net:PostHTTPAsync(url, data, options, context, callable)
end 

function BotsManager:GetManager (url)
    local headers = {}
    local options = HttpOptions(headers, 30)
    options:SetHeader('Authorization', 'Token '..self.profile.token)
    options:SetHeader('Content-Type', 'application/json')
    local url = 'http://127.0.0.1:8000/v1'..url
    return Net:GetHTTP(url, options)
end

function BotsManager:EmitAction(instigator, action, order)
    local data = {}
    data['Instigator'] = instigator
    data['Action'] = action
    data['Order'] = order
    local data_json = json.encode(data)
    self:PostManager('/emit/', data_json)
end

function BotsManager:OnEmitAction(data)
end

function BotsManager:EmitActionAsync(instigator, action, order)
    local data = {}
    data['Instigator'] = instigator
    data['Action'] = action
    data['Order'] = order
    local data_json = json.encode(data)
    self:PostManagerAsync('/emit/', data_json, self, self.OnEmitAction)
end

function BotsManager:PostPushLevelData(result)
    if result ~= nil then
        --print('valid result :) .. '..result.status)
        --print('result: '..tostring(result.body))
        if result.status == 200 then
            local decoded = json.decode(result.body)
            --local encoded = json.encode(decoded)
            --print('encoded test: '..encoded)
            if decoded == nil then
                local t, err = json.decode(result.body)
                --print('failed to decode: '..tostring(err))
            end
            self.data = decoded
            --print('test bot '.. json.encode(decoded['bots']))
        else
            self.data = nil
        end
    end
end

function BotsManager:PushLevelData(data)
    -- local data = self:GetAllLevelDataJSONConcat() 
    -- local data = '{ '..self:GetAllLevelDataJSON().."}"
    if self.project_id ~= -1 then
        local url = "http://127.0.0.1:8000/v1/project/"..tostring(self.project_id)..'/level/update/'
        local headers= {}
        local options = HttpOptions(headers, 90)
        options:SetHeader('Authorization', 'Token '..self.profile.token)
        options:SetHeader('Level', SharedUtils:GetLevelName())
        Net:PostHTTPAsync(url, data, options, self, self.PostPushLevelData)
    end
    
    -- if result ~= nil then
    --     if result.status == 200 then 
    --         -- print("Successfully got level data")
    --         local decoded = json.decode(result.body)
    --         self.data = decoded
    --     else
    --         self.data = nil
    --     end
    --    
    -- end
    
end

function BotsManager:PostFastStreamData(result)

end

function BotsManager:FastStreamData(data)
    if self.project_id ~= -1 then
        local url = "http://127.0.0.1:8000/v1/project/"..tostring(self.project_id)..'/level/update/stream/'
        local headers= {}
        local options = HttpOptions(headers, 90)
        options:SetHeader('Authorization', 'Token '..self.profile.token)
        options:SetHeader('Level', SharedUtils:GetLevelName())
        Net:PostHTTPAsync(url, data, options, self, self.PostFastStreamData)
    end
end

function BotsManager:StepThroughData()
    if self.data ~= nil then
        if tonumber(#self.data.bots) ~= 0 and self.data_step <= tonumber(#self.data.bots) then
            -- print(tostring(#self.data.bots))
            -- print("Stepping thru data "..self.data_step)
            local bot = self.data.bots[self.data_step]
            local currentBot = self.bots[bot.bot_index]
            if currentBot ~= nil then
                                
                if bot.path ~= nil then
                    if tonumber(#bot.path) > 0 then
                        -- print("Setting Path")
                        
                        local p = self:RawPathToVec3Path(bot.path)
                        -- currentBot.destination = nil
                        if #currentBot.path > 0 then
                            if currentBot.lock_path then
                                --currentBot.lock_path = false
                            end
                            if p[1] ~= currentBot.path[1] and not currentBot.lock_path then
                                -- find closest step
                                local min_distance = 98999
                                local min_step = 1
                                for idx, point in pairs(p) do
                                    if currentBot.path ~= nil and point ~= nil then
                                        if point:Distance(currentBot.path[currentBot.path_step]) < min_distance then
                                            min_distance =point:Distance(currentBot.path[currentBot.path_step])
                                            min_step = idx
                                        end
                                    end
                                end
                                currentBot.path_step = min_step
                            end
                        else
                            if not currentBot.lock_path then
                                currentBot.path_step = 1
                            end
                        end
                        if not currentBot.lock_path then
                            -- currentBot.path_step = 1
                            currentBot.path = {}
                            currentBot.path = self:RawPathToVec3Path(bot.path)
                            currentBot.lock_path = true
                            -- print("Set Path")
                        end
                        --print("Set Path")
                        
                    end
                end
                if bot.target ~= -1 then
                    --print("Setting target")
                    if currentBot.target ~= nil then
                        
                        if currentBot.target.id == bot.target then
                        else
                            currentBot.target = self.sorted_players[bot.target] --PlayerManager:GetPlayerById(bot.target)
                            -- currentBot.lock_path = false -- unlock here as I want the bots to be responsive with enemies.
                        end
                    else
                    currentBot.target = self.sorted_players[bot.target] --PlayerManager:GetPlayerById(bot.target)
                    end
                else
                    currentBot.target = nil
                    if currentBot.lock_path == false then
                        --currentBot.path_step = 1
                    end
                end

                -- print("setting name")
                -- currentBot.player_controller.name = bot.name

                -- print("setting order")
                currentBot.order = bot.order
                -- print("setting action")
                currentBot.action = bot.action
                currentBot.requested_action = -1
                currentBot.requested_order = -1
                currentBot.requested_target_id = -2
                currentBot.selected_kit = bot.selected_kit

                if (currentBot.player_controller.alive) then
                    if currentBot:IsOutOfAmmo() and (SharedUtils:GetTime() -  currentBot.last_request_ammo_request) > 5 then
                        currentBot.last_request_ammo_request = SharedUtils:GetTime()
                        self:EmitActionAsync(currentBot.player_controller.id, Actions.PROVIDE_AMMO, Orders.FRIENDLY)
                    end
                    if currentBot:IsLowHealth() and (SharedUtils:GetTime() -  currentBot.last_request_health_request) > 5 then
                        currentBot.last_request_health_request = SharedUtils:GetTime()
                        self:EmitActionAsync(currentBot.player_controller.id, Actions.PROVIDE_HEALTH, Orders.FRIENDLY)
                    end
                end

                -- print("checking respawn")
                if currentBot.requested_respawn then
                    self:RespawnBot(currentBot)
                    currentBot.requested_respawn = false
                end
                -- print("done checking respawn")

            else
                -- print("Invalid bot @ "..bot.bot_index)
            end
            self.data_step = self.data_step + 1
        else
            self.data = nil
        end
    else
        if self.data_step ~= 1 then
            self.data_step = 1
        end
    end
end

function BotsManager:PushBotData(Bot)
    local data = Bot:EncodeAsJSON()
    local url = "http://127.0.0.1:8000/bots/update-bot/"
    local result = Net:PostHTTP(url, data)
end

function BotsManager:StepThroughBots(dt, pass)
    if (not (tonumber(self.bot_update_step) > tonumber(#self.bots))) and tonumber(#self.bots) > 0 then
        local bot = self.bots[self.bot_update_step]
        if bot.requested_respawn and self.should_step_through_bots and (SharedUtils:GetTime() - self.last_bot_update_time) > 1 then
            self:RespawnBot(bot)
            -- print('respawn '..self.bot_update_step)
            bot.requested_respawn = false
            self.last_bot_update_time = SharedUtils:GetTime()
        end
        -- if (SharedUtils:GetTimeMS() - self.last_bot_update_time) >= self.bot_update_interval then
        --     bot:Tick(dt, pass)
        --     -- print('ticking')
        --     self.last_bot_update_time = SharedUtils:GetTime()
        -- end
        
        self.bot_update_step = self.bot_update_step + 1
    else
        self.bot_update_step = 1
        self.should_step_through_bots = false
    end
end

function BotsManager:Tick(deltaTime, pass)
    
    if pass ~= UpdatePass.UpdatePass_PostFrame then
        return
      end
    if tonumber(#self.bots) > 0 then
        for _, bot in pairs(self.bots) do
            bot:InternalTick(deltaTime, pass)
        end
    end
        -- print("ticking")
    self:StepThroughBots(deltaTime, pass)

    --print("Getting(serializing) scene data")
    --print("Got scene data")

    -- if (SharedUtils:GetTimeMS() - self.last_bot_update_time) >= self.bot_update_interval then
    --     if #self.bots  >0 then
    --         for _, bot in pairs(self.bots) do
    --             bot:Tick(dt, pass)
    --         end 
    --     end
    --     -- print('ticking')
    --     self.last_bot_update_time = SharedUtils:GetTime()
    -- end
    if (SharedUtils:GetTimeMS() - self.last_bot_stream_update_time) > (self.bot_stream_update_tickrate) then
        local data = self:GetMinimalLevelDataJSONConcat()
        self:FastStreamData(data)
        -- print("Sending fast stream")
        self.last_bot_stream_update_time = SharedUtils:GetTimeMS()
    end
    if self.should_update == true or (SharedUtils:GetTime() - self.last_update_time) > self.bot_update_interval then
        self.last_update_time = SharedUtils:GetTime()
        -- print("Update")
        self.should_update = false
        local data = self:GetAllLevelDataJSONConcat()

        self:PushLevelData(data)
        -- self:RegularBotTick()
        -- if self.update_coroutine ~= nil then
        --     if coroutine.status(self.update_coroutine) ~= 'dead' and self.data ~= nil then
        --         coroutine.resume(self.update_coroutine, self, self.data)
        --     else
        --         self.update_coroutine = nil
        --     end
        -- end
        

        -- for _, bot in pairs(self.bots) do
        --     if bot.requested_respawn then
        --         self:RespawnBot(bot)
        --         bot.requested_respawn = false
        --     end
        -- end
        self.should_step_through_bots = true
        
    end

    
    
    -- if self.should_step_through_bots then
    --     self:StepThroughBots()
    -- end
    self:StepThroughData()
    
end

function BotsManager:CreateBot(name, team, squad)

    bot = bot_.createBot(self, name, team, squad)
    -- self:PushBotData(bot) -- no need for this as we are doing this in tick
    print("Created bot")
    return bot
end

function BotsManager:Destroy()
    print("Destroying BotManager")
    for _, bot in pairs(self.bots) do
        bot:Destroy()
    end
    -- local oldbots = self.bots
    
    for i, bot in pairs(self.bots) do
        table.remove(self.bots, i)
    end 
    for i, obj in pairs(self.objectives) do
        table.remove(self.objectives, i)
    end

    print("Done destroying")
    self.bots = {}
    self.objectives = {}
end

-- return the position of the nearest enemy obj
function BotsManager:GetNearestEnemyObjective(position, team)
    nearest = nil
    for _, entity in pairs(self.objectives) do
        local data = CapturePointEntityData(entity.data)
        local teamid = data.areaValue
        local currentPosition = SpatialEntity(entity).transform.trans
        if teamid ~= team and nearest == nil then
            nearest = currentPosition
        elseif teamid ~= team and currentPosition:Distance(position) < nearest:Distance(position) then
            nearest = currentPosition
        end
    end
    return nearest
end

function BotsManager:GetNearestEnemyObjectiveEntity(position, team)
    nearest = nil
    nearestEntity = nil
    for _, entity in pairs(self.objectives) do
        local data = CapturePointEntityData(entity.data)
        local teamid = data.areaValue
        local currentPosition = SpatialEntity(entity).transform.trans
        if teamid ~= team and nearest == nil then
            nearest = currentPosition
            nearestEntity = entity
        elseif teamid ~= team and currentPosition:Distance(position) < nearest:Distance(position) then
            nearest = currentPosition
            nearestEntity = entity
        end
    end
    return nearestEntity
end

function BotsManager:GetNumberOfRegisteredObjectives()
    count = 0
    for _, obj in pairs(self.objectives) do
        count = count + 1
    end

    return count
end

function BotsManager:GetAllObjectivesForTeam(team)
    local _objectives=  {}
    for _, obj in pairs(self.objectives) do
        if obj.isControlled and obj.team == team then
            table.insert(_objectives, obj)
        end
    end
    return _objectives
end

-- for debugging, spawn at all of the objectives
function BotsManager:SpawnBotsAtObjectives(team, all)
    local idx = 1
    local soldierBlueprint = ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))
    local soldierKit = ResourceManager:SearchForInstanceByGuid(Guid('A15EE431-88B8-4B35-B69A-985CEA934855'))
    local n_objectives = self:GetNumberOfRegisteredObjectives()
    -- local neutral_objectives = self:GetAllObjectivesForTeam(0)
    local team1_objectives = self:GetAllObjectivesForTeam(1)
    local team2_objectives = self:GetAllObjectivesForTeam(2)

    print("Spawning bots at objectives")
    print("Objectives: " .. n_objectives)
    for _, bot in pairs(self.bots) do
        --print("Accessing element: "..idx.."Of table length"..n_objectives)
        if bot.player_controller.teamId == team or all then
            local entity = nil
            if bot.player_controller.teamId == 1 then
                entity = team1_objectives[math.random(1, #team1_objectives)]
            elseif bot.player_controller.teamId == 2 then
                entity = team2_objectives[math.random(1, #team2_objectives)]
            end
            local currentTransform = entity.transform:Clone()
            local currentQuat = currentTransform:ToQuatTransform(true)
            local newPos = VecLib:RandomPointInRadius(currentTransform.trans, 25.0)
            currentTransform = LinearTransform(
                currentTransform.left, currentTransform.up, currentTransform.forward,
                Vec3(newPos.x, currentTransform.trans.y, newPos.z)
            )
            -- print("Ok, spawning bot... at  x"..currentTransform.trans.x .."y ".. currentTransform.trans.y.."z "..currentTransform.trans.z)
            -- print("Bot transform: scale: ".. currentQuat.transAndScale.w)

            bot:SpawnBot(currentTransform,CharacterPoseType.CharacterPoseType_Stand , soldierBlueprint, soldierKit, {})
            -- bot.path = self:FindPath(currentTransform.trans, self:GetNearestEnemyObjective(currentTransform.trans, TeamId.Team1))
            bot.action = Actions.ATTACK
            -- break
            if idx < n_objectives then
                idx = idx + 1
            else
                idx = 1
            end
        end
    end
end

function BotsManager:SpawnBotsAroundTransform(Transform)
    

    for _, bot in pairs(self.bots) do
        local currentTransform = Transform:Clone()
        local newPos = VecLib:RandomPointInRadius(currentTransform.trans, 25.0)
        --US
	    local soldierBlueprint = ResourceManager:SearchForDataContainer('Characters/Soldiers/MpSoldier')
	    local soldierKit = ResourceManager:SearchForInstanceByGuid(Guid('0A99EBDB-602C-4080-BC3F-B388AA18ADDD'))
        local visualUnlocks = {}
	    --RU
	    if bot.teamId == TeamId.Team2 then
	    	soldierBlueprint = ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))
            soldierKit = ResourceManager:SearchForDataContainer('Gameplay/Kits/RURecon')
            visualUnlocks =  { ResourceManager:SearchForDataContainer('Persistence/Unlocks/Soldiers/Visual/MP/RU/MP_RU_Recon_Appearance_DrPepper') }
	    end
        currentTransform = LinearTransform(
            currentTransform.left, currentTransform.up, currentTransform.forward,
            Vec3(newPos.x, currentTransform.trans.y, newPos.z)
        )
        bot:SpawnBot(currentTransform,CharacterPoseType.CharacterPoseType_Stand , soldierBlueprint, soldierKit, visualUnlocks)
        bot.objective = self:GetNearestEnemyObjectiveEntity(currentTransform.trans, TeamId.Team1)
        bot.path_step = 1
        bot.path = {}
        -- local find_path = self:FindPath(currentTransform.trans, self:GetNearestEnemyObjective(currentTransform.trans, TeamId.Team1))
        -- if find_path ~= nil then
        --     bot.path = find_path
        -- end
       
        bot.action = Actions.ATTACK
        if bot.objective == nil then
            print("Bot objective is nil")
        else
            print("Bot objective is valid")
        end
    end
end

function BotsManager:GetNearestSpawnPointFromTranslation(Translation, Team)
    local spawnPoints = {}
    if (Team == 1) then
        spawnPoints = self.friendly_spawn_points
    else
        spawnPoints = self.enemy_spawn_points
    end
    local minDistance = math.huge
    local minTranslation = Translation
    local optimalPoints = {}
    for _, p in pairs(spawnPoints) do
        if p:Distance(Translation) < 30 then
            table.insert(optimalPoints, p)
        end
    end
    if #optimalPoints == 0 then
        return Vec3(
            Translation.x + math.random(-5, 5),
            Translation.y,
            Translation.z + math.random(-5, 5)
        )
    end
    minTranslation = optimalPoints[math.random(1, #optimalPoints)]

    if minTranslation:Distance(Translation) > 50 then
        return Vec3(
            Translation.x + math.random(-5, 5),
            Translation.y,
            Translation.z + math.random(-5, 5)
        )
    end
    return Vec3(
        minTranslation.x + math.random(-5, 5),
        minTranslation.y - 0.6,
        minTranslation.z + math.random(-5, 5)
    )
end

function BotsManager:GetRandomSpawnPoint(Team)
    local spawnPoints = {}
    if (Team == 1) then
        spawnPoints = self.friendly_spawn_points
    else
        spawnPoints = self.enemy_spawn_points
    end
    if #spawnPoints > 1 then
        return spawnPoints[math.random(1, #spawnPoints)]
    else
        return nil
    end
end

function BotsManager:SpawnBotAroundTransform(Transform, bot)
    if self.soldierBlueprint == nil then
        self.soldierBlueprint =ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))
    end
    --US
    -- local soldierBlueprint = ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))
    -- local soldierKit = ResourceManager:SearchForInstanceByGuid(Guid('0A99EBDB-602C-4080-BC3F-B388AA18ADDD'))
    -- 
    -- --RU
    -- if bot.teamId == TeamId.Team2 then
    --     soldierBlueprint = ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))
    --     soldierKit = ResourceManager:SearchForInstanceByGuid(Guid('DB0FCE83-2505-4948-8661-660DD0C64B63'))
    -- end

    if self.use_spawn_points then
        local currentTransform = Transform:Clone()
        local optimalTranslation = self:GetNearestSpawnPointFromTranslation(currentTransform.trans, bot.teamId)
        if optimalTranslation ~= nil then
            local newTransform = LinearTransform(
                currentTransform.left, currentTransform.up, currentTransform.forward,
                optimalTranslation
            )
            bot:SpawnBot(newTransform,CharacterPoseType.CharacterPoseType_Stand , self.soldierBlueprint, nil, {}, nil)
            bot.objective = self:GetNearestEnemyObjectiveEntity(newTransform.trans, TeamId.Team1)
            bot.path_step = 1
            bot.path = {}
            bot.action = Actions.ATTACK
            return true
        else
            return false
        end
    end

    local currentTransform = Transform:Clone()
    local newPos = VecLib:RandomPointInRadius(currentTransform.trans, 25.0)
    currentTransform = LinearTransform(
        currentTransform.left, currentTransform.up, currentTransform.forward,
        Vec3(newPos.x, currentTransform.trans.y, newPos.z)
    )
    bot:SpawnBot(currentTransform,CharacterPoseType.CharacterPoseType_Stand , soldierBlueprint, nil, {}, nil)
    bot.objective = self:GetNearestEnemyObjectiveEntity(currentTransform.trans, TeamId.Team1)
    bot.path_step = 1
    bot.path = {}
    bot.action = Actions.ATTACK
    return true
end

function BotsManager:SpawnBotOnTransform(Transform, Bot)
    --US
    local soldierBlueprint = ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))
    local soldierKit = ResourceManager:SearchForInstanceByGuid(Guid('0A99EBDB-602C-4080-BC3F-B388AA18ADDD'))
    
    --RU
    if Bot.teamId == TeamId.Team2 then
        soldierBlueprint = ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))
        soldierKit = ResourceManager:SearchForInstanceByGuid(Guid('DB0FCE83-2505-4948-8661-660DD0C64B63'))
    end
    Bot:SpawnBot(Transform, CharacterPoseType.CharacterPoseType_Stand , soldierBlueprint, soldierKit, {}, nil)

end

function BotsManager:SpawnBotAtEntity(entity, bot)
    --US
    local soldierBlueprint = ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))
    local soldierKit = ResourceManager:SearchForInstanceByGuid(Guid('0A99EBDB-602C-4080-BC3F-B388AA18ADDD'))
    
    --RU
    if bot.teamId == TeamId.Team2 then
        soldierBlueprint = ResourceManager:SearchForInstanceByGuid(Guid('261E43BF-259B-41D2-BF3B-9AE4DDA96AD2'))
        soldierKit = ResourceManager:SearchForInstanceByGuid(Guid('DB0FCE83-2505-4948-8661-660DD0C64B63'))
    end
   
    local currentTransform = LinearTransform(
        1.0
    )
    bot:SpawnBot(currentTransform, CharacterPoseType.CharacterPoseType_Stand , soldierBlueprint, soldierKit, {}, entity)
    bot.objective = self:GetNearestEnemyObjectiveEntity(currentTransform.trans, TeamId.Team1)
    bot.path_step = 1
    bot.path = {}
    bot.action = Actions.ATTACK
end

function BotsManager:RespawnBot(bot)
    -- first priority is to spawn on squadmate
    if self.lock_respawn then
        return
    end

    local has_spawned_on_squadmate = false
    local has_spawned_on_objective = false
    local players_in_squad = PlayerManager:GetPlayersBySquad(bot.player_controller.teamId, bot.player_controller.squadId)
    local alive_players_in_squad = {}
    if #players_in_squad > 0 then
        for x, p in pairs(players_in_squad) do
            if p.alive then
                alive_players_in_squad[x] = p
            end
        end
        if #alive_players_in_squad > 0 then
            local choice = alive_players_in_squad[math.random(1, #alive_players_in_squad)]
                if choice ~= nil then
                
                    has_spawned_on_squadmate = self:SpawnBotAroundTransform(choice.soldier.transform, bot)
                    bot.target = nil
            end
        end
    end

    if not has_spawned_on_squadmate then
        local friendly_objectives = self:GetAllObjectivesForTeam(bot.player_controller.teamId)
        if #friendly_objectives > 0 then
            local choice = friendly_objectives[math.random(1, #friendly_objectives)]
            if choice ~= nil then
                -- first, try spawn on objective entity
                local successfulSpawn = bot.player_controller:Spawn(choice, false)
                if (not successfulSpawn) then
                    
                    has_spawned_on_objective = self:SpawnBotAroundTransform(choice.transform , bot)
                else
                    print("Successfully spawned on entity")
                    has_spawned_on_objective = true
                end
                -- self:SpawnBotAtEntity(choice, bot)
                bot.target = nil
            end
        end
    end

    if (not (has_spawned_on_objective and has_spawned_on_squadmate)) then
        local choice = self:GetRandomSpawnPoint(bot.player_controller.teamId)
        if choice ~= nil then
            local transform = LinearTransform(
                1.0
            )

            transform:Translate(Vec3(
                choice.x + math.random(-10, 10)+ math.random(-10, 10),
                choice.y - 0.6,
                choice.z + math.random(-10, 10)+ math.random(-10, 10)
            ))
            print("Attempting to spawn bot")
            self:SpawnBotAroundTransform(transform:Clone(), bot)
        end
    end
end

-- GetBotThatTargets
-- target : Player
function BotsManager:GetBotThatTargets(target)
    local foundBot = nil
    for _, bot in pairs(self.bots) do
        if bot.target ~= nil then
            if bot.target == target then
                print("found bot")
                foundBot = bot
                break
            end
        end 
    end
    print("returning bot")
    return foundBot
end

-- GetBotFromSoldier
function BotsManager:GetBotFromSoldier(soldier)
    local foundBot = nil
    for _, bot in pairs(self.bots) do
        if bot.player_controller.id == soldier.player.id then
            foundBot = bot
            break
        end
    end
    return foundBot
end

if g_BotsManager == nil then
    g_BotsManager = BotsManager()
end

return g_BotsManager