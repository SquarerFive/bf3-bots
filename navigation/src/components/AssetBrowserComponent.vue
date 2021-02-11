<template>
  <div>
    <div class="row">
      <q-card flat class="col">
        <div class="q-pa-sm">
          <div class="text-subtitle1">Assets</div>
        </div>
        <q-separator />
        <q-scroll-area style="height: 30vh;">
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
              <asset-component :disabled="manager.currentAssetSelection.length > 0 && onlyAllowSingleAsset" :add="true" :asset="asset" :outSelectedAssets="manager.currentAssetSelection" />
            </div>
          </q-list>
        </q-scroll-area>
      </q-card>
      <q-card flat class="col">
        <div class="q-pa-sm">
          <div class="text-subtitle1">Selected</div>
        </div>
        <q-separator />
        <q-scroll-area style="height: 30vh">
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
            <asset-component :add="false" :asset="asset" :outSelectedAssets="manager.currentAssetSelection" v-for="asset in manager.currentAssetSelection" :key="asset.id" />
          </q-list>
        </q-scroll-area>
      </q-card>
      <q-card flat class="col-2">
        <div class="q-pa-sm">
          <div class="text-subtitle1">Filters</div>
        </div>
        <q-separator />
        <q-checkbox label="Enable Tag Filters" v-model="enableTagFilters" />
        <q-scroll-area style="height: 30vh">
          <q-list>
            <q-item v-for="tag in tagsFilterList" :key="tag">
              <q-checkbox :disable="!enableTagFilters" :label="tag" :value="filteredTags.findIndex(el => { return el === tag } ) !== -1" @input="onClickTagFilter(tag)" />
            </q-item>
          </q-list>
        </q-scroll-area>
      </q-card>
    </div>
  </div>
</template>

<script lang="ts">
// eslint-disable-next-line camelcase
import { GameAsset, Manager } from 'src/store/models'
import { Vue, Component, Prop } from 'vue-property-decorator'
import AssetComponent from 'components/AssetComponent.vue'

@Component({ components: { AssetComponent } })
export default class AssetBrowserComponent extends Vue {
    assets : GameAsset[] = []
    selectedAssets : GameAsset[] = []
    // manager : Manager|undefined = undefined
    // outSelectedAssets: GameAsset[] = []
    @Prop({ required: false, type: String, default: 'ALL' }) teamFilter!: string
    @Prop({ required: false, type: String, default: '' }) assetSearchFilter!: string
    @Prop({ required: false }) manager!: Manager
    @Prop({ required: false, default: false, type: Boolean }) onlyAllowSingleAsset!: boolean
    // @Prop({ required: true, type: Array, default: [] })
    outSelectedAssets: GameAsset[] = []
    tagsFilterList : string[] = []
    filteredTags : string[] = []
    enableTagFilters = false

    onClickTagFilter (tag : string) {
      console.log('click')
      if (this.filteredTags.findIndex(el => { return el === tag }) === -1) {
        this.filteredTags.push(tag)
      } else {
        this.filteredTags.splice(this.filteredTags.findIndex(el => { return el === tag }), 1)
      }
    }

    get filteredAssets () {
      console.log('update')
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      return this.assets.filter(a => { return ((a.name.toLowerCase().includes(this.assetSearchFilter.toLowerCase()) || a.asset_type.toLowerCase().includes(this.assetSearchFilter.toLowerCase())) && (this.enableTagFilters ? this.filteredTags.every(el => a.tags.includes(el)) : true)) })
    }

    mounted () {
      // this.manager = new Manager(this)
      this.manager.getGameAssets().then(result => {
        console.log(result.data)
        this.assets = <GameAsset[]>result.data
        for (let i = 0; i < this.assets.length; ++i) {
          for (let j = 0; j < this.assets[i].tags.length; ++j) {
            const tag = this.assets[i].tags[j]
            if (this.tagsFilterList.findIndex(el => { return el === tag }) === -1) {
              this.tagsFilterList.push(tag)
            }
          }
        }
      }).catch(err => {
        console.error(err)
      })

      this.outSelectedAssets = this.manager.currentAssetSelection
      // eslint-disable-next-line camelcase
      // this.manager.currentAssetSelection[0] = defaultGameAsset_second
    }
}
</script>
