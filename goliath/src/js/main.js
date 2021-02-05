import 'alpinejs'
import '../scss/main.scss'
import { dom, library } from '@fortawesome/fontawesome-svg-core'
import { faBars, faTimes } from '@fortawesome/free-solid-svg-icons'

library.add(faBars, faTimes)

// Will automatically find any <i> tags in the page and replace those with <svg> elements.
// https://fontawesome.com/how-to-use/javascript-api/methods/dom-i2svg
// https://fontawesome.com/how-to-use/javascript-api/methods/dom-watch
dom.watch()
