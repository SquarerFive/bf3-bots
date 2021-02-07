<template>
  <q-page class="row items-center justify-evenly">
    <q-card :class="activeBotConfigClass" style="left:25px; position:absolute; max-width:500px;">
      <q-card-section>
        <div class="text-h6">Bot Configuration <span class="key transparent" style="float: right">F2</span></div>
        <div class="text-subtitle2"></div>
      </q-card-section>

      <q-separator />

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="one">
          <!--
          <div class="text-h6">Hotkeys</div>
          <div class="text-h7" style="padding:10px;margin-bottom:10px;">
            <span :class="recordingClass" style="padding:5px;margin-right:5px;">F2</span>Record
            <span :class="navigableClass" style="padding:5px;margin-right:2px;">F3</span> Mark as Navigable
            <span :class="unnavigableClass" style="padding:5px;margin-right:2px;">F4</span> Mark as Unnavigable
          </div>
          <q-separator  />
          -->
          <q-badge color="secondary">
            Accuracy: {{ firingAccuracy }}
          </q-badge>
          <q-slider v-model="firingAccuracy" :min="0.0001" :max="1" :step="0.001" @change="updateFiringAccuracy"/>

          <div class="row inline" style="width: 100%">
            <div style="margin-top:10px;margin-bottom:10px; padding:2px; margin-right: 1vh;" class="col">
              <q-badge color="secondary">
                Aim Offset X: {{ firingOffsetX.toFixed(4) }}
              </q-badge>
              <q-slider v-model="firingOffsetX" :min="0.0001" :max="2" :step="0.001" />
            </div>
            <div style="margin-top:10px;margin-bottom:10px; padding:2px;  margin-right: 1vh;" class="col">
              <q-badge color="secondary">
                Aim Offset Y: {{ firingOffsetY.toFixed(4) }}
              </q-badge>
              <q-slider v-model="firingOffsetY" :min="0.0001" :max="2" :step="0.001" />
            </div>
            <div style="margin-top:10px;margin-bottom:10px; padding:2px;" class="col">
              <q-badge color="secondary">
                Aim Offset Z: {{ firingOffsetZ.toFixed(4) }}
              </q-badge>
              <q-slider v-model="firingOffsetZ" :min="0.0001" :max="2" :step="0.001" />
            </div>
          </div>
          <div class="row inline" style="width: 100%">
            <div style="margin-top:10px;margin-bottom:10px; padding:2px; margin-right: 1vh;" class="col">
              <q-badge color="secondary">
                Aim Base Offset X: {{ firingBaseOffsetX.toFixed(4) }}
              </q-badge>
              <q-slider v-model="firingBaseOffsetX" :min="-2" :max="2" :step="0.001" />
            </div>
            <div style="margin-top:10px;margin-bottom:10px; padding:2px;  margin-right: 1vh;" class="col">
              <q-badge color="secondary">
                Aim Base Offset Y: {{ firingBaseOffsetY.toFixed(4) }}
              </q-badge>
              <q-slider v-model="firingBaseOffsetY" :min="-2" :max="2" :step="0.001" />
            </div>
            <div style="margin-top:10px;margin-bottom:10px; padding:2px;" class="col">
              <q-badge color="secondary">
                Aim Base Offset Z: {{ firingBaseOffsetZ.toFixed(4) }}
              </q-badge>
              <q-slider v-model="firingBaseOffsetZ" :min="-2" :max="2" :step="0.001" />
            </div>
          </div>
          <div class="row">
          <q-checkbox label="Aim when Firing" v-model="aimWhenFiring" />
          </div>
          <div class="row">
            <q-space />
            <q-btn color="warning" text-color="dark" label="Apply Settings" @click="applyBotAimSettings"/>
            <q-btn color="warning" text-color="dark" label="Close" style="margin-left: 1vh;" @click="closeBotSettings"/>
          </div>
        </q-tab-panel>

        <q-tab-panel name="two">
          In Development
        </q-tab-panel>
      </q-tab-panels>
    </q-card>
    <!--
    <map-editor></map-editor>
    -->
  </q-page>
</template>

<script lang="ts">
import { Todo, Meta } from 'components/models'
import ExampleComponent from 'components/ClassComponent.vue'
import { Component } from 'vue-property-decorator'
import MapEditor from 'components/MapEditor.vue'
import { Manager } from '../store/models'
import Vue from 'vue'
import { ManagerStore } from 'src/store/ManagerStoreModule'

@Component({
  components: { ExampleComponent, MapEditor }
})
export default class PageIndex extends Vue {
  todos: Todo[] = [
    {
      id: 1,
      content: 'ct1'
    },
    {
      id: 2,
      content: 'ct2'
    },
    {
      id: 3,
      content: 'ct3'
    },
    {
      id: 4,
      content: 'ct4'
    },
    {
      id: 5,
      content: 'ct5'
    }
  ];

  meta: Meta = {
    totalCount: 1200
  };

  tab = 'one';

  showNavtools = true;

  activeNavToolClass = 'navtools-card-xtoggled';

  // recording
  isRecording = false;
  recordingClass = 'key'
  // nav
  recordMode = 0; // 0 = mark as navigable ; 1 = mark as unnavigable
  navigableClass = 'key';
  unnavigableClass = 'key';
  // update
  // eslint:disable-next-line
  updateInterval : ReturnType<typeof setInterval> | null = null;
  firingOffsetX = 0.0001
  firingOffsetY = 0.02
  firingOffsetZ = 0.001

  firingBaseOffsetX = 0.001
  firingBaseOffsetY = 0.02
  firingBaseOffsetZ = 0.01
  aimWhenFiring = false
  firingAccuracy = 0.1

  updateFiringAccuracy (newValue : number) {
    const alpha = 1.0 - newValue
    this.firingOffsetX = 1.4 * alpha
    this.firingOffsetY = 1.0 * alpha
    this.firingOffsetZ = 1.6 * alpha
  }

  applyBotAimSettings () {
    const data = JSON.stringify({
      firingOffsetX: this.firingOffsetX,
      firingOffsetY: this.firingOffsetY,
      firingOffsetZ: this.firingOffsetZ,
      firingBaseOffsetX: this.firingBaseOffsetX,
      firingBaseOffsetY: this.firingBaseOffsetY,
      firingBaseOffsetZ: this.firingBaseOffsetZ,
      aimWhenFiring: this.aimWhenFiring
    })
    window.GameSyncManager.dispatchVext('OnUpdateBotSettings', [data])
  }

  closeBotSettings () {
    ManagerStore.setShouldShowBotSettings(false)
  }

  setShowNavtools (state: boolean) {
    this.showNavtools = state
    this.activeNavToolClass = this.showNavtools ? 'navtools-card' : 'navtools-card-xtoggled'
    console.log(this.activeNavToolClass)
  }

  setSampleRadius () {
    console.log('SetSampleRadius')
    // this.$vext.DispatchEventLocal('OnSetSampleRadius', this.sample_radius);
    /* eslint:disable-next-line */
    // eslint-disable-next-line no-eval
    // eval('WebUI.Call(\'DispatchEvent\', \'OnSetSampleRadius\',' + String((this.sampleRadius).toString()) + ');')
  }

  setRecording (state: boolean) {
    this.isRecording = state
    this.recordingClass = state ? 'key toggled-red' : 'key'
    if ((this.updateInterval == null) && this.isRecording) {
      this.updateInterval = setInterval(() => {
        const embedElement : HTMLEmbedElement | null = <HTMLEmbedElement>document.getElementById('cost-map')
        if (embedElement != null) {
          console.log('Valid embed')
          console.log(embedElement.src)
          // eslint:disable-next-line
          // embed_element.src =  'http://www.google.com/';
          // eslint:disable-next-line
          embedElement.src = 'http://localhost:8000/pathfinding/render/?' + (new Date().getTime()).toString()
          embedElement.src = embedElement.src + ''
        }
      }, 5000)
    }
    if ((!this.isRecording) && this.updateInterval) {
      clearInterval(this.updateInterval)
      this.updateInterval = null
    }
  }

  setMode (newMode: number) {
    this.recordMode = newMode
    this.navigableClass = this.recordMode === 0 ? 'key toggled-green' : 'key'
    this.unnavigableClass = this.recordMode === 1 ? 'key toggled-green' : 'key'
  }

  setToolbarMessage (newMessage : string) {
    this.$store.commit('player/updatePlayerPosition', newMessage)
  }

  get shouldShowBotSettings () {
    if (window.GameSyncManager) {
      console.log('window')
      return window.GameSyncManager.shouldShowGameSettings
    }
    return false
  }

  get activeBotConfigClass () {
    return ManagerStore.shouldShowBotSettings ? 'navtools-card' : 'navtools-card-xtoggled'
  }

  mounted () {
    console.log('Hello')
    this.setRecording(false)
    this.setMode(0)
    this.setShowNavtools(false)

    this.$root.$on('setMode', (newMode : number) => {
      this.recordMode = newMode
      this.navigableClass = this.recordMode === 0 ? 'key toggled-green' : 'key'
      this.unnavigableClass = this.recordMode === 1 ? 'key toggled-green' : 'key'
    })

    this.$root.$on('setRecording', (state : boolean) => {
      this.isRecording = state
      this.recordingClass = state ? 'key toggled-red' : 'key'
    })

    this.$root.$on('setShowNavtools', (state : boolean) => {
      this.showNavtools = state
      this.activeNavToolClass = this.showNavtools ? 'navtools-card' : 'navtools-card-xtoggled'
    })

    window.GameSyncManager = new Manager(this)
  }
}
</script>
