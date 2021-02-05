
export interface ProfileInterface {
  username: string,
  token: string
}

export interface ManagerStateInterface {
  loggedIn: boolean;
  profile: ProfileInterface,
  levelBuildProgress : number
}

function state (): ManagerStateInterface {
  return {
    loggedIn: false,
    profile: {
      username: '',
      token: ''
    },
    levelBuildProgress: 0.0
  }
}

export default state
