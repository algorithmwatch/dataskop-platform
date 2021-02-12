import 'alpinejs'
import '../scss/main.scss'
import { dom, library } from '@fortawesome/fontawesome-svg-core'
import {
  faBars, faTimes, faUserCircle, faChevronDown, faPlus,

  // case types:
  faTruck, faBuilding, faPersonBooth, faTachometerAlt
} from '@fortawesome/free-solid-svg-icons'
import { faGoogle } from '@fortawesome/free-brands-svg-icons'

/*
  Case types icons
    <i class="fas fa-truck"></i>
    <i class="fab fa-google"></i>
    <i class="fas fa-building"></i>
    <i class="fas fa-person-booth"></i>
    <i class="fas fa-tachometer-alt"></i>
    <i class="fas fa-plus"></i>

*/

library.add(
  faBars, faTimes, faUserCircle, faChevronDown, faPlus,

  // case type icons:
  faTruck, faBuilding, faPersonBooth, faTachometerAlt, faGoogle
)

// Will automatically find any <i> tags in the page and replace those with <svg> elements.
// https://fontawesome.com/how-to-use/javascript-api/methods/dom-i2svg
// https://fontawesome.com/how-to-use/javascript-api/methods/dom-watch
dom.watch()
