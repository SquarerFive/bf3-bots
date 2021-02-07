class 'ScorecardClientBase'
local NavGrid = require('__shared/NavGrid')
local ScorecardClient = require("ScorecardClient")


local scorecard_grid = nil

function ScorecardClientBase:__init()
	self:RegisterVars()
	self:RegisterEvents()
end


function ScorecardClientBase:RegisterVars()
	self.castDistance = 200

	self.scorecard_step = 0
	self.scorecard_step_size_x = 0
	self.scorecard_step_size_y = 0

	self.scorecard_min_point = nil
	self.scorecard_max_point = nil
	
end


function ScorecardClientBase:RegisterEvents()
	Events:Subscribe("UI:DrawHud", self, self.OnDrawHud)
	Events:Subscribe('UpdateManager:Update', self, self.OnUpdatePass)
	
end




function ScorecardClientBase:OnDrawHud(a,b,c)
	local s_Player = PlayerManager:GetLocalPlayer()
	if s_Player == nil then
		return
	end

	local s_Soldier = s_Player.soldier
	if s_Soldier == nil then
		return
	end
	

end

function ScorecardClientBase:OnUpdatePass(deltaTime, pass)
    if(pass ~= UpdatePass.UpdatePass_PreSim) then
        return
    end
	local local_player = PlayerManager:GetLocalPlayer()
	if(local_player == nil) then
		return
	else
		-- print("Valid player")
		if (local_player.soldier) then
			ScorecardClient:Tick(deltaTime, pass, local_player)
		end
	end
	if(local_player.soldier == nil) then
		
		return
	end

end


g_ScorecardClientBase = ScorecardClientBase()

-- Hooks:Install('BulletEntity:Collision', 1, function(hook, entity, hit, giverInfo)
-- 	print(entity)
-- 	if (hit.rigidBody) then
-- 		print(hit.rigidBody)
-- 	end
-- end)