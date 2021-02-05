<template>
    <q-page>
        <q-drawer dark side="right" v-model="right" class="bg-grey-10">
            <q-list dark class="bg-grey-10">
                <q-item dark>
                    <q-item-section class='text-subtitle1'>
                        Add Level
                    </q-item-section>
                </q-item>
                <!-- <q-separator /> -->

                    <q-form dark class="q-gutter-md">
                        <q-item style="margin-bottom: -40px">
                            <p>Level Configuration</p>
                        </q-item>
                        <q-item style="margin-bottom: -20px;">
                            <q-input dark filled v-model="config.level_name" :disable="true" label="Level Name" hint="FB Loaded Level" />
                        </q-item>
                        <q-item style="margin-bottom: -40px">
                            <p>Grid Bounds </p>
                        </q-item>

                        <q-item style="margin-bottom: -20px">
                            <q-item-section>
                                <q-input filled dark v-model="config.start.x" label="X" hint="Start X"/>
                            </q-item-section>
                            <q-item-section>
                                <q-input filled dark v-model="config.start.y" label="Y" hint="Start Y"/>
                            </q-item-section>
                            <q-item-section>
                                <q-input filled dark v-model="config.start.z" label="Z" hint="Start Z"/>
                            </q-item-section>
                        </q-item>

                        <q-item style="margin-bottom: -15px">
                            <q-item-section>
                                <q-input filled dark v-model="config.end.x" label="X" hint="End X"/>
                            </q-item-section>
                            <q-item-section>
                                <q-input filled dark v-model="config.end.y" label="Y" hint="End Y"/>
                            </q-item-section>
                            <q-item-section>
                                <q-input filled dark v-model="config.end.z" label="Z" hint="End Z"/>
                            </q-item-section>
                        </q-item>
                        <q-item style="margin-bottom: -15px">
                            <q-item-section>
                                <q-btn @click="syncStart" color="warning" text-color="dark" label="Start from Player"/>
                            </q-item-section>
                            <q-item-section>
                                <q-btn @click="syncEnd" color="warning" text-color="dark" label="End from Player"/>
                            </q-item-section>
                        </q-item>
                        <q-item style="margin-bottom: -40px">
                            <p>Build Configuration</p>
                        </q-item>
                        <q-item>
                            <q-item-section>
                                <q-input filled dark v-model="config.voxel_step_size" label="Step Size" hint="Having larger values would result in less iterations, but may crash the game." />
                            </q-item-section>
                            <q-item-section>
                                <q-input filled dark v-model="config.voxel_size" label="Voxel Size" hint="Smaller values here would result in longer build times." />
                            </q-item-section>
                        </q-item>
                        <q-item style="margin-top:50px;">
                            <q-btn @click="calculateSettings" color="warning" text-color="dark" label="Calculate Settings"/>
                        </q-item>
                        <q-item style="background-color: #131313; color: #545454; font-size:12px;">
                            <span>Iterations[GridSizeX] X: {{config.iterations_x}} <br> Iterations[GridSizeY] Y: {{config.iterations_y}}</span>
                        </q-item>
                        <q-item>
                            <q-btn @click="startBuild" :disable="isBuilding" color="warning" text-color="dark" label="Add Level and Generate Navmesh"/>
                        </q-item>
                    </q-form>
                    <q-item class="absolute-bottom bg-grey-10" v-if="initializedGameSyncManager">
                        <q-linear-progress dark stripe rounded size="20px" :value="buildProgress" color="red" class="q-mt-sm" />
                    </q-item>
            </q-list>
        </q-drawer>
    </q-page>
</template>

<script lang="ts">
import { LevelBuildSettings, LevelBuildSyncPayload, Vector } from 'src/store/models'
import { Vue, Component } from 'vue-property-decorator'
import { Manager } from '../../../store/models'
import '../../../boot/windowGlobal'
import { ManagerStore } from 'src/store/ManagerStoreModule'

@Component({
  components: {}
})
export default class AddLevel extends Vue {
    right = true
    start: Vector = { x: 0, y: 0, z: 0 }
    end: Vector = { x: 1, y: 1, z: 1 }
    voxelStepSize = 32.0
    voxelSize = 1.0
    initializedGameSyncManager = false
    isBuilding = false

    config : LevelBuildSettings = {
      level_name: '',
      start: this.start,
      end: this.end,
      iterations_x: 0,
      iterations_y: 0,
      voxel_step_size: 32.0,
      voxel_size: 1.0
    }

    get buildProgress () {
      if (ManagerStore) {
        return ManagerStore.levelBuildProgress
      }
      return 0.0
    }

    syncStart () {
      console.log(window.GameSyncManager.currentPosition)
      this.config.start = window.GameSyncManager.currentPosition
    }

    syncEnd () {
      this.config.end = window.GameSyncManager.currentPosition
    }

    calculateSettings () {
      this.config = window.GameSyncManager.calculateBuildSettings(
        this.config
      )
    }

    startBuild () {
      this.isBuilding = true
      this.calculateSettings() // ensure we run this
      const payload: LevelBuildSyncPayload = {
        build_settings: this.config,
        profile: ManagerStore.profile,
        project_id: ManagerStore.currentProject.project_id
      }
      window.GameSyncManager.dispatchVext('StartBuild', [JSON.stringify(payload)])
    }

    gameSyncManager : Manager|undefined;

    mounted () {
      window.GameSyncManager = new Manager(this)
      this.gameSyncManager = window.GameSyncManager
      this.config.level_name = window.GameSyncManager.currentFBLevelName
      this.initializedGameSyncManager = true
      this.calculateSettings()
    }
}
</script>
