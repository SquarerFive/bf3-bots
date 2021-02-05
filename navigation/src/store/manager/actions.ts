import { ActionTree } from 'vuex'
import { StateInterface } from '../index'
import { ManagerStateInterface } from './state'

const actions: ActionTree<ManagerStateInterface, StateInterface> = {
  someAction (/* context */) {
    // your code
  }
}

export default actions
