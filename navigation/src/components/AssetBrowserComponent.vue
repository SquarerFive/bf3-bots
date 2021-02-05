<template>
  <div>
    <div class="row">
      <q-card flat class="col">
        <div class="q-pa-sm">
          <div class="text-subtitle1">Assets</div>
        </div>
        <q-separator />
        <q-scroll-area style="height: 300px">
          <q-list>
            <div v-for="asset in filteredAssets" :key="asset.id">
              <!--
              <q-item>
                <q-item-section>
                  <q-item-label>{{ asset.name }}</q-item-label>
                    <q-item-label caption>
                      {{ asset.path }}
                    </q-item-label>
                </q-item-section>
                <q-item-section avatar>
                  <q-btn icon="add" color="positive" @click="selectedAssets.push(asset); outSelectedAssets.push(asset)">
                  </q-btn>
                </q-item-section>
              </q-item>
              -->
              <asset-component :add="true" :asset="asset" :outSelectedAssets="outSelectedAssets" />
            </div>
          </q-list>
        </q-scroll-area>
      </q-card>
      <q-card flat class="col">
        <div class="q-pa-sm">
          <div class="text-subtitle1">Selected</div>
        </div>
        <q-separator />
        <q-scroll-area style="height: 300px">
          <q-list>
            <!--
            <q-item v-for="asset in outSelectedAssets" :key="asset.id">
              <q-item-section>
                <q-item-label>{{ asset.name }}</q-item-label>
                  <q-item-label caption>
                    {{ asset.path }}
                  </q-item-label>
              </q-item-section>
              <q-item-section avatar>
                <q-btn icon="remove" color="negative" @click="selectedAssets.splice(selectedAssets.indexOf(asset), 1); outSelectedAssets.splice(outSelectedAssets.indexOf(asset), 1)">
                </q-btn>
              </q-item-section>
            </q-item>
            -->
            <asset-component :add="false" :asset="asset" :outSelectedAssets="outSelectedAssets" v-for="asset in outSelectedAssets" :key="asset.id" />
          </q-list>
        </q-scroll-area>
      </q-card>
    </div>
  </div>
</template>

<script lang="ts">
import { GameAsset, Manager } from 'src/store/models'
import { Vue, Component, Prop } from 'vue-property-decorator'
import AssetComponent from 'components/AssetComponent.vue'

@Component({ components: { AssetComponent } })
export default class AssetBrowserComponent extends Vue {
    assets : GameAsset[] = []
    selectedAssets : GameAsset[] = []
    manager : Manager|undefined = undefined
    // outSelectedAssets: GameAsset[] = []
    @Prop({ required: false, type: String, default: 'ALL' }) teamFilter!: string
    @Prop({ required: false, type: String, default: '' }) assetSearchFilter!: string
    // @Prop({ required: true, type: Array, default: [] })
    outSelectedAssets: GameAsset[] = []

    get filteredAssets () {
      console.log('update')
      return this.assets.filter(a => { return a.name.includes(this.assetSearchFilter) })
    }

    mounted () {
      this.manager = new Manager(this)
      this.manager.getGameAssets().then(result => {
        console.log(result.data)
        this.assets = <GameAsset[]>result.data
      }).catch(err => {
        console.error(err)
      })
    }
}
</script>
