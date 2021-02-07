class 'ScorecardServerSettings'

Events:Subscribe('Partition:Loaded', function(partition)
	for _, instance in pairs(partition.instances) do
        if instance:Is("SyncedBFSettings") then
            print("doing SyncedBFSettings")
            local syncedBFSettings = SyncedBFSettings(instance)
            syncedBFSettings:MakeWritable()
            syncedBFSettings.unlicensedUnlocksUnlocked = true
            syncedBFSettings.allUnlocksUnlocked = true
        end
        if instance:Is("SyncedGameSettings") then
            print("doing SyncedGameSettings")
            local syncedGameSettings = SyncedGameSettings(instance)
            syncedGameSettings:MakeWritable()
            syncedGameSettings.enableFriendlyFire = true
            syncedGameSettings.allowClientSideDamageArbitration = false
        end
		if instance:Is('ServerSettings') then
			local serverSettings = ServerSettings(instance)
			serverSettings:MakeWritable()
			print("serverSettings ".. tostring(serverSettings))
			
			print("AI enabled by default? ".. tostring(serverSettings.isAiEnabled))
			print("Collision enabled by default? ".. tostring(serverSettings.isSoldierDetailedCollisionEnabled))
			print("InternetSimulation enabled by default? ".. tostring(serverSettings.isInternetSimulationEnabled))
			print("Reconfigurable enabled by default? ".. tostring(serverSettings.isReconfigurable))
			print("queryProviderEnabled enabled by default? ".. tostring(serverSettings.queryProviderEnabled))
			print("isRenderDamageEvents enabled by default? ".. tostring(serverSettings.isRenderDamageEvents))
			print("isPresenceEnabled enabled by default? ".. tostring(serverSettings.isPresenceEnabled))
			serverSettings.isAiEnabled = true
			serverSettings.isReconfigurable = true
			serverSettings.isSoldierDetailedCollisionEnabled = true
			serverSettings.isInternetSimulationEnabled = true
			serverSettings.isNetworkStatsEnabled = true
			serverSettings.vegetationEnabled = false
            serverSettings.isPresenceEnabled = true
            serverSettings.queryProviderEnabled = true
            serverSettings.isRenderDamageEvents = true
            serverSettings.isStatsEnabled = true
            serverSettings.havokVisualDebugger = true
            serverSettings.scoringLogEnabled = true
            serverSettings.isRanked = true
            serverSettings.unlockResolver = true
			serverSettings.serverName = "Yeet"
            print("AI enabled? ".. tostring(serverSettings.isAiEnabled))
			print("Collision enabled? ".. tostring(serverSettings.isSoldierDetailedCollisionEnabled))
			print("InternetSimulation enabled? ".. tostring(serverSettings.isInternetSimulationEnabled))
			print("Reconfigurable enabled? ".. tostring(serverSettings.isReconfigurable))
			print("enabled AI")
        end
    end
end)