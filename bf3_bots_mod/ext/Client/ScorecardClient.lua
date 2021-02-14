class "ScorecardClient"
local NavGrid = require("__shared/NavGrid")

Events:Subscribe('Extension:Loaded', function()
    WebUI:Init()
end)

function ScorecardClient:DrawPolyline(Polyline)
    for idx, line in pairs(Polyline) do
        if idx < #Polyline then
            local start_point = Polyline[idx]
            local end_point = Polyline[idx+1]
			DebugRenderer:DrawLine(start_point, end_point, Vec4(1,0,0,1), Vec4(1,0,0,1))
        end
    end
end

function ScorecardClient:__init()
    self.min_point = nil
    self.max_point = nil

    self.step_size_x = 0
    self.step_size_y = 0
    self.steps = 32
    self.current_step = 0
    self.current_step_x = 0
    self.current_step_y = 0
    self.ready_to_go = false
    self.scorecard_grid = nil
    self.encoded_grid = ""
    self.encoded_scores = ""
    self.encoded_score_results = {}
    self.completed = false

    -- ui
    self.is_showing_navtools = true
    self.is_recording = false
    self.recording_mode = 0
    self.last_update_time = 0
    -- pos
    self.record_last_update_time = 0
    --
    self.preview_path = nil
    --
    self.sample_radius = 1.0
    -- pathfinding debug
    self.pathfind_start = nil
    self.pathfind_end = nil
    -- model
    self.profile = {}
    --
    self.project_id = 0
    --
    self.width = 0
    self.height = 0
    --
    self.elevation_based_scoring = false

    NetEvents:Subscribe("OnRequestScorecardGrid", self, self.OnRequestScorecardGrid)
	NetEvents:Subscribe("OnSetPath", self, self.OnSetPath)

    -- Events:Subscribe('UpdateManager:Update', self, self.Tick)
    Events:Subscribe("UI:DrawHud", self, self.TickUI)
    Events:Subscribe("OnSetSampleRadius", self, self.OnSetSampleRadius)
    Events:Subscribe("StartBuild", self, self.StartBuild)
    Events:Subscribe('OnSetActiveProject', self, self.OnSetActiveProject)
    Events:Subscribe("OnUpdateBotSettings", self, self.OnUpdateBotSettings)
end

function ScorecardClient:OnUpdateBotSettings(data)
    print('request update bot settings')
    local data = json.decode(data)
    print(data.aimWhenFiring)
    print(data)
    local firingOffset = Vec3(
        data.firingOffsetX,
        data.firingOffsetY,
        data.firingOffsetZ
    )
    local firingBaseOffset = Vec3(
        data.firingBaseOffsetX,
        data.firingBaseOffsetY,
        data.firingBaseOffsetZ
    )
    local aimWhenFiring = data.aimWhenFiring
    NetEvents:Send("OnUpdateBotSettings", firingOffset, firingBaseOffset, aimWhenFiring)
end

function ScorecardClient:OnSetActiveProject(data)
    
    local data = json.decode(data)
    self.project_id = math.floor(tonumber(data.project_id))
    self.profile = data.profile
    local profile = data.profile
    print("Set active project to... "..self.project_id)
    NetEvents:Send("OnSetActiveProject", self.project_id, profile)
end

function ScorecardClient:StartBuild(in_data)
    print("StartBuild")
    print(in_data)
    local data = json.decode(in_data)
    print(data)
    self.profile = data.profile
    self.project_id = data.project_id
    NavGrid.profile = self.profile
    NavGrid.project_id = self.project_id
    local settings = data.build_settings
    self.steps = tonumber(settings.voxel_step_size)
    self.step_size_x = settings.iterations_x / self.steps
    self.step_size_y = settings.iterations_y / self.steps
    self.min_point = Vec3(
        tonumber(settings.start.x),
        tonumber(settings.start.y),
        tonumber(settings.start.z)
    )
    self.max_point = Vec3(
        tonumber(settings["end"].x),
        tonumber(settings["end"].y),
        tonumber(settings["end"].z)
    )
    if (self.scorecard_grid ~= nil) then
        self.scorecard_grid:Destroy()
        self.scorecard_grid = nil
        self.current_step_x = 0
        self.current_step_y = 0
        self.current_step = 0
        self.completed = false
    end
    self.elevation_based_scoring = in_data.elevation_based_scoring
    local headers = {}
    local options = HttpOptions(headers, 918292)
    options:SetHeader('Level', SharedUtils:GetLevelName())
    options:SetHeader('Authorization', 'Token '..self.profile.token)
    options:SetHeader("Size-X", tostring(settings.iterations_x))
    options:SetHeader("Size-Y", tostring(settings.iterations_y))
    options:SetHeader("Min-X", tostring(self.min_point.x))
    options:SetHeader("Min-Y", tostring(self.min_point.z))
    options:SetHeader("Max-X", tostring(self.max_point.x))
    options:SetHeader("Max-Y", tostring(self.max_point.z))
    local url = 'http://127.0.0.1:8000/v1/project/'..tostring(math.floor(self.project_id))..'/level/reset/rasters/'
    local result = Net:PostHTTPAsync(url, '', options, self, self.OnLevelRastersReset)
    print(result)
    
end

function ScorecardClient:OnLevelRastersReset(result)
    print(result)
    print('step size ' .. self.step_size_x)
    self.width = self.step_size_x * self.steps
    self.height = self.step_size_y * self.steps
    self.ready_to_go = true
end

function ScorecardClient:OnSetSampleRadius(new_radius)
    print("New radius: "..new_radius)
    self.sample_radius = new_radius
end

function ScorecardClient:TickUI()
    if self.preview_path ~= nil then
        self:DrawPolyline(self.preview_path)
    end
end

function ScorecardClient:OnSetPath(path)
    self.preview_path = path
end

function ScorecardClient:OnRequestScorecardGrid(size_x, size_z, min_point, max_point)
    self.step_size_x = size_x/self.steps
	self.step_size_y = size_z/self.steps
	self.max_point = max_point
    self.min_point = min_point
    print("ScorecardClient: ".."Total grid size: "..size_x.." "..size_z)
    print("ScorecardClient: ".."Total grid step size: "..self.step_size_x.." "..self.step_size_y)
    
    self.ready_to_go = true
    
end

function ScorecardClient:CanVisualize()
    if self.current_step >= self.steps then
        return true
    end
    return false
end

function ScorecardClient:OnNavgridComplete(data)
end

-- note: this only executes if player.soldier is valid. [check __init__.lua]
function ScorecardClient:Tick(deltaTime, pass, local_player)
    if(pass ~= UpdatePass.UpdatePass_PreSim) then
        return
    end
    
    -- print("ChangePose: ".. 
    --     tostring(local_player.input:GetLevel(EntryInputActionEnum.EIAChangePose)) ..
    --     " QuicktimeCrouchDuck: ".. tostring(local_player.input:GetLevel(EntryInputActionEnum.EIAQuicktimeCrouchDuck))..
    --     " Clutch: ".. tostring(local_player.input:GetLevel(EntryInputActionEnum.EIAClutch))..
    --     " Throttle: ".. tostring(local_player.input:GetLevel(EntryInputActionEnum.EIAThrottle))..
    --     " GearDown: ".. tostring(local_player.input:GetLevel(EntryInputActionEnum.EIAGearDown))..
    --     " GearUp: ".. tostring(local_player.input:GetLevel(EntryInputActionEnum.EIAGearUp))..
    --     " Handbrake: ".. tostring(local_player.input:GetLevel(EntryInputActionEnum.EIAHandBrake))..
    --     " Brake: ".. tostring(local_player.input:GetLevel(EntryInputActionEnum.EIABrake))
    --    )

     -- print('throttle: '.. local_player.input:GetLevel(EntryInputActionEnum.EIAThrottle))
    
	-- local local_player = PlayerManager:GetLocalPlayer()
    WebUI:ExecuteJS("window.GameSyncManager.updateCurrentPosition("..
      local_player.soldier.transform.trans.x.." ,"..local_player.soldier.transform.trans.y.." ,"..local_player.soldier.transform.trans.z..");")
    WebUI:ExecuteJS("window.GameSyncManager.updateCurrentLevelName('".. SharedUtils:GetLevelName() .. "');")
    if ((SharedUtils:GetTime() - self.last_update_time) > 0.2) then
        if InputManager:IsKeyDown(InputDeviceKeys.IDK_F1) then

            if self.is_showing_navtools then
                -- WebUI:ExecuteJS("window.Index.setShowNavtools(false);")
                WebUI:ExecuteJS("window.GameSyncManager.resetFocus();")
                self.is_showing_navtools = false
            else
                -- WebUI:ExecuteJS("window.Index.setShowNavtools(true);")
                WebUI:ExecuteJS("window.GameSyncManager.enableFocus();")
                self.is_showing_navtools = true
            end
        end
        if InputManager:IsKeyDown(InputDeviceKeys.IDK_F2) then
            -- if self.is_recording then
            --     WebUI:ExecuteJS("window.Index.setRecording(false);")
            --     self.is_recording = false
            -- else
            --     WebUI:ExecuteJS("window.Index.setRecording(true);")
            --     self.is_recording = true
            -- end
            local start = local_player.soldier.transform.trans + Vec3(0, 2, 0)
            local rayTest = RaycastManager:DetailedRaycast(start, start + (local_player.soldier.transform.forward*6000), 10, MaterialFlags.MfPenetrable | MaterialFlags.MfClientDestructible, 1)
            for idx, t in pairs(rayTest) do
                print('Hit Index: '..idx)
                if t ~= nil then
                    print('hit@ : '..t.position.x..' '..t.position.y..' '..t.position.z)
                end 
            end
            local hits = NavGrid.NestedRaycast(start, start + (local_player.soldier.transform.forward*6000), local_player.soldier.transform.forward, 5)
            if #hits > 0 then
                self.preview_path = {
                    start:Clone(), hits[1].position:Clone()
                }
            end
            for index, hit in pairs(hits) do
                print('layered hit: '..index)
                print('hit: '..hit.position.x..' '..hit.position.y..' '..hit.position.z)
                if hit.rigidBody ~= nil then
                    print(hit.rigidBody.typeInfo.name.. ' '..tostring(hit.rigidBody.data))
                    if hit.rigidBody.data ~= nil then
                        print('hit rigidBody '..hit.rigidBody.data.instanceGuid.ToString('D'))
                    end
                end
                -- if hit.material ~= nil then
                --     print('hit material '..hit.material.typeInfo.name)
                -- end
            end
        end
        if InputManager:IsKeyDown(InputDeviceKeys.IDK_F3) then
            if self.recording_mode == 1 then
                WebUI:ExecuteJS("window.Index.setMode(0);")
                self.recording_mode = 0
            end
        end
        if InputManager:IsKeyDown(InputDeviceKeys.IDK_F4) then
            if self.recording_mode == 0 then
                WebUI:ExecuteJS("window.Index.setMode(1);")
                self.recording_mode = 1
            end
        end
        if InputManager:IsKeyDown(InputDeviceKeys.IDK_F5) then
            self.pathfind_start = local_player.soldier.transform.trans
        end
        if InputManager:IsKeyDown(InputDeviceKeys.IDK_F6) then
            self.pathfind_end = local_player.soldier.transform.trans
            if (self.pathfind_start ~= nil) then
                NetEvents:Send("OnScorecardRequestPath", self.pathfind_start, self.pathfind_end)
            end
        end
        self.last_update_time = SharedUtils:GetTime()
    end
    if local_player ~= nil then
        if (SharedUtils:GetTime() - self.record_last_update_time) > 0.4 and self.is_recording then
            NetEvents:Send("OnScorecardCostModification", self.recording_mode, self.sample_radius)
            -- print("Sending scorecard mod update")
            self.record_last_update_time = SharedUtils:GetTime()
        end
    end

    local size_x = self.step_size_x * self.steps
    local size_y = self.step_size_y * self.steps
    if self.ready_to_go then
        if self.current_step_y < self.steps then
            local start_of_grid_x = (self.step_size_x * self.current_step_x)+1
            local start_of_grid_y = (self.step_size_y * self.current_step_y)+1
            local end_of_grid_x = (self.step_size_x * (self.current_step_x+1))+1
            local end_of_grid_y = (self.step_size_y * (self.current_step_y+1))+1
            if self.scorecard_grid == nil then
                self.scorecard_grid = NavGrid.CreateFromBounds(
                    end_of_grid_x, end_of_grid_y, self.min_point, self.max_point,
                    start_of_grid_x, start_of_grid_y, self.profile, self.project_id,
                    self.width, self.height, self.elevation_based_scoring
                )
            else
                self.scorecard_grid:Extend(
                    end_of_grid_x, end_of_grid_y, self.min_point, self.max_point,
                    start_of_grid_x, start_of_grid_y,
                    self.width, self.height
                )
            end
            self.current_step_y = self.current_step_y + 1
        end
        if self.current_step_y >= self.steps then
            if self.current_step_x+1 < self.steps then 
                self.current_step_x = self.current_step_x + 1
                self.current_step_y = 0
                WebUI:ExecuteJS("window.GameSyncManager.updateBuildProgress("..tostring(self.current_step_x / self.steps)..");")
            else
                self.ready_to_go = false
                self.completed = true
                WebUI:ExecuteJS('window.GameSyncManager.onFinishBuild();')
                print("Completed")

                -- local data, error = json.encode(self.scorecard_grid.grid_scores)
                -- print("Encoded data")
                -- local encoded_scores = json.encode(self.scorecard_grid.grid_scores)
                -- print("Data ".."length: "..#encoded_scores)

                -- send here
                -- local headers = {}
                -- local options = HttpOptions(headers, 90)
                -- -- options:SetHeader('Content-Type', 'application/json')
                -- -- options:SetHeader('Content-Length', tostring(#encoded_scores))
                -- options:SetHeader('Level', SharedUtils:GetLevelName())
                -- options:SetHeader('Authorization', 'Token '..self.profile.token)
                -- local url = 'http://127.0.0.1:8000/v1/project/'..tostring(math.floor(self.project_id))..'/level/add-block/complete/'
                -- local result = Net:PostHTTPAsync(url, '', options, self, self.OnNavgridComplete)
                -- print(result)
-- 
                -- NetEvents:SendUnreliable(
                --     "OnScorecardEncoded", 
                --     encoded_scores, 
                --     self.step_size_x*self.steps, 
                --     self.step_size_y*self.steps, 
                --     self.min_point.x, 
                --     self.min_point.z ,
                --     self.max_point.x, 
                --     self.max_point.z)

                -- if data == nil then
                --     print("Data error: "..error)
                --     print("We need to check errors... ")
                --     self.scorecard_grid:CheckForErrors()
                --     print("After going through : "..self.scorecard_grid.iterations.." Iterations")
                -- else
                --     print(encoded_scores)
                -- end
            end
        end
    end
    -- if self.current_step_y < self.steps and self.ready_to_go then 
    --     local start_of_grid_x = (self.step_size_x * self.current_step_x)+1
    --     local start_of_grid_y = (self.step_size_y * self.current_step_y)+1
    --     local end_of_grid_x = (self.step_size_x * (self.current_step_x+1))+1
    --     local end_of_grid_y = (self.step_size_y * (self.current_step_y+1))+1
    --     if self.scorecard_grid == nil then
    --         self.scorecard_grid = NavGrid.CreateFromBounds(
    --             end_of_grid_x, end_of_grid_y, self.min_point, self.max_point,
    --             start_of_grid_x, start_of_grid_y
    --         )
    --     else
    --         self.scorecard_grid:Extend(
    --             end_of_grid_x, end_of_grid_y, self.min_point, self.max_point,
    --             start_of_grid_x, start_of_grid_y
    --         )
    --         
    --     end
    --     local r, error = json.encode(self.scorecard_grid.grid_scores)
    --     if r == nil then
    --         print(error)
-- 
    --     end
    --     -- table.insert(self.encoded_score_results, json.encode(self.scorecard_grid.grid_scores))
    --     self.current_step_y = self.current_step_y + 1
    -- elseif self.current_step_y >= self.steps and self.ready_to_go then
    --     if self.current_step_x >= self.steps then
    --         self.ready_to_go = false
    --     end
    --     -- self.encoded_ = json.encode(self.encoded_score_results)
    --     self.current_step_y = 0
    --     self.current_step_x = self.current_step_x + 1
    --     
    --     --print(self.encoded_)
    --     --NetEvents:SendUnreliable("OnScorecardEncoded", self.encoded_)
    -- end

end
 
if not g_ScorecardClient then
    g_ScorecardClient = ScorecardClient()
end
return g_ScorecardClient