<template>
    <q-page class="bg-grey-10"> <!-- style="color: white; height: 100%; width: 100%; margin-top: 0; padding: 0"> -->
        <q-dialog full-width ref="assetDialog" v-model="assetBrowserOpened" style="width: 50vh">
            <q-card style="width: 50vh" v-if="manager">
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
                <asset-browser-component :onlyAllowSingleAsset="isSettingKitAsset" :manager="manager" ref='assetBrowser' :teamFilter="''" :assetSearchFilter="searchFilter"> </asset-browser-component>
                <q-btn color="primary" style="margin: 5px; float: right;">
                    Submit
                </q-btn>
                </q-card-section>
            </q-card>
        </q-dialog>
        <q-dialog v-model="cloneLoadoutOpened">
            <q-card style="width: 60vh">
                <q-card-section class="row items-center q-pb-none">
                    <div class="text-h6">Copy from</div>
                    <q-space />
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>
                <q-card-section>
                    <div class="text-subtitle-2">
                        Click on a tree item to select.
                    </div>
                    <q-tree :nodes="cloneTree" node-key="label">
                    </q-tree>
                </q-card-section>
                <q-card-section>
                    <div class="text-subtitle-2" v-if="selectedTreeNode">
                        Selected: {{selectedTreeNode.label}} [Owner ID: {{selectedTreeNode.owner_id}}, Type: {{selectedTreeNode.type}}, Item ID: {{selectedTreeNode.id}}]
                    </div>
                </q-card-section>
                <q-card-section style="float: right;">
                    <q-btn color="warning" label="start copy" text-color="dark" :disable="selectedTreeNode == null" @click="onStartCopyLoadout"/>
                </q-card-section>
            </q-card>
        </q-dialog>
        <q-toolbar class="bg-dark">
            <q-btn-dropdown :label="faction" color="warning" text-color="dark">
                <q-list>
                    <q-item v-for="factionOption in factionOptions" :key="factionOption" clickable @click="onSelectFaction(factionOption)">
                        <q-item-section>
                            {{factionOption}}
                        </q-item-section>
                    </q-item>
                </q-list>
            </q-btn-dropdown>
            <q-toolbar-title>
            </q-toolbar-title>
            <q-btn color="warning" text-color="dark" icon="content_copy" label="copy from" @click="cloneLoadoutOpened=true"/>
            <q-btn color="warning" text-color="dark" icon="save" label="save" @click="onUpdateKits" style="margin-left: 5px" />
        </q-toolbar>
        <div class="row" v-if="activeKitCollection && manager">
            <soldier-kit-component :manager="manager" :kit="activeKitCollection.assault" :name="'Assault'" class="col" :onRequestAddAsset="onRequestAddAsset" />
            <soldier-kit-component :manager="manager" :kit="activeKitCollection.engineer" :name="'Engineer'" class="col" :onRequestAddAsset="onRequestAddAsset" />
            <soldier-kit-component :manager="manager" :kit="activeKitCollection.support" :name="'Support'" class="col" :onRequestAddAsset="onRequestAddAsset" />
            <soldier-kit-component :manager="manager" :kit="activeKitCollection.recon" :name="'Recon'" class="col" :onRequestAddAsset="onRequestAddAsset" />
        </div>
    </q-page>
</template>

<script lang="ts">
import { deepCopy, GameAsset, Level, Manager, SoldierKitCollection, TreeNode } from 'src/store/models'
import { Component, Vue } from 'vue-property-decorator'
import AssetBrowserComponent from '../../../components/AssetBrowserComponent.vue'
import SoldierKitComponent from 'components/SoldierKitComponent.vue'
import { ManagerStore } from 'src/store/ManagerStoreModule'

@Component({ components: { AssetBrowserComponent, SoldierKitComponent } })
export default class LoadoutManager extends Vue {
    assetBrowserOpened = false
    cloneLoadoutOpened = false
    searchFilter = ''
    selectAssets: GameAsset[] = []
    level : Level | null = null
    factionOptions : string[] = ['Faction 0', 'Faction 1']
    faction = 'Faction 0'
    friendlyKitCollection : SoldierKitCollection | null = null
    enemyKitCollection : SoldierKitCollection | null = null

    activeKitCollection : SoldierKitCollection | null = null
    manager : Manager | null = null

    cloneTree : TreeNode[] = []
    selectedTreeNode : TreeNode | null = null
    isSettingKitAsset = false

    mounted () {
      console.log('mounted loadout manager')
      this.$on('onRequestAddAsset', (assetArray : GameAsset[]) => {
        console.log(assetArray)
      })
      this.manager = new Manager(this)
      const levelId = this.$route.params.level_id
      this.manager.get_level(String(ManagerStore.currentProject.project_id), levelId).then(result => {
        this.level = result
        console.log(this.level)
        this.friendlyKitCollection = this.level.friendly_kit
        this.enemyKitCollection = this.level.enemy_kit
        this.activeKitCollection = this.level.friendly_kit
        this.cloneTree = this.levelsToTree()
      }).catch(err => {
        console.error(err)
      })
    }

    onRequestAddAsset (assetArray : GameAsset[], isKitAsset : boolean) {
      this.$nextTick(() => {
        console.log(this.$refs)
      })
      this.isSettingKitAsset = isKitAsset
      this.assetBrowserOpened = true
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      const browser : AssetBrowserComponent = <AssetBrowserComponent>(this.$refs.assetDialog)
      browser.outSelectedAssets = assetArray
      this.selectAssets = assetArray
    }

    onSelectFaction (newFaction : string) {
      this.faction = newFaction
      switch (this.faction) {
        case 'Faction 0':
          this.activeKitCollection = this.friendlyKitCollection
          break
        case 'Faction 1':
          this.activeKitCollection = this.enemyKitCollection
          break
      }
    }

    onUpdateKits () {
      if (this.manager && this.level && this.friendlyKitCollection && this.enemyKitCollection) {
        this.manager.updateKits(String(this.level.project_id), String(this.level.level_id), this.friendlyKitCollection, this.enemyKitCollection).then(result => {
          console.log(result)
        }).catch(err => {
          console.error(err)
        })
      }
    }

    onClickTreeItem (item : TreeNode) {
      this.selectedTreeNode = item
      console.log(this.selectedTreeNode)
    }

    levelsToTree () {
      const tree : TreeNode[] = []
      if (this.manager && this.level) {
        const levels = ManagerStore.availableLevels
        levels.forEach(l => {
          if (this.level) {
            let factionOneItemCount = 0
            l.friendly_kit.assault.primary_weapon.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.assault.secondary_weapon.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.assault.primary_gadget.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.assault.secondary_gadget.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.assault.melee.forEach(() => { factionOneItemCount += 1 })

            l.friendly_kit.engineer.primary_weapon.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.engineer.secondary_weapon.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.engineer.primary_gadget.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.engineer.secondary_gadget.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.engineer.melee.forEach(() => { factionOneItemCount += 1 })

            l.friendly_kit.support.primary_weapon.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.support.secondary_weapon.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.support.primary_gadget.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.support.secondary_gadget.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.support.melee.forEach(() => { factionOneItemCount += 1 })

            l.friendly_kit.recon.primary_weapon.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.recon.secondary_weapon.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.recon.primary_gadget.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.recon.secondary_gadget.forEach(() => { factionOneItemCount += 1 })
            l.friendly_kit.recon.melee.forEach(() => { factionOneItemCount += 1 })
            const factionOneNode : TreeNode = {
              label: `Faction 0 (items: ${factionOneItemCount})`,
              icon: 'emoji_flags',
              children: <TreeNode[]>[],
              type: 'faction',
              selectable: true,
              // eslint-disable-next-line @typescript-eslint/unbound-method
              handler: this.onClickTreeItem,
              expandable: true,
              owner_id: this.level.id,
              id: 0
            }
            let factionTwoItemCount = 0
            l.enemy_kit.assault.primary_weapon.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.assault.secondary_weapon.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.assault.primary_gadget.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.assault.secondary_gadget.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.assault.melee.forEach(() => { factionTwoItemCount += 1 })

            l.enemy_kit.engineer.primary_weapon.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.engineer.secondary_weapon.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.engineer.primary_gadget.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.engineer.secondary_gadget.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.engineer.melee.forEach(() => { factionTwoItemCount += 1 })

            l.enemy_kit.support.primary_weapon.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.support.secondary_weapon.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.support.primary_gadget.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.support.secondary_gadget.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.support.melee.forEach(() => { factionTwoItemCount += 1 })

            l.enemy_kit.recon.primary_weapon.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.recon.secondary_weapon.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.recon.primary_gadget.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.recon.secondary_gadget.forEach(() => { factionTwoItemCount += 1 })
            l.enemy_kit.recon.melee.forEach(() => { factionTwoItemCount += 1 })
            const factionTwoNode : TreeNode = {
              label: `Faction 1 (items: ${factionTwoItemCount})`,
              icon: 'emoji_flags',
              children: <TreeNode[]>[],
              type: 'faction',
              selectable: true,
              // eslint-disable-next-line @typescript-eslint/unbound-method
              handler: this.onClickTreeItem,
              expandable: true,
              owner_id: l.id,
              id: 1
            }
            tree.push({
              label: l.name,
              icon: 'map',
              children: <TreeNode[]>[factionOneNode, factionTwoNode],
              type: 'level',
              selectable: true,
              // eslint-disable-next-line @typescript-eslint/unbound-method
              handler: this.onClickTreeItem,
              expandable: true,
              owner_id: l.project_id,
              id: l.id
            })
          }
        })
      }
      return tree
    }

    onStartCopyLoadout () {
      console.log('request copy', this.selectedTreeNode)
      if (this.selectedTreeNode) {
        console.log('available levels: ', ManagerStore.availableLevels)
        if (this.selectedTreeNode.type === 'faction') {
          const level = ManagerStore.availableLevels.filter(l => { return this.selectedTreeNode ? (l.id === this.selectedTreeNode.owner_id) : false })[0]
          console.log('request copy for faction', level)
          if (level && this.activeKitCollection) {
            console.log('copying...', this.selectedTreeNode)
            const selectedKit = this.selectedTreeNode.id === 0 ? level.friendly_kit : level.enemy_kit
            const copiedKit = <SoldierKitCollection>deepCopy<SoldierKitCollection>(
              selectedKit
            )
            this.activeKitCollection.assault.primary_weapon = copiedKit.assault.primary_weapon
            this.activeKitCollection.assault.secondary_weapon = copiedKit.assault.secondary_weapon
            this.activeKitCollection.assault.primary_gadget = copiedKit.assault.primary_gadget
            this.activeKitCollection.assault.secondary_gadget = copiedKit.assault.secondary_gadget
            this.activeKitCollection.assault.melee = copiedKit.assault.melee
            this.activeKitCollection.assault.appearance = copiedKit.assault.appearance
            this.activeKitCollection.assault.kit_assets = copiedKit.assault.kit_assets
            this.activeKitCollection.assault.kit_asset = copiedKit.assault.kit_asset

            this.activeKitCollection.engineer.primary_weapon = copiedKit.engineer.primary_weapon
            this.activeKitCollection.engineer.secondary_weapon = copiedKit.engineer.secondary_weapon
            this.activeKitCollection.engineer.primary_gadget = copiedKit.engineer.primary_gadget
            this.activeKitCollection.engineer.secondary_gadget = copiedKit.engineer.secondary_gadget
            this.activeKitCollection.engineer.melee = copiedKit.engineer.melee
            this.activeKitCollection.engineer.appearance = copiedKit.engineer.appearance
            this.activeKitCollection.engineer.kit_assets = copiedKit.engineer.kit_assets
            this.activeKitCollection.engineer.kit_asset = copiedKit.engineer.kit_asset

            this.activeKitCollection.support.primary_weapon = copiedKit.support.primary_weapon
            this.activeKitCollection.support.secondary_weapon = copiedKit.support.secondary_weapon
            this.activeKitCollection.support.primary_gadget = copiedKit.support.primary_gadget
            this.activeKitCollection.support.secondary_gadget = copiedKit.support.secondary_gadget
            this.activeKitCollection.support.melee = copiedKit.support.melee
            this.activeKitCollection.support.appearance = copiedKit.support.appearance
            this.activeKitCollection.support.kit_assets = copiedKit.support.kit_assets
            this.activeKitCollection.support.kit_asset = copiedKit.support.kit_asset

            this.activeKitCollection.recon.primary_weapon = copiedKit.recon.primary_weapon
            this.activeKitCollection.recon.secondary_weapon = copiedKit.recon.secondary_weapon
            this.activeKitCollection.recon.primary_gadget = copiedKit.recon.primary_gadget
            this.activeKitCollection.recon.secondary_gadget = copiedKit.recon.secondary_gadget
            this.activeKitCollection.recon.melee = copiedKit.recon.melee
            this.activeKitCollection.recon.appearance = copiedKit.recon.appearance
            this.activeKitCollection.recon.kit_assets = copiedKit.recon.kit_assets
            this.activeKitCollection.recon.kit_asset = copiedKit.recon.kit_asset

            console.log('copied.')
          }
        }
        if (this.selectedTreeNode.type === 'level') {
          const level = ManagerStore.availableLevels.filter(l => { return this.selectedTreeNode ? (l.id === this.selectedTreeNode.id) : false })[0]
          if (level && this.friendlyKitCollection && this.enemyKitCollection) {
            console.log('firing start copy', this.selectedTreeNode)
            const copiedFriendlyKit = <SoldierKitCollection>deepCopy<SoldierKitCollection>(
              level.friendly_kit
            )
            const copiedEnemyKit = <SoldierKitCollection>deepCopy<SoldierKitCollection>(
              level.enemy_kit
            )
            console.log('level: ', level)
            this.friendlyKitCollection.assault.primary_weapon = copiedFriendlyKit.assault.primary_weapon
            this.friendlyKitCollection.assault.secondary_weapon = copiedFriendlyKit.assault.secondary_weapon
            this.friendlyKitCollection.assault.primary_gadget = copiedFriendlyKit.assault.primary_gadget
            this.friendlyKitCollection.assault.secondary_gadget = copiedFriendlyKit.assault.secondary_gadget
            this.friendlyKitCollection.assault.melee = copiedFriendlyKit.assault.melee
            this.friendlyKitCollection.assault.appearance = copiedFriendlyKit.assault.appearance
            this.friendlyKitCollection.assault.kit_assets = copiedFriendlyKit.assault.kit_assets
            this.friendlyKitCollection.assault.kit_asset = copiedFriendlyKit.assault.kit_asset

            this.friendlyKitCollection.engineer.primary_weapon = copiedFriendlyKit.engineer.primary_weapon
            this.friendlyKitCollection.engineer.secondary_weapon = copiedFriendlyKit.engineer.secondary_weapon
            this.friendlyKitCollection.engineer.primary_gadget = copiedFriendlyKit.engineer.primary_gadget
            this.friendlyKitCollection.engineer.secondary_gadget = copiedFriendlyKit.engineer.secondary_gadget
            this.friendlyKitCollection.engineer.melee = copiedFriendlyKit.engineer.melee
            this.friendlyKitCollection.engineer.appearance = copiedFriendlyKit.engineer.appearance
            this.friendlyKitCollection.engineer.kit_assets = copiedFriendlyKit.engineer.kit_assets
            this.friendlyKitCollection.engineer.kit_asset = copiedFriendlyKit.engineer.kit_asset

            this.friendlyKitCollection.support.primary_weapon = copiedFriendlyKit.support.primary_weapon
            this.friendlyKitCollection.support.secondary_weapon = copiedFriendlyKit.support.secondary_weapon
            this.friendlyKitCollection.support.primary_gadget = copiedFriendlyKit.support.primary_gadget
            this.friendlyKitCollection.support.secondary_gadget = copiedFriendlyKit.support.secondary_gadget
            this.friendlyKitCollection.support.melee = copiedFriendlyKit.support.melee
            this.friendlyKitCollection.support.appearance = copiedFriendlyKit.support.appearance
            this.friendlyKitCollection.support.kit_assets = copiedFriendlyKit.support.kit_assets
            this.friendlyKitCollection.support.kit_asset = copiedFriendlyKit.support.kit_asset

            this.friendlyKitCollection.recon.primary_weapon = copiedFriendlyKit.recon.primary_weapon
            this.friendlyKitCollection.recon.secondary_weapon = copiedFriendlyKit.recon.secondary_weapon
            this.friendlyKitCollection.recon.primary_gadget = copiedFriendlyKit.recon.primary_gadget
            this.friendlyKitCollection.recon.secondary_gadget = copiedFriendlyKit.recon.secondary_gadget
            this.friendlyKitCollection.recon.melee = copiedFriendlyKit.recon.melee
            this.friendlyKitCollection.recon.appearance = copiedFriendlyKit.recon.appearance
            this.friendlyKitCollection.recon.kit_assets = copiedFriendlyKit.recon.kit_assets
            this.friendlyKitCollection.recon.kit_asset = copiedFriendlyKit.recon.kit_asset

            this.enemyKitCollection.assault.primary_weapon = copiedEnemyKit.assault.primary_weapon
            this.enemyKitCollection.assault.secondary_weapon = copiedEnemyKit.assault.secondary_weapon
            this.enemyKitCollection.assault.primary_gadget = copiedEnemyKit.assault.primary_gadget
            this.enemyKitCollection.assault.secondary_gadget = copiedEnemyKit.assault.secondary_gadget
            this.enemyKitCollection.assault.melee = copiedEnemyKit.assault.melee
            this.enemyKitCollection.assault.appearance = copiedEnemyKit.assault.appearance
            this.enemyKitCollection.assault.kit_assets = copiedEnemyKit.assault.kit_assets
            this.enemyKitCollection.assault.kit_asset = copiedEnemyKit.assault.kit_asset

            this.enemyKitCollection.engineer.primary_weapon = copiedEnemyKit.engineer.primary_weapon
            this.enemyKitCollection.engineer.secondary_weapon = copiedEnemyKit.engineer.secondary_weapon
            this.enemyKitCollection.engineer.primary_gadget = copiedEnemyKit.engineer.primary_gadget
            this.enemyKitCollection.engineer.secondary_gadget = copiedEnemyKit.engineer.secondary_gadget
            this.enemyKitCollection.engineer.melee = copiedEnemyKit.engineer.melee
            this.enemyKitCollection.engineer.appearance = copiedEnemyKit.engineer.appearance
            this.enemyKitCollection.engineer.kit_assets = copiedEnemyKit.engineer.kit_assets
            this.enemyKitCollection.engineer.kit_asset = copiedEnemyKit.engineer.kit_asset

            this.enemyKitCollection.support.primary_weapon = copiedEnemyKit.support.primary_weapon
            this.enemyKitCollection.support.secondary_weapon = copiedEnemyKit.support.secondary_weapon
            this.enemyKitCollection.support.primary_gadget = copiedEnemyKit.support.primary_gadget
            this.enemyKitCollection.support.secondary_gadget = copiedEnemyKit.support.secondary_gadget
            this.enemyKitCollection.support.melee = copiedEnemyKit.support.melee
            this.enemyKitCollection.support.appearance = copiedEnemyKit.support.appearance
            this.enemyKitCollection.support.kit_assets = copiedEnemyKit.support.kit_assets
            this.enemyKitCollection.support.kit_asset = copiedEnemyKit.support.kit_asset

            this.enemyKitCollection.recon.primary_weapon = copiedEnemyKit.recon.primary_weapon
            this.enemyKitCollection.recon.secondary_weapon = copiedEnemyKit.recon.secondary_weapon
            this.enemyKitCollection.recon.primary_gadget = copiedEnemyKit.recon.primary_gadget
            this.enemyKitCollection.recon.secondary_gadget = copiedEnemyKit.recon.secondary_gadget
            this.enemyKitCollection.recon.melee = copiedEnemyKit.recon.melee
            this.enemyKitCollection.recon.appearance = copiedEnemyKit.recon.appearance
            this.enemyKitCollection.recon.kit_assets = copiedEnemyKit.recon.kit_assets
            this.enemyKitCollection.recon.kit_asset = copiedEnemyKit.recon.kit_asset

            this.activeKitCollection = this.friendlyKitCollection
            console.log('copied', this.activeKitCollection)
          }
        } else {
        }
      }
    }
}
</script>
