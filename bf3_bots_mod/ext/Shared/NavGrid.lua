class 'NavGrid'

-- cached world entities
local cachedSpatialEntities = {}
local cachedSpatialWorldBox = {}

profile = {}
project_id = {}

-- utilities

function IsPointInsideBox(point, box)
    return point.x <= box.max.x and point.y <= box.max.y and point.z <= box.max.z and
        point.x >= box.min.x and point.y >= box.min.y and point.z >= box.min.z
end

function Intersect(Box1, Box2)
    if ((Box1.min.x > Box2.max.x) or (Box2.min.x > Box1.max.x)) then
        return false
    end
    if ((Box1.min.y > Box2.max.y) or (Box2.min.y > Box1.max.y)) then
        return false
    end
    if ((Box1.min.z > Box2.max.z) or (Box2.min.z > Box1.max.z)) then
        return false
    end

    return true
end

function AreWeOverlapping(Box1, Box2)
    
    --if Box2.min.magnitude >= 400 or Box2.max.magnitude >= 400 then
      --  return false
    --end
    --local _Box1 = AxisAlignedBox(Box1.min + Transform1.trans, Box1.max + Transform1.trans)
   -- local areWeInside = IsPointInsideBox(Transform2.trans, Box1)
    --local _Box2 = nil
    --if Box2.min.magnitude == 0.0 or Box2.max.magnitude == 0.0 then
        --_Box2 = AxisAlignedBox(Box2.min+Vec3(-1.0, -1.0, -1.0) + Transform2.trans, Box2.max+ Vec3(1.0, 1.0, 1.0)+ Transform2.trans)
    --else
        --_Box2 = AxisAlignedBox( Transform2 * Box2.min, Transform2 * Box2.max)
        -- _Box2 = AxisAlignedBox(Box2.min, Box2.max)
    --end
    

    -- print("AreWeOverlapping?".. "_Box 1: ".. "Min: "..
    --     _Box1.min.x .." ".._Box1.min.y.." ".._Box1.min.z..
    --     "Max: ".._Box1.max.x .." ".._Box1.max.y.." ".._Box1.max.z..
    --     " _Box 2: ".. "Min: "..
    --     _Box2.min.x .." ".._Box2.min.y.." ".._Box2.min.z..
    --     "Max: ".._Box2.max.x .." ".._Box2.max.y.." ".._Box2.max.z ..
    --     " Magnitude ".._Box2.min.magnitude
    -- )
    return Intersect(Box1, Box2)
    -- return 
    --     (_Box1.min.x < _Box2.max.x and _Box2.min.x < _Box1.max.x and
    --     _Box1.min.y < _Box2.max.y and _Box2.min.y < _Box1.max.y and
    --     _Box1.min.z < _Box2.max.z and _Box2.min.x < _Box1.max.z)-- or areWeInside
end
-- todo: cache world boxes for grid

function NavGrid.AddCache(entity, entity_box)
    table.insert(cachedSpatialEntities, entity)
    table.insert(cachedSpatialWorldBox, entity_box)
end

function NavGrid:__init()
    self.center_transform = nil
    -- size in both directions (+- 5)
    self.grid_size_x = 1.5
    self.grid_size_y = 1.5

    self.grid = {}
    self.grid_scores=  {}

    -- store our transforms seperately
    self.grid_transforms = {}
    --
    self.cell_size = 1.0
    -- sampleRadius
    self.sample_radius = self.grid_size_x * self.cell_size
    -- cached path
    self.cached_path  = {}
    -- grid_centers - this will be reset per pathfinding call
    self.box_centers = {}
    -- explored grid, again this will be reset per pathfinding call
    self.explored_grid = {}

    -- debug
    self.errors = {}
    self.iterations = 0
    self.encoded_scores = {}

    self.profile = {}
    self.project_id = 0
    
    
    if #cachedSpatialEntities == 0 then
        local ToLookFor = "ServerVegetationTreeEntity"
        if SharedUtils:IsClientModule() then
            ToLookFor = "ClientVegetationTreeEntity"
        end

        local it = EntityManager:GetIterator(ToLookFor)
        local obj = it:Next()
        if obj ~= nil then 
            
            local value = 0.0
            while obj ~= nil and value == 0.0 do
                obj = SpatialEntity(obj)
                table.insert(cachedSpatialEntities, obj)
                table.insert(cachedSpatialWorldBox, 
                    AxisAlignedBox(
                        obj.transform * obj.aabb.min,
                        obj.transform * obj.aabb.max
                    ))
                obj = it:Next()
            end
        end
    end
end

function NavGrid:Destroy()
    self.grid = {}
    self.grid_scores = {}
    self.grid_transforms = {}
    self.cached_path = {}
    self.profile = {}
    self.encoded_scores = {}
end

function NavGrid.OnUnloadStatic()
    print("Unloading navgrid cache")
    cachedSpatialWorldBox = {}
    cachedSpatialEntities = {}
end
-- static

function NavGrid.TransformBox(Box, Transform)
    local tr = Transform:Clone()
    return AxisAlignedBox(tr* Box.min, tr* Box.max)
end

function NavGrid.NormalizeTransform(Transform)
    
    return LinearTransform(
        Vec3(1.0, 0.0, 0.0), Vec3(0.0, 1.0, 0.0), Vec3(0.0, 0.0, 1.0),
        Transform.trans
    )

end

function NavGrid.FloorTransform(Transform)
    return LinearTransform(
        Transform.left, Transform.up, Transform.forward,
        Vec3(
            math.floor(Transform.trans.x),
            math.floor(Transform.trans.y),
            math.floor(Transform.trans.z)
        )
    )
end 

function NavGrid.ShrinkBox(Box, Amount)
    return AxisAlignedBox(
        Vec3(Box.min.x+Amount, Box.min.y+Amount, Box.min.z+Amount), 
        Vec3(Box.max.x - Amount, Box.max.y - Amount, Box.max.z - Amount))
end

-- Size: Vec3 - CenterPosition: Vec3
function NavGrid.BoxFromCenter(Size, CenterPosition)
    return AxisAlignedBox(
            CenterPosition - (Size * 0.5),
            CenterPosition + (Size * 0.5)
    )
end

function NavGrid.Create(transform)
    local self = NavGrid()
    -- reminder, that the y axis is up
    self.center_transform = transform:Clone()
    --self.center_transform:Translate(Vec3(0.0, 0.0, 0.0))
    local start_x = -(self.grid_size_x)-0.5
    local start_y = -(self.grid_size_y)-0.5
    local offset_per_axis = self.cell_size

    for x = 1, self.grid_size_x*2 do
        self.grid[x] = {}
        self.grid_scores[x] =  {}
        for y = 1, self.grid_size_y*2 do
            local cell_adj_size = self.cell_size * 2
            local offset_x = self.grid_size_x*0.5
            local offset_y = self.grid_size_y*0.5
            -- self.grid[x][y] = AxisAlignedBox(
            --     Vec3(
            --         -(self.cell_size+((x-1)*cell_adj_size))+offset_x, 
            --         -self.cell_size, 
            --         -(self.cell_size+((y-1)*cell_adj_size))+offset_y
            --     ), 
            --     Vec3(
            --         (self.cell_size+((x-1)*cell_adj_size))+offset_x, 
            --         self.cell_size, 
            --         (self.cell_size+((y-1)*cell_adj_size))+offset_y
            --     )
            -- )
            local position = Vec3(
                start_x + ((x-1)*offset_per_axis),
                0.0,
                start_y + ((y-1)*offset_per_axis)
            )
            self.grid[x][y] = NavGrid.BoxFromCenter(Vec3(self.cell_size, self.cell_size, self.cell_size), position)

            self.grid_scores[x][y] = 0.0
        end
    end
    -- self:UpdateScores()
    return self
end



function NavGrid.CreateFromBounds(size_x, size_z, min_point, max_point, start_x, start_z, profile, project_id, width, height)
    local self = NavGrid()
    self.profile = profile
    self.project_id = project_id
    local center_position = min_point + Vec3(self.cell_size/2, self.cell_size/2, self.cell_size/2)
    center_position = Vec3(center_position.x, center_position.y+300, center_position.z)
    --local jsonContentScores = '{ "scores": ['
    local cacheData = {}
    local index = 1
    for x=start_x, size_x do
        -- if self.grid[x] == nil then
        --     self.grid[x] = {}
        -- end
        --if self.grid_scores[x] == nil then
        --    self.grid_scores[x] = {}
        --end
        for y=start_z, size_z do
            -- self.grid_scores[x][y] = {}

            local position = center_position + Vec3(
                (self.cell_size*(x-1)),
                0,
                (self.cell_size*(y-1))
            )
            local rayResult = RaycastManager:Raycast(position, Vec3(position.x, position.y-600, position.z), RayCastFlags.IsAsyncRaycast)
            local elevation = 0.0
            local rayScoreC = {{}}
            rayScoreC[1]['elevation'] = 0.0
            rayScoreC[1]['value'] = 0.0
            if (rayResult) then
                local rayScore = self:RaycastAndScore(position,Vec3(position.x, rayResult.position.y-1.0,position.z), rayResult.position.y)
                -- self.grid_scores[x][y][1] = rayScore
                -- self.grid_scores[x][y][2] = rayResult.position.y
                if rayScore[1] ~= nil then
                    elevation = rayScore[1]['elevation']
                    rayScoreC = rayScore
                end
            else
                -- self.grid_scores[x][y][1] = 1200
                -- self.grid_scores[x][y][2] = 0
                rayScoreC = {}
            end
            cacheData[index] = {}
            cacheData[index]['x'] = x
            cacheData[index]['y'] = y
            cacheData[index]['elevation'] = elevation
            cacheData[index]['values'] = rayScoreC
            --local content = "{"..'"value": '..self.grid_scores[x][y].." ,"..'"x": '..x.." ,"..'"y": '..y.." }, "
            --jsonContentScores = jsonContentScores..content
            self.iterations = self.iterations  +1
            index = index + 1
            -- self.grid[x][y] = NavGrid.BoxFromCenter(Vec3(self.cell_size, self.cell_size, self.cell_size), position)
        end
    end
    --jsonContentScores = jsonContentScores.." ]}"
    --table.insert(self.encoded_scores, jsonContentScores)
    local dataToPush = json.encode(cacheData)
    local headers = {}
    local options = HttpOptions(headers, 90)
    options:SetHeader("Content-Type", "application/json")
    options:SetHeader("Content-Length", tostring(#dataToPush))
    options:SetHeader("Size-X", tostring(width))
    options:SetHeader("Size-Y", tostring(height))
    options:SetHeader("Min-X", tostring(min_point.x))
    options:SetHeader("Min-Y", tostring(min_point.z))
    options:SetHeader("Max-X", tostring(max_point.x))
    options:SetHeader("Max-Y", tostring(max_point.z))
    options:SetHeader("Level", SharedUtils:GetLevelName())
    options:SetHeader("Authorization", "Token " .. self.profile.token)
    local result = Net:PostHTTPAsync('http://127.0.0.1:8000/v1/project/'..tostring(math.floor(self.project_id))..'/level/add-block/', dataToPush, options, self, self.OnPostBlock)

    return self
end

function NavGrid:RaycastAndScore(Start, End, OldScore)

    local hits = self.NestedRaycast(Start, End, Vec3(0.0, -1.0, 0.0), 5)
    local results = {} -- { 1: { value: 0.0, elevation: 0.0 } }
    for _, hit in pairs(hits) do
        local score = 256
        local elevation = -6969420
        if hit ~= nil then
            if hit.rigidBody ~= nil then
                if hit.rigidBody:Is("TerrainPhysicsEntity") or hit.rigidBody:Is("ClientTerrainEntity") then
                    score = 0.0
                    elevation = hit.position.y
                elseif hit.rigidBody:Is("BreakablePhysicsEntity") or hit.rigidBody:Is("StaticPhysicsEntity") then
                    score = 256
                    elevation = hit.position.y
                elseif hit.rigidBody:Is("ClientWaterEntity") or hit.rigidBody:Is("WaterPhysicsEntity") then
                    score = 500
                    elevation = hit.position.y - 3
                else
                    score = 700
                    elevation = hit.position.y
                end
            end
            local r = {}
            r['value'] = score
            r['elevation'] = elevation
            table.insert(results, r)
        end
    end

    return results
end
    --    local rayResult = RaycastManager:SpatialRaycast(Start, End, SpatialQueryFlags.AllGrids)
	--    local ray = RaycastManager:DetailedRaycast(Start, End, 3, 16777215, 1)
    --    
    --    local score = 0.0
    --    if ray ~= nil then
    --        for _, rayHit in pairs(ray) do
    --            if rayHit ~= nil then
    --                if rayHit.rigidBody ~= nil then
    --                    if rayHit.rigidBody:Is("TerrainPhysicsEntity") then --or rayHit.rigidBody:Is("StaticPhysicsEntity") then
    --                        --NetEvents:Send("OnScorecardMessage", rayHit.rigidBody.typeInfo.name)
    --                        score = 0.0
    --                    else
    --                        score = 256
    --                    end
    --                end 
    --                
    --            end
    --        end
    --    end
    --    local isTerrain = false
    --    
    --    local isWater = false
    --    local isStructure = false
    --    if (rayResult ~= nil) then
    --        for _, entity in pairs(rayResult) do
    --            if entity:Is("ClientTerrainEntity") then
    --                isTerrain = true
    --            end
    --            if entity:Is("ClientWaterEntity") then
    --                local spe = SpatialEntity(entity)
    --                if spe.aabb.max.y > OldScore then
    --                    isWater = true
    --                end
    --            end
    --            if entity:Is("BreakablePhysicsEntity") then --or entity:Is("GroupPhysicsEntity") then
    --                isStructure = true
    --            end
    --        end
    --    else
    --        score = 2048.0
    --    end
    --    -- if (isTerrain and (not isWater) and (not isStructure)) then
    --    --     score = 0 + OldScore
    --    if isWater then
    --        score = 500-- + OldScore
    --    --elseif isStructure then
    --    --    score = 100 + OldScore
    --    end
    --    return score


function NavGrid:Extend(size_x, size_z, min_point, max_point, start_x, start_z, width, height)
    local center_position = min_point + Vec3(self.cell_size/2, self.cell_size/2, self.cell_size/2)
    center_position = Vec3(center_position.x, center_position.y+300, center_position.z)
    --local jsonContentScores = '{ "scores": ['
    local cacheData = {} -- {{ x: x, y: y, elevation: 0.0, values: {0.0, 1.0, 2.0, 3.0, 4.0, 5.0} }}
    local index = 1
    for x=start_x, size_x do
        -- if self.grid[x] == nil then
        --     self.grid[x] = {}
        -- end
        -- if self.grid_scores[x] == nil then
        --     self.grid_scores[x] = {}
        -- end
        for y=start_z, size_z do
            -- self.grid_scores[x][y] = {}
            local position = center_position + Vec3(
                (self.cell_size*(x-1)),
                0,
                (self.cell_size*(y-1))
            )
            local rayResult = RaycastManager:Raycast(position, Vec3(position.x, position.y-6000, position.z), RayCastFlags.IsAsyncRaycast)
            local elevation = 0.0
            local rayScoreC = {{}}
            rayScoreC[1]['elevation'] = 0.0
            rayScoreC[1]['value'] = 0.0
            if (rayResult) then
                local rayScore = self:RaycastAndScore(position,Vec3(position.x, rayResult.position.y-1.0,position.z), rayResult.position.y)
                -- self.grid_scores[x][y][1] = rayScore
                -- self.grid_scores[x][y][2] = rayResult.position.y
                if (rayScore[1] ~= nil) then
                    elevation = rayScore[1]['elevation']
                    rayScoreC = rayScore
                end
            else
                -- self.grid_scores[x][y][1] = 1200
                -- self.grid_scores[x][y][2] = 0
                rayScoreC = {}
            end
            cacheData[index] = {}
            cacheData[index]['x'] = x
            cacheData[index]['y'] = y
            cacheData[index]['elevation'] = elevation
            cacheData[index]['values'] = rayScoreC
            --local content = "{"..'"value": '..self.grid_scores[x][y].." ,"..'"x": '..x.." ,"..'"y": '..y.." }, "
            --jsonContentScores = jsonContentScores..content
            self.iterations = self.iterations  +1
            index = index + 1
            -- self.grid[x][y] = NavGrid.BoxFromCenter(Vec3(self.cell_size, self.cell_size, self.cell_size), position)
        end
    end

    local dataToPush = json.encode(cacheData)

    local headers = {}
    local options = HttpOptions(headers, 90)
    options:SetHeader("Content-Type", "application/json")
    options:SetHeader("Content-Length", tostring(#dataToPush))
    options:SetHeader("Size-X", tostring(width))
    options:SetHeader("Size-Y", tostring(height))
    options:SetHeader("Min-X", tostring(min_point.x))
    options:SetHeader("Min-Y", tostring(min_point.z))
    options:SetHeader("Max-X", tostring(max_point.x))
    options:SetHeader("Max-Y", tostring(max_point.z))
    options:SetHeader("Level", SharedUtils:GetLevelName())
    options:SetHeader("Authorization", "Token " .. self.profile.token)
    local result = Net:PostHTTPAsync('http://127.0.0.1:8000/v1/project/'..tostring(math.floor(self.project_id))..'/level/add-block/', dataToPush, options, self, self.OnPostBlock)
    --jsonContentScores = jsonContentScores.." ]}"
    --table.insert(self.encoded_scores, jsonContentScores)
end

function NavGrid:OnPostBlock(result)
end

function NavGrid:CheckForErrors()

    for x, grid in pairs(self.grid_scores) do
        print("Length of table at X: "..x.." "..#self.grid_scores[x])
        
    end
end

function NavGrid.CreateFrom(grid, transform)
    local self = NavGrid()
    self.center_transform = transform:Clone()
    self.center_transform:Translate(Vec3(0.0, 0.0, 0.0))
    self.grid = grid
    for x = 1, self.grid_size_x*2 do
        
        self.grid_scores[x] =  {}
        for y = 1, self.grid_size_y*2 do
            self.grid_scores[x][y] = 0.0
        end
    end

    return self 
end

function NavGrid.Distance(aX, aY, bX, bY)
    return math.sqrt(
        (aX-bX)*(aX-bX) + 
        (aY-bY)*(aY-bY)
    )
end

function NavGrid.Test()
    return ''
end

function NavGrid.NestedRaycast(start_point, end_point, direction, layers)
    local hits = {} -- RayCastHit[]
    local last_point = nil
    for i = 1, layers+1 do
        local p = start_point
        if last_point ~= nil then
            p = last_point + (direction*1.3)
        end
        local ray = RaycastManager:Raycast(p, end_point, RayCastFlags.IsAsyncRaycast)
        
        hits[i] = ray
        if ray ~= nil then
            last_point = ray.position 
        end
    end
    return hits
end

-- end static

-- we will only update if the new transform is outside of a specific radius
function NavGrid:UpdateTransform(NewTransform)
    if (NewTransform.trans:Distance(self.center_transform.trans)) > (self.grid_size_x*self.cell_size) then
        self.center_transform = NavGrid.FloorTransform(
            NavGrid.NormalizeTransform(NewTransform)
        )
        return true
    end
    return false
end

function NavGrid:IsInsideGrid(X,Y)
    if (X >= 1 and X <= self.grid_size_x*2) and (Y >= 1 and Y <= self.grid_size_y*2) then
        return true
    else
        return false
    end
end

function NavGrid:ShouldMoveTo(Current_X, Current_Y, New_X, New_Y, Target_X, Target_Y)
    if not self:IsInsideGrid(New_X, New_Y) then
        return false
    end
    if (self.Distance(New_X, New_Y, Target_X, Target_Y) < self.Distance(Current_X, Current_Y, Target_X, Target_Y)) and self.grid_scores[New_X][New_Y] ~= 1.0
        and self.explored_grid[New_X][New_Y] == false then
        table.insert(self.cached_path, self.box_centers[New_X][New_Y])
        self.explored_grid[New_X][New_Y] = true
        return true
    else
        return false
    end
    
end

function NavGrid:GetDirectionTo(From, To)
    return (To - From):Normalize()
end

function NavGrid:GetPathTo(From, To)
    self.box_centers = {}
    self.explored_grid = {}
    self.cached_path = {From}
    
    -- log
    -- print("From: "..From.x .. " "..From.y.." "..From.z.." To: "..To.x.." "..To.y.." "..To.z )
    
    --local idx = 1
    local start_x = 1
    local start_y = 1
    local target = From + (self:GetDirectionTo(From, To)*self.cell_size)
    local target_x = 1
    local target_y = 1

    -- log 
    -- print("To Nudged: "..target.x .." ".. target.y.." "..target.z)
    
    for x, grid in pairs(self.grid) do
        
        self.explored_grid[x] = {}
        self.box_centers[x] = {}
        for y, box in pairs(self.grid[x]) do
            -- self.grid_scores[x][y] = 0.0
            self.explored_grid[x][y] = false
            local transformed_box = NavGrid.TransformBox(
                box, 
                NavGrid.NormalizeTransform(self.center_transform)
            )
            self.box_centers[x][y] = (transformed_box.max + transformed_box.min) * 0.5
            if IsPointInsideBox(From, transformed_box) then
                start_x = x
                start_y = y
            end
            if IsPointInsideBox(target, transformed_box) then
                target_x = x
                target_y = y
            end
            --idx = idx + 1
        end
    end
    -- print("Start: " .. start_x .. " ".. start_y .. " End: "..target_x.." "..target_y)
    local max_attempts = 24
    local should_continue = true

    local attempts = 0
    while should_continue do

        if self:ShouldMoveTo(start_x, start_y, start_x+1, start_y, target_x, target_y) then
            start_x = start_x + 1
            start_y = start_y
        elseif self:ShouldMoveTo(start_x, start_y, start_x+1, start_y+1, target_x, target_y) then
            start_x = start_x + 1
            start_y = start_y + 1
        elseif self:ShouldMoveTo(start_x, start_y, start_x-1, start_y, target_x, target_y) then
            start_x = start_x - 1
            start_y = start_y
        elseif self:ShouldMoveTo(start_x, start_y, start_x-1, start_y-1, target_x, target_y) then
            start_x = start_x - 1
            start_y = start_y -1
        elseif self:ShouldMoveTo(start_x, start_y, start_x, start_y+1, target_x, target_y) then
            start_x = start_x
            start_y = start_y + 1
        elseif self:ShouldMoveTo(start_x, start_y, start_x-1, start_y+1, target_x, target_y) then
            start_x = start_x - 1
            start_y = start_y + 1
        elseif self:ShouldMoveTo(start_x, start_y, start_x, start_y-1, target_x, target_y) then
            start_x = start_x
            start_y = start_y - 1
        elseif self:ShouldMoveTo(start_x, start_y, start_x+1, start_y-1, target_x, target_y) then
            start_x = start_x + 1
            start_y = start_y - 1
        end



        if start_x == target_x and start_y == target_y then
            should_continue = false
        end


        attempts = attempts + 1
        if attempts == max_attempts then
            should_continue = false
        end
    end
    
end

function NavGrid:UpdateScores()
    -- print("Updating scores... Center Transform : ".. self.center_transform.trans.x.. " "..self.center_transform.trans.y.." "..self.center_transform.trans.z)
    local ToLookFor = "ServerVegetationTreeEntity"
    if SharedUtils:IsClientModule() then
        ToLookFor = "ClientVegetationTreeEntity"
    end
    
    -- transfrm our boxes here
    local transformed_boxes = {}

    for x, grid in pairs(self.grid) do
        transformed_boxes[x] = {}
        for y, box in pairs(self.grid[x]) do
            self.grid_scores[x][y] = 0.0
            transformed_boxes[x][y] = NavGrid.TransformBox(
                box, 
                NavGrid.NormalizeTransform(self.center_transform)
            )
        end
    end
    
        -- print("Get obj" .. obj.typeInfo.name)
    
    for x, grid in pairs(transformed_boxes) do
        for y, box in pairs(transformed_boxes[x]) do  
            local value = 0.0
            for w, world_box in pairs(cachedSpatialWorldBox) do
                -- local world_box = obj--cachedSpatialWorldBox[w]
                
                -- if entity:Is(ToLookFor) then
                -- local s_entity = SpatialEntity(entity)
                -- local box = self.grid[x][y]
        
                
                -- local entity_world_box = NavGrid.TransformBox(s_entity.aabb, s_entity.transform)
                if (AreWeOverlapping(box, world_box)) then 
                    self.grid_scores[x][y] = 1.0
                    value = 1.0
                    break
                else
                    -- self.grid_scores[x][y] = 0.0
                end
                
               
            end
        end
    end
    

    return
    
    -- EntityManager:TraverseAllEntities(function(entity)
    --     -- Do something with entity.
    --     if entity:Is("SpatialEntity") then --and (not entity:Is("ServerWaterEntity")) and (not entity:Is("ServerTerrainEntity")) and (not entity:Is("ServerStaticModelGroupEntity")) then
    --         local s_entity = SpatialEntity(entity)
    --         if s_entity then
    --             for x, grid in pairs(self.grid) do
    --                 for y, box in pairs(self.grid[x]) do
    --              
    --                     local box = self.grid[x][y]
    --                     local value = 0.0
    --                     local transformed_box = 
    --                     NavGrid.TransformBox(
	-- 						NavGrid.ShrinkBox(box, 0.0), 
	-- 						NavGrid.NormalizeTransform(self.center_transform)
	-- 					)
    --                     --AxisAlignedBox(self.center_transform.trans + box.min, self.center_transform.trans + box.max)
    --                     local shouldTestGroup = false
    --                     if entity:Is("ServerStaticModelGroupEntity") and shouldTestGroup then
    --                         local sm_entity = GameEntity(entity)
    --                         local datas = StaticModelGroupEntityData(sm_entity.data).memberDatas
    --                         
    --                         for _, member in pairs(datas) do
    --                             -- print("Iterating members")
    --                             for _, transform in pairs(member.instanceTransforms) do
    --                                 if IsPointInsideBox(transform.trans, transformed_box) then
    --                                     value = 1.0
    --                                     self.grid_scores[x][y] = value
    --                                     -- print("Point inside box: "..transform.trans.x.." : "..transform.trans.y.." : "..transform.trans.z)
    --                                     break
    --                                 end
    --                             end
    --                             if value ~= 0.0 then
    --                                 break
    --                             end
    --                         end
    --                     end
    --                     local entity_world_box = NavGrid.TransformBox(s_entity.aabb, s_entity.transform)
    --                     if (AreWeOverlapping(transformed_box, entity_world_box) and (not entity:Is("ServerWaterEntity")) and (not entity:Is("ServerTerrainEntity")))
    --                         and value == 0.0
    --                         and (not entity:Is("ServerStaticModelGroupEntity")) and (not entity:Is("ServerSoldierEntity"))
    --                         and (not entity:Is("ServerSoldierWeapon")) then
    --                         self.grid_scores[x][y] = 1.0
    --                         local min_ = s_entity.aabb.min + s_entity.transform.trans
    --                         local max_ = s_entity.aabb.max + s_entity.transform.trans
    --                         print("Overlapping ".. entity.typeInfo.name .. " - Entity box min " ..
    --                              min_.x .." ".. min_.y .." ".. min_.z..
    --                              " - Entity box max " ..
    --                              max_.x .." ".. max_.y .." ".. max_.z
    --                         )
    --                     
    --                     end
    --                 end
    --             end
    --         end
    --     end    
    -- end)

    
end

function NavGrid:Update()
    for x, gridx in pairs(self.grid) do
        for y, box in pairs(self.grid[x]) do

        end
    end
end

if not g_NavGrid_Shared then
    g_NavGrid_Shared = NavGrid()
end
return g_NavGrid_Shared