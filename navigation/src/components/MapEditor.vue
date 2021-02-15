<template>
  <div style="height: 100%; width: 100%; position: absolute">
    <div
      class="full-width full-height row wrap justify-start items-start content-start"
      style="flex-grow: 1; height: 100%"
    >
      <div class="col-3 col-md-2 bg-grey-10" style="height: 100%;">
        <q-list separator dark>
          <div>
            <q-btn :loading="isRecalculating" label="Recalculate costs" flat color="warning" text-color="white" style="width:50%" @click="onClickRecalculateCosts"/>
            <q-btn label="Reset Level" flat color="warning" text-color="white" style="width:50%;" @click="onClickResetLevel"/>
          </div>
          <div>
            <q-checkbox dark label="Elevation-Based Mesh" v-model="elevationBasedScoring" @input="onElevationBasedInput" />
          </div>
          <div>
            <q-checkbox dark label="VoxelDF-Based Mesh" v-model="voxelDFBasedMesh" @input="onVoxelDFInput" />
          </div>
          <q-item>
          <q-item-section>
            <q-input dark outlined dense v-model="elevationAlphaPower" hint="Elevation Alpha Power" />
          </q-item-section>
          <q-item-section>
            <q-input dark outlined dense v-model="elevationAlphaBeta" hint="Elevation Alpha Beta" />
          </q-item-section>
          <q-item-section>
            <q-input dark outlined dense v-model="elevationAlphaBetaPower" hint="Elevation Alpha Beta Power" />
          </q-item-section>
          </q-item>
          <q-separator dark style="margin-top: 35px;" />
          <q-item>
          <q-btn-dropdown flat :label="`Level Z: ${levelZ}`" style='width: 100%'>
            <q-list>
              <q-item v-for="levelZElem in levelZIndexes" :key='levelZElem' dense clickable v-close-popup @click='onChangeLevelZIndex(levelZElem)'>
                <q-item-section>
                  <q-item-label>Level {{levelZElem}}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
          </q-item>
          <q-item clickable v-ripple>
            <q-item-section>
              <q-checkbox dark
                v-model="enableEditing"
                @input="onEditingModeChanged"
              />
            </q-item-section>
            <q-item-section>Enable Editing</q-item-section>
          </q-item>
          <div v-if="enableEditing">
            <q-item
              clickable
              v-ripple
              :active="drawing && drawingMode == 0"
              @click="updateDrawingMode(true, 0)"
            >
              <q-item-section avatar>
                <q-icon name="edit_road" />
              </q-item-section>
              <q-item-section> Draw Roads [e*0.25]</q-item-section>
            </q-item>
            <q-item
              clickable
              v-ripple
              :active="drawing && drawingMode == 1"
              @click="updateDrawingMode(true, 1)"
            >
              <q-item-section avatar>
                <q-icon name="house" />
              </q-item-section>
              <q-item-section> Draw Structure [e*2.25] </q-item-section>
            </q-item>
          </div>
        </q-list>
      </div>

      <div class="col-8 col-md-8" style="height: 100%; position: relative">
        <div id="mapContainer">&nbsp;</div>
      </div>
      <div class="col-2 bg-grey-10" style="height: 100%">
        <q-scroll-area style="height: 80vh">
          <div class="text-subtitle1" style="padding-left:5px; color: #989898;" >Roads</div><q-separator dark />
          <q-editor dark v-model="dynamicRoadContentsForCurrentLayer" height="100%"  flat/>
          <div class="text-subtitle1" style="padding-left:5px; color: #989898;" >Structures</div><q-separator dark />
          <q-editor dark v-model="dynamicStructureContentsForCurrentLayer" height="100%"  flat/>
        </q-scroll-area>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import 'leaflet/dist/leaflet.css'
import 'leaflet-draw/dist/leaflet.draw.css'
// import * as L from 'leaflet';

import { defaultLevel, Level, Manager, Player } from 'src/store/models'
import L, { FeatureGroup, LatLng } from 'leaflet'
import 'leaflet-draw'
import { ManagerStore } from 'src/store/ManagerStoreModule'
// import { ManagerStore } from 'src/store/ManagerStoreModule'

declare module 'leaflet' {
  export interface LeafletEvent {
    layerType: string
  }
}

@Component
export default class MapEditor extends Vue {
  level: Level = defaultLevel;

  manager: Manager | undefined;

  mapContent = '// map edits will appear here\n {}';

  mapCostRaster: L.ImageOverlay | undefined;
  showToolset = true;
  enableEditing = false;

  drawing = false;
  drawingMode = 0;
  // DEPRECATED
  drawnItems: L.FeatureGroup | undefined;
  //
  roadItemsLayers : L.FeatureGroup [] = [];
  buildingItemsLayers : L.FeatureGroup [] = [];
  navigableItemsLayers : L.FeatureGroup [] = [];
  unNavigableItemsLayers : L.FeatureGroup [] = [];
  destructableItemsLayers : L.FeatureGroup [] = [];

  roadItemsJSONLayers : L.FeatureGroup[] = [];
  buildingItemsJSONLayers : L.FeatureGroup[] = [];
  navigableItemsJSONLayers : L.FeatureGroup[] = [];
  unNavigableItemsJSONLayers : L.FeatureGroup[] = [];
  destructableItemsJSONLayers : L.FeatureGroup[] = [];
  //
  levelZ = 0;
  levelZIndexes = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9
  ]
  //

  isRecalculating = false
  elevationBasedScoring = false
  elevationAlphaPower = '0.05'
  elevationAlphaBeta = '1.5'
  elevationAlphaBetaPower = '7.0'
  voxelDFBasedMesh = false

  drawingColors = [
    '#ff7017',
    '#1778ff',
    '#00b51b',
    '#b52700'
  ]

  map : L.Map|undefined

  players : Player[] = []
  playerFeatures : FeatureGroup|null = null

  setupMap () {
    const mapContainer = L.map('mapContainer', { crs: L.CRS.Simple }).setView(
      [225, 225],
      1
    )
    this.map = mapContainer
    if (this.manager) {
      this.mapCostRaster = L.imageOverlay(
        this.manager.get_level_base_cost_surface_uri(
          this.level.project_id.toString(),
          this.level.level_id.toString(),
          this.levelZ
        ),
        [
          [0, 0],
          [this.level.transform.height, this.level.transform.width]
        ]
      ).addTo(mapContainer)
      console.log('raster', this.level, this.mapCostRaster.getBounds())
    }

    this.drawnItems = new L.FeatureGroup()
    this.playerFeatures = new L.FeatureGroup()

    mapContainer.addLayer(this.playerFeatures)

    for (let i = 0; i < this.levelZIndexes.length; ++i) {
      this.roadItemsLayers.push(new L.FeatureGroup())
      this.buildingItemsLayers.push(new L.FeatureGroup())
      this.navigableItemsLayers.push(new L.FeatureGroup())
      this.unNavigableItemsLayers.push(new L.FeatureGroup())
      this.destructableItemsLayers.push(new L.FeatureGroup())

      this.roadItemsLayers[this.roadItemsLayers.length - 1].setStyle({ color: this.getFeatureColour(0) })
      this.buildingItemsLayers[this.buildingItemsLayers.length - 1].setStyle({ color: this.getFeatureColour(1) })
      this.navigableItemsLayers[this.navigableItemsLayers.length - 1].setStyle({ color: this.getFeatureColour(2) })
      this.unNavigableItemsLayers[this.unNavigableItemsLayers.length - 1].setStyle({ color: this.getFeatureColour(3) })
      this.destructableItemsLayers[this.destructableItemsLayers.length - 1].setStyle({ color: this.getFeatureColour(4) })

      this.roadItemsJSONLayers.push(new L.FeatureGroup())
      this.buildingItemsJSONLayers.push(new L.FeatureGroup())
      this.navigableItemsJSONLayers.push(new L.FeatureGroup())
      this.unNavigableItemsJSONLayers.push(new L.FeatureGroup())
      this.destructableItemsJSONLayers.push(new L.FeatureGroup())
    }
    mapContainer.addLayer(this.roadItemsLayers[this.levelZ])
    mapContainer.addLayer(this.buildingItemsLayers[this.levelZ])
    mapContainer.addLayer(this.navigableItemsLayers[this.levelZ])
    mapContainer.addLayer(this.unNavigableItemsLayers[this.levelZ])
    mapContainer.addLayer(this.destructableItemsLayers[this.levelZ])
    // mapContainer.addLayer(this.drawnItems)

    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
    var drawControl = new L.Control.Draw({
      edit: {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        featureGroup: this.roadItemsLayers[0],
        remove: false
      }
    })

    mapContainer.addControl(drawControl)
    // console.log('test', this.$leaflet);
    mapContainer.on(L.Draw.Event.CREATED, (e : L.LeafletEvent | L.DrawEvents.Created) => {
      console.log('created', e)
      // manage our transformation
      const layer = (<L.Layer>e.layer)
      // eslint-disable-next-line @typescript-eslint/no-unused-vars, no-unused-vars
      let projectedLayer : L.Layer|undefined

      if (e.layerType === 'polygon' || e.layerType === 'rectangle') {
        const lp = <L.Polygon>layer
        const lpc : L.Polygon = new L.Polygon(lp.getLatLngs(), lp.options)
        const points = lpc.getLatLngs()
        // let projectedPoints : LatLng[] | LatLng[][] | LatLng[][][] = points
        // projectedPoints = []
        // let i = 0
        if (Array.isArray(points[0])) {
          if (Array.isArray(points[0][0])) {
            const pt : LatLng[][][] = <LatLng[][][]>points
            for (let i = 0; i < pt.length; ++i) {
              for (let j = 0; j < pt[i].length; ++j) {
                for (let k = 0; k < pt[i][j].length; ++k) {
                  if (this.manager) {
                    const newPos = this.manager.projectToWorld(
                      pt[i][j][k].lng,
                      pt[i][j][k].lat,
                      this.level
                    )
                    pt[i][j][k] = new LatLng(newPos[0], newPos[1])
                  }
                }
              }
            }
          } else {
            const pt : LatLng[][] = <LatLng[][]>points
            for (let i = 0; i < pt.length; ++i) {
              for (let j = 0; j < pt[i].length; ++j) {
                if (this.manager) {
                  const newPos = this.manager.projectToWorld(
                    pt[i][j].lng,
                    pt[i][j].lat,
                    this.level
                  )
                  pt[i][j] = new LatLng(newPos[0], newPos[1])
                }
              }
            }
          }
        } else {
          const pt : LatLng[] = <LatLng[]>points
          for (let i = 0; i < pt.length; ++i) {
            if (this.manager) {
              const newPos = this.manager.projectToWorld(
                pt[i].lng,
                pt[i].lat,
                this.level
              )
              pt[i] = new LatLng(newPos[0], newPos[1])
            }
          }
          lpc.setLatLngs(pt)
          // e.layer = lp
        }
        projectedLayer = lpc
      } else if (e.layerType === 'circlemarker') {
        const l : L.CircleMarker = <L.CircleMarker>e.layer
        const lc : L.CircleMarker = new L.CircleMarker(l.getLatLng(), l.options)
        lc.setRadius(1000)
        if (this.manager) {
          const newPos = this.manager.projectToWorld(
            lc.getLatLng().lng,
            lc.getLatLng().lat,
            this.level
          )
          lc.setLatLng(new LatLng(newPos[0], newPos[1]))
          projectedLayer = lc
        }
      } else if (e.layerType === 'circle') {
        const l : L.Circle = <L.Circle>e.layer
        const lc : L.Circle = new L.Circle(l.getLatLng(), l.options)
        if (this.manager) {
          const newPos = this.manager.projectToWorld(
            lc.getLatLng().lng,
            lc.getLatLng().lat,
            this.level
          )
          lc.setLatLng(new LatLng(newPos[0], newPos[1]))
          projectedLayer = lc
        }
      }

      const gLayer = this.getFeatureGroup(this.drawingMode)
      const gContextLayer = this.getFeatureGroupJSON(this.drawingMode)
      const gContextLayers = this.getFeatureGroupJSONLayers(this.drawingMode)
      if (gLayer && this.drawing && gContextLayer && projectedLayer) {
        console.log('our json layer: ', gContextLayer)
        const c = gLayer.addLayer(e.layer)
        // const d = gContextLayer.addLayer(projectedLayer)
        gContextLayer.addLayer(projectedLayer)
        c.setStyle(
          {
            color: this.getFeatureColour(this.drawingMode)
          }
        )
        // console.log(c)
        const mapContent = []
        for (let i = 0; i < gContextLayers.length; ++i) {
          mapContent.push(gContextLayers[i].toGeoJSON())
        }
        this.mapContent = JSON.stringify(mapContent) // JSON.stringify(d.toGeoJSON())
        this.onChangeLevelZIndex(this.levelZ + 1)
        this.onChangeLevelZIndex(this.levelZ - 1)
        if (this.manager) {
          this.manager.updateLevelFeature(ManagerStore.currentProject.project_id, this.level.level_id, 'road', this.dynamicRoadContent()).then(
            result => {
              console.log(result)
            }
          ).catch(err => {
            console.error(err)
          })
          this.manager.updateLevelFeature(ManagerStore.currentProject.project_id, this.level.level_id, 'structure', this.dynamicStructureContent()).then(
            result => {
              console.log(result)
            }
          ).catch(err => {
            console.error(err)
          })
        }

        // console.log(c.toGeoJSON())
      }
    })

    console.log('drawControl', drawControl)
  }

  updateMap () {
    // console.log(this.drawnItems)
    if (this.mapCostRaster && this.manager && this.map) {
      console.log('update map')
      if (this.playerFeatures) {
        this.playerFeatures.clearLayers()
        // this.manager.getPlayers().then(result => {
        //   this.players = result
        // }).catch(err => {
        //   console.error(err)
        // })
        this.players.forEach(player => {
          if (this.manager && this.playerFeatures) {
            const gridPos = this.manager.projectToGrid(player.transform.trans, this.level)
            const point = new L.CircleMarker(new L.LatLng(this.level.transform.height - gridPos[1], gridPos[0]), { radius: 5.0 })
            if (player.is_human) {
              point.setStyle({ color: '#dea300' })
            } else if (player.team === 1) {
              point.setStyle({ color: '#b8411d' })
            }
            this.playerFeatures.addLayer(point)
          }
        })
      }
      // this.mapCostRaster.setUrl('https://openthread.google.cn/images/ot-contrib-google.png')
      setTimeout(() => {
        if ((this.mapCostRaster && this.manager && this.map)) {
          this.mapCostRaster.setUrl(
            this.manager.get_level_base_cost_surface_uri(
              this.level.project_id.toString(),
              this.level.level_id.toString(),
              this.levelZ
            )
          )
        }
      }, 2000)
    }
  }

  get dynamicRoadContentsForCurrentLayer () {
    const gContextLayer = this.getFeatureGroupJSON(0)
    const mapContent = []
    if (gContextLayer) {
      mapContent.push(gContextLayer.toGeoJSON())
      return JSON.stringify(mapContent[0])
    }
    return ''
  }

  get dynamicStructureContentsForCurrentLayer () {
    const gContextLayer = this.getFeatureGroupJSON(1)
    const mapContent = []
    if (gContextLayer) {
      mapContent.push(gContextLayer.toGeoJSON())
      return JSON.stringify(mapContent[0])
    }
    return ''
  }

  dynamicRoadContent () {
    const gContextLayers = this.getFeatureGroupJSONLayers(0)
    if (gContextLayers[0]) {
      const l : L.FeatureGroup = gContextLayers[0]
      const mapContext : ReturnType<typeof l.toGeoJSON>[] = []
      gContextLayers.forEach(l => {
        if (l) {
          mapContext.push(l.toGeoJSON())
        }
      })
      console.log('dynamic road contents: ', mapContext)
      return JSON.stringify(mapContext)
    }
    return ''
  }

  dynamicStructureContent () {
    const gContextLayers = this.getFeatureGroupJSONLayers(1)
    if (gContextLayers[0]) {
      const l : L.FeatureGroup = gContextLayers[0]
      const mapContext : ReturnType<typeof l.toGeoJSON>[] = []
      gContextLayers.forEach(l => {
        if (l) {
          mapContext.push(l.toGeoJSON())
        }
      })
      return JSON.stringify(mapContext)
    }
    return ''
  }

  updateDrawingMode (drawing: boolean, drawMode: number) {
    this.drawing = drawing
    this.drawingMode = drawMode
  }

  onEditingModeChanged (newState: boolean) {
    if (!newState) {
      this.drawing = false
    }
  }

  getFeatureColour (key : number) : string {
    if ((!(key in this.drawingColors)) || !this.drawing) {
      return '#00aeff'
    } else {
      return String(this.drawingColors[key])
    }
  }

  forceGetFeatureColour (key : number) : string {
    if ((!(key in this.drawingColors))) {
      return '#00aeff'
    } else {
      return String(this.drawingColors[key])
    }
  }

  getFeatureGroup (key : number) : L.FeatureGroup|undefined {
    switch (key) {
      case (0):
        return this.roadItemsLayers[this.levelZ]
      case (1):
        console.log('building')
        return this.buildingItemsLayers[this.levelZ]
      case (2):
        return this.navigableItemsLayers[this.levelZ]
      case (3):
        return this.unNavigableItemsLayers[this.levelZ]
      case (4):
        return this.destructableItemsLayers[this.levelZ]
    }
  }

  getFeatureGroupJSON (key : number) : L.FeatureGroup|undefined {
    switch (key) {
      case (0):
        return this.roadItemsJSONLayers[this.levelZ]
      case (1):
        console.log('building')
        return this.buildingItemsJSONLayers[this.levelZ]
      case (2):
        return this.navigableItemsJSONLayers[this.levelZ]
      case (3):
        return this.unNavigableItemsJSONLayers[this.levelZ]
      case (4):
        return this.destructableItemsJSONLayers[this.levelZ]
    }
  }

  getFeatureGroupJSONLayers (key : number) : L.FeatureGroup[] {
    switch (key) {
      case (0):
        return this.roadItemsJSONLayers
      case (1):
        console.log('building')
        return this.buildingItemsJSONLayers
      case (2):
        return this.navigableItemsJSONLayers
      case (3):
        return this.unNavigableItemsJSONLayers
      case (4):
        return this.destructableItemsJSONLayers
    }
    return []
  }

  onChangeLevelZIndex (layer : number) {
    if (this.map) {
      this.map.removeLayer(this.roadItemsLayers[this.levelZ])
      this.map.removeLayer(this.buildingItemsLayers[this.levelZ])
      this.map.removeLayer(this.navigableItemsLayers[this.levelZ])
      this.map.removeLayer(this.unNavigableItemsLayers[this.levelZ])
      this.map.removeLayer(this.destructableItemsLayers[this.levelZ])

      this.levelZ = layer
      this.map.addLayer(this.roadItemsLayers[this.levelZ])
      this.map.addLayer(this.buildingItemsLayers[this.levelZ])
      this.map.addLayer(this.navigableItemsLayers[this.levelZ])
      this.map.addLayer(this.unNavigableItemsLayers[this.levelZ])
      this.map.addLayer(this.destructableItemsLayers[this.levelZ])
    }
  }

  iHandler : ReturnType<typeof setInterval>|undefined;

  mounted () {
    this.manager = new Manager(this)
    this.$root.$on('setupMap', (inLevel : Level) => {
      this.level = inLevel
      this.setupMap()
      if (this.manager) {
        const roadLayers = this.manager.projectFeatureCollectionToGrid(this.level.roads, this.level)
        for (let i = 0; i < roadLayers.length; ++i) {
          roadLayers[i].forEach(layer => {
            if (this.roadItemsLayers[i]) {
              // this.roadItemsLayers[i].setStyle({ color: this.getFeatureColour(0) })
              const c = this.roadItemsLayers[i].addLayer(layer)
              c.setStyle({ color: this.forceGetFeatureColour(0) })
              console.log('add Layer: ', i, layer, this.roadItemsLayers[i])
            }
          })
        }
        const roadLayersJSON = this.manager.importFeatureCollectionJSON(this.level.roads, this.level)
        for (let i = 0; i < roadLayersJSON.length; ++i) {
          roadLayersJSON[i].forEach(layer => {
            if (this.roadItemsJSONLayers[i]) {
              this.roadItemsJSONLayers[i].addLayer(layer)
            }
          })
        }
        const structureLayers = this.manager.projectFeatureCollectionToGrid(this.level.structures, this.level)
        for (let i = 0; i < structureLayers.length; ++i) {
          structureLayers[i].forEach(layer => {
            const c = this.buildingItemsLayers[i].addLayer(layer)
            c.setStyle({ color: this.forceGetFeatureColour(1) })
            // this.buildingItemsLayers[i].setStyle({ color: this.getFeatureColour(1) })
            console.log('adding building layer', layer, i)
          })
        }
        const structureLayersJSON = this.manager.importFeatureCollectionJSON(this.level.structures, this.level)
        for (let i = 0; i < structureLayersJSON.length; ++i) {
          structureLayersJSON[i].forEach(layer => {
            this.buildingItemsJSONLayers[i].addLayer(layer)
            // this.buildingItemsJSONLayers[i].setStyle({ color: this.getFeatureColour(1) })
          })
        }

        this.manager.getPlayers().then(result => {
          this.players = result
        }).catch(err => {
          console.error(err)
        })
      }
    })
    // this.setupMap()
    // console.log('Setup map')

    this.iHandler = setInterval(() => {
      this.updateMap()
    }, 2000)
  }

  beforeDestroy () {
    console.log('unmounting...')
    if (this.iHandler) {
      clearInterval(this.iHandler)
      console.log('clear interval')
    }
    this.$root.$off('setupMap')
  }

  onClickResetLevel () {
    if (this.manager) {
      this.manager.resetLevel(ManagerStore.currentProject.project_id, this.level.level_id).catch(err => console.error(err))
    }
  }

  onClickRecalculateCosts () {
    if (this.manager) {
      this.isRecalculating = true
      this.manager.recalculateCosts(this.level.project_id, this.level.level_id, this.elevationBasedScoring, this.voxelDFBasedMesh, parseFloat(this.elevationAlphaPower), parseFloat(this.elevationAlphaBeta), parseFloat(this.elevationAlphaBetaPower)).then(() => {
        this.isRecalculating = false
      }).catch(err => { console.error(err); this.isRecalculating = false })
    }
  }

  onElevationBasedInput (val : boolean) {
    if (val) {
      this.voxelDFBasedMesh = false
    }
  }

  onVoxelDFInput (val : boolean) {
    if (val) {
      this.elevationBasedScoring = false
    }
  }
}

</script>
