<template>
  <q-page style="background-color: white;">
      <map-editor ref="map"></map-editor>
  </q-page>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import MapEditor from 'components/MapEditor.vue'
import { defaultLevel, Level, Manager } from 'src/store/models'

@Component({ components: { MapEditor } })
export default class Map extends Vue {
  currentLevel : Level = defaultLevel
  manager : Manager|undefined

  mounted () {
    const projectId = this.$route.params.id
    const levelId = this.$route.params.level_id
    this.manager = new Manager(this)
    this.manager.get_level(projectId, levelId).then(
      result => {
        this.currentLevel = result
        console.log('got level', this.currentLevel)
        // const g : MapEditor = (<MapEditor> this.$refs.map)
        this.$root.$emit('setupMap', this.currentLevel)
      }
    ).catch(e => {
      console.error('failed to get level', e)
    })
  }
}
</script>
