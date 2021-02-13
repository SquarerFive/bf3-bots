<template>
  <div>
    <div class="row">
      <q-card flat class="col">
        <div class="q-pa-sm">
          <q-checkbox :value="allAssetsSelected" @input="selectAllAssets">
            <div class="text-subtitle1" style="margin:0; padding:0;">Assets</div>
            <br><div class="text-subtitle2" style="margin-top:-30px;color:#989898;font-size:12px; padding:0">{{filteredAssets.length}} assets | {{assetSliceIndex}}/{{maxAssetSliceIndex}}</div>
          </q-checkbox>
          <q-btn :disable="assetSliceIndex >= maxAssetSliceIndex" @click="assetSliceIndex+=1" dense style="float: right" color="primary" icon="keyboard_arrow_right" />
          <q-btn :disable="assetSliceIndex <= 0" @click="assetSliceIndex-=1" dense style="float: right; margin-right: 5px;" color="primary" icon="keyboard_arrow_left" />
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
              <asset-component :actionSelectedAssets="actionSelectedAssets" :disabled="manager.currentAssetSelection.length > 0 && onlyAllowSingleAsset || (currentSelectedAsset !== null && asset.tags.findIndex(el => {return el === 'Attachment'}) == -1)" :add="true" :asset="asset" :outSelectedAssets="(currentSelectedAsset === null || asset == undefined) ? manager.currentAssetSelection : currentSelectedAsset.children" />
            </div>
          </q-list>
        </q-scroll-area>
        <q-btn :disable="actionSelectedAssets.length ==0" label="Add To Selected" push style="margin-left: 24px;" @click="addToSelected" />
      </q-card>
      <q-card flat class="col">
        <div class="q-pa-sm">
          <q-checkbox :value="allSelectedAssetsSelected" @input="selectedAllSelectedAssets">
            <div class="text-subtitle1">Selected</div>
          </q-checkbox>
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
            <asset-component :clickable="true" :selected="isAssetActiveSelected(asset)" :onClick="setActiveSelectedAsset" :actionSelectedAssets="actionSelectedSelectedAssets" :add="false" :asset="asset" :outSelectedAssets="manager.currentAssetSelection" v-for="asset in manager.currentAssetSelection" :key="asset.id" />
          </q-list>
        </q-scroll-area>
        <q-btn :disable="actionSelectedSelectedAssets.length ==0" label="Remove from Selected" push style="margin-left: 24px;" @click="removeFromSelected" />
      </q-card>
      <q-separator vertical style="margin-left: 12px; margin-right: 12px;" />
      <q-card flat bordered class="col-2">
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
      <q-card flat bordered class="col-2" style="margin-left: 12px;" v-if="currentSelectedAsset !== null">
        <div class="q-pa-sm">
          <div class="text-subtitle1">Asset Children/Attachments</div>
        </div>
        <q-separator />
        <q-scroll-area style="height: 30vh">
          <q-list>
            <asset-component :clickable="false" :asset="child" v-for="child in currentSelectedAsset.children" :key="child.path" :add="false" :outSelectedAssets="currentSelectedAsset.children" :actionSelectedAssets="[]" :selectable="false" />
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
    actionSelectedAssets: GameAsset[] = []
    actionSelectedSelectedAssets: GameAsset[] = []
    assetSliceIndex = 0
    maxAssetSliceIndex = 2

    // selected asset to add attachments
    currentSelectedAsset: GameAsset|null = null

    setActiveSelectedAsset (asset : GameAsset) {
      if (this.currentSelectedAsset != null) {
        console.log('valid selected asset', this.currentSelectedAsset.path, asset.path)
        if (this.currentSelectedAsset.path === asset.path) {
          this.currentSelectedAsset = null
          console.log('set null')
        }
      } else {
        this.currentSelectedAsset = asset
        console.log(this.currentSelectedAsset)
      }
    }

    isAssetActiveSelected (asset : GameAsset) {
      if (this.currentSelectedAsset) {
        if (asset.path === this.currentSelectedAsset.path) {
          return true
        }
      }
      return false
    }

    get activeSelectedAssetPath () {
      if (this.currentSelectedAsset) {
        return this.currentSelectedAsset
      }
      return ''
    }

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
      const filteredAssets = this.assets.filter(a => { return ((a.name.toLowerCase().includes(this.assetSearchFilter.toLowerCase()) || a.asset_type.toLowerCase().includes(this.assetSearchFilter.toLowerCase())) && (this.enableTagFilters ? this.filteredTags.every(el => a.tags.includes(el)) : true)) })
      return filteredAssets.slice(this.assetSliceIndex * 64, (this.assetSliceIndex + 1) * 64)
    }

    get allAssetsSelected () {
      return this.filteredAssets.every((el) => {
        return this.actionSelectedAssets.findIndex(elm => { return el.path === elm.path }) > -1
      })
    }

    get allSelectedAssetsSelected () {
      if (this.outSelectedAssets.length > 0) {
        return this.outSelectedAssets.every((el) => {
          return this.actionSelectedSelectedAssets.findIndex(elm => { return el.path === elm.path }) > -1
        })
      } else {
        return false
      }
    }

    selectAllAssets () {
      if (!this.allAssetsSelected) {
        this.filteredAssets.forEach(elm => { this.actionSelectedAssets.push(elm) })
      } else {
        this.actionSelectedAssets = []
      }
      console.log('push all assets', this.actionSelectedAssets)
    }

    selectedAllSelectedAssets () {
      if (!this.allSelectedAssetsSelected) {
        this.outSelectedAssets.forEach(elm => { this.actionSelectedSelectedAssets.push(elm) })
      } else {
        this.actionSelectedSelectedAssets = []
      }
    }

    addToSelected () {
      this.actionSelectedAssets.forEach(el => {
        if (!this.outSelectedAssets.some(elm => { return el.path === elm.path })) {
          this.outSelectedAssets.push(el)
        }
      })
    }

    removeFromSelected () {
      this.actionSelectedSelectedAssets.forEach(el => {
        if (this.outSelectedAssets.findIndex(elm => { return el.path === elm.path }) > -1) {
          this.outSelectedAssets.splice(this.outSelectedAssets.findIndex(elm => { return el.path === elm.path }), 1)
        }
      })
      this.actionSelectedSelectedAssets = this.actionSelectedSelectedAssets.filter(el => { return this.outSelectedAssets.findIndex(elm => { return elm.path === el.path }) > -1 })
    }

    mounted () {
      // this.manager = new Manager(this)
      this.manager.getGameAssets().then(result => {
        console.log(result.data)
        this.assets = <GameAsset[]>result.data
        this.maxAssetSliceIndex = Math.ceil(this.assets.length / 64)
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
