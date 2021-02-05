<template>
  <q-page class="row items-center justify-evenly">
    <q-card :class="activeNavToolClass" style="left:25px; position:absolute; max-width:500px;">
      <q-card-section>
        <div class="text-h6">Navigation Tools <span class="key transparent" style="float: right">F1</span></div>
        <div class="text-subtitle2"></div>
      </q-card-section>

      <q-tabs v-model="tab" class="">
        <q-tab label="Modify" name="one" />
        <q-tab label="Create" name="two" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="one">
          <div class="text-h6">Hotkeys</div>
          <div class="text-h7" style="padding:10px;margin-bottom:10px;">
            <span :class="recordingClass" style="padding:5px;margin-right:5px;">F2</span>Record
            <span :class="navigableClass" style="padding:5px;margin-right:2px;">F3</span> Mark as Navigable
            <span :class="unnavigableClass" style="padding:5px;margin-right:2px;">F4</span> Mark as Unnavigable
          </div>
          <q-separator  />
          <div style="margin-top:10px;margin-bottom:10px;">
            <q-badge color="secondary">
              Sample Radius: {{ sampleRadius }}px
            </q-badge>
            <q-slider v-model="sampleRadius" :min="1" :max="16" @click="setSampleRadius()" @change="setSampleRadius"/>
          </div>
          <q-separator  />
          <div class="text-h6" style="margin-top:5px;">Nav Surface</div>
          <embed id="cost-map" style="padding:2px;border-radius:10px;" src="http://localhost:8000/pathfinding/render/" type="image/png" width="450" height='450'>

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
  sampleRadius = 1.0;

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
    eval('WebUI.Call(\'DispatchEvent\', \'OnSetSampleRadius\',' + String((this.sampleRadius).toString()) + ');')
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
