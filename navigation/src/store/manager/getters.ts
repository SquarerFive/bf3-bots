import { GetterTree } from 'vuex'
import { StateInterface } from '../index'
import { ManagerStateInterface } from './state'

const getters: GetterTree<ManagerStateInterface, StateInterface> = {
  someAction (/* context */) {
    // your code
  }
}

export default getters
