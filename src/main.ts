import '@fontsource-variable/caveat'
import '@fontsource-variable/fraunces'
import '@fontsource-variable/nunito'
import './styles/variables.css'
import './styles/base.css'
import './styles/layout.css'
import './styles/components.css'
import './styles/animations.css'
import { mount } from 'svelte'
import App from './App.svelte'

const target = document.getElementById('app')

if (!target) {
  throw new Error('The #app element is missing from index.html')
}

export default mount(App, { target })
