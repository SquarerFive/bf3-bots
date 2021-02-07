class 'ScorecardShared'


function ScorecardShared:__init()
	print("Initializing ScorecardShared")
	
end



g_ScorecardShared = ScorecardShared()



-- some fixes

Events:Subscribe('Partition:Loaded', function(partition)
	for _, instance in pairs(partition.instances) do
        if instance:Is('GameModeSettings') then
            local settings = GameModeSettings(instance)
            settings:MakeWritable()

            for _, information in pairs(settings.information) do
                for _, size in pairs(information.sizes) do
                    for _, team in pairs(size.teams) do
                        if team.playerCount > 0 then
                            team.playerCount = 127
                            print('patched')
                        end
                    end
                end
            end
        end
    end
end)