<template>
    <q-page class="bg-grey-10"> <!-- style="color: white; height: 100%; width: 100%; margin-top: 0; padding: 0"> -->
    <q-dialog ref="assetDialog" v-model="assetBrowserOpened">
        <q-card style="width: 600px">
            <q-card-section class="row items-center q-pb-none">
                <div class="text-h6">Asset Browser</div>
                <q-space />
                <q-btn icon="close" flat round dense v-close-popup />
            </q-card-section>
            <q-card-section>
                <q-input standout='bg-dark' v-model="searchFilter" label="Search for an Asset">
                    <template v-slot:prepend>
                        <q-icon name="search" />
                    </template>
                </q-input>
            </q-card-section>
            <q-card-section>
            <asset-browser-component ref='assetBrowser' :teamFilter="''" :assetSearchFilter="searchFilter"> </asset-browser-component>
            <q-btn color="primary" style="margin: 5px; float: right;">
                Submit
            </q-btn>
            </q-card-section>
        </q-card>
        </q-dialog>
        <div class="row">
            <soldier-kit-component :onRequestAddAsset="onRequestAddAsset" />
            <div class="col" style="height: 100%; position: relative; padding: 2px;">
                <q-card bordered flat class="my-card text-dark" style="border-radius: 0; height: 100%;">
                    <q-card-section>
                        <div class="text-h5">Assault</div>
                        <div class="text-subtitle2">Kit Instance</div>
                    </q-card-section>
                    <q-separator />
                    <q-card-section>
                        <q-card bordered flat style="margin-bottom:5px;">
                            <div class="q-pa-sm">
                                <div class="row">
                                    <div class="text-subtitle1 col q-pa-sm">Primary</div>
                                    <q-btn dense class="col" flat color="positive" style="float:right;">Add</q-btn>
                                </div>
                                <q-list>
                                    <q-item v-for="asset in selectAssets" :key="asset.id">
                                        test
                                    </q-item>
                                </q-list>
                            </div>
                            <q-separator />
                        </q-card>
                        <q-card bordered flat>
                            <div class="q-pa-sm">
                              <div class="text-subtitle1">Secondary</div>
                            </div>
                        </q-card>
                        <q-list>
                        </q-list>
                    </q-card-section>
                </q-card>
            </div>
            <div class="col" style="height: 100%; position: relative; padding: 2px;">
                <q-card flat bordered class="my-card text-dark" style="border-radius: 0; height: 100%;">
                    <q-card-section>
                        <div class="text-h5">Engineer</div>
                        <div class="text-subtitle2">Kit Instance</div>
                    </q-card-section>
                    <q-separator />
                    <q-card-section>
                        <div class="text-subtitle1">Active Selection</div>
                    </q-card-section>
                </q-card>
            </div>
            <div class="col" style="height: 100%; position: relative; padding: 2px;">
                <q-card flat bordered class="my-card text-dark" style="border-radius: 0; height: 100%;">
                    <q-card-section>
                        <div class="text-h5">Support</div>
                        <div class="text-subtitle2">Kit Instance</div>
                    </q-card-section>
                    <q-separator />
                    <q-card-section>
                        <div class="text-subtitle1">Active Selection</div>
                    </q-card-section>
                </q-card>
            </div>
            <div class="col" style="height: 100%; position: relative; padding: 2px;">
                <q-card flat bordered class="my-card text-dark" style="border-radius: 0; height: 100%;">
                    <q-card-section>
                        <div class="text-h5">Recon</div>
                        <div class="text-subtitle2">Kit Instance</div>
                    </q-card-section>
                    <q-separator />
                    <q-card-section>
                        <div class="text-subtitle1">Active Selection</div>
                    </q-card-section>
                </q-card>
            </div>
        </div>
    </q-page>
</template>

<script lang="ts">
import { GameAsset } from 'src/store/models'
import { Component, Vue } from 'vue-property-decorator'
import AssetBrowserComponent from '../../../components/AssetBrowserComponent.vue'
import SoldierKitComponent from 'components/SoldierKitComponent.vue'

@Component({ components: { AssetBrowserComponent, SoldierKitComponent } })
export default class LoadoutManager extends Vue {
    assetBrowserOpened = true
    searchFilter = ''
    selectAssets: GameAsset[] = []

    mounted () {
      console.log('mounted loadout manager')
      this.$on('onRequestAddAsset', (assetArray : GameAsset[]) => {
        console.log(assetArray)
      })
    }

    onRequestAddAsset (assetArray : GameAsset[]) {
      this.$nextTick(() => {
        console.log(this.$refs)
      })
      this.assetBrowserOpened = true
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      const browser : AssetBrowserComponent = <AssetBrowserComponent>(this.$refs.assetDialog)
      browser.outSelectedAssets = assetArray
      this.selectAssets = assetArray
    }
}
</script>
