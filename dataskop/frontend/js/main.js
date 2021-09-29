import { dom, library } from '@fortawesome/fontawesome-svg-core';
import {
  faFacebook,
  faFacebookSquare,
  faGoogle,
  faInstagram,
  faTwitter,
  faTwitterSquare,
} from '@fortawesome/free-brands-svg-icons';
import {
  faBell as faBellOutline,
  faComments,
  faPaperPlane,
  faQuestionCircle,
  faUserCircle as faUserCircleOutline,
} from '@fortawesome/free-regular-svg-icons';
import {
  faAddressCard,
  faBars,
  faBell,
  faBuilding,
  faChevronCircleDown,
  faChevronDown,
  faClock,
  faExternalLinkAlt,
  faPencilAlt,
  faPersonBooth,
  faPlus,
  faSearch,
  faStarHalfAlt,
  faSyringe,
  faTachometerAlt,
  faThumbsDown,
  faThumbsUp,
  faTimes,
  faTruck,
  faUserCircle,
  faUserClock,
} from '@fortawesome/free-solid-svg-icons';
import 'alpinejs';
import 'regenerator-runtime/runtime';
import '../scss/main.scss';

// Add a subset of Font Awesome icons to be used in an ordinary way.
// https://fontawesome.com/v5.0/how-to-use/with-the-api/setup/library
library.add(
  faBars,
  faTimes,
  faUserCircle,
  faChevronDown,
  faChevronCircleDown,
  faPlus,
  faBell,
  faUserClock,
  faClock,
  faThumbsUp,
  faThumbsDown,
  faPencilAlt,
  faStarHalfAlt,
  faPaperPlane,
  faComments,
  faUserCircleOutline,
  faBellOutline,
  faQuestionCircle,
  faSyringe,
  faExternalLinkAlt,
  faSearch,
  faTruck,
  faBuilding,
  faPersonBooth,
  faTachometerAlt,
  faAddressCard,
  // brands
  faTwitter,
  faFacebook,
  faInstagram,
  faTwitterSquare,
  faFacebookSquare,
  faGoogle
);

// Will automatically find any <i> tags in the page and replace those with <svg> elements.
// https://fontawesome.com/how-to-use/javascript-api/methods/dom-i2svg
// https://fontawesome.com/how-to-use/javascript-api/methods/dom-watch
dom.watch();

function initSmoothAnchorLinkScroll() {
  // src: https://stackoverflow.com/a/7717572/5732518
  const elements = document.querySelectorAll('a[href^="#"].smooth-scroll');
  elements.forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelector(anchor.getAttribute('href')).scrollIntoView({
        behavior: 'smooth',
      });
    });
  });
}

initSmoothAnchorLinkScroll();
