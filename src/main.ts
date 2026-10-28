import { mount } from 'svelte'
import App from './App.svelte'

const target = document.getElementById('app')

if (!target) {
  throw new Error('The #app element is missing from index.html')
}

export default mount(App, { target })
