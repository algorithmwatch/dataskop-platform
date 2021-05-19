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

  // case types:
  faTruck,
  faUserCircle,
  faUserClock,
} from '@fortawesome/free-solid-svg-icons';
import 'alpinejs';
import 'regenerator-runtime/runtime';
import '../scss/main.scss';

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

  faTwitter,
  faFacebook,
  faInstagram,
  faTwitterSquare,
  faFacebookSquare,

  // case type icons:
  faTruck,
  faBuilding,
  faPersonBooth,
  faTachometerAlt,
  faGoogle,
  faAddressCard
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

window.hubSearch = () => {
  return {
    searchTerm: '',
    isLoading: false,
    results: [],
    minTermLength: 2,
    resultType: {
      internal: 1,
      external: 2,
    },

    async handleInput(e) {
      if (this.searchTerm.length < this.minTermLength) {
        this.results = [];
        return;
      }

      await this.fetchResults();
    },

    async fetchResults() {
      this.isLoading = true;
      const caseTypeResults = await this.fetchCaseTypes();
      const caseExternalSupportResults = await this.fetchExternalSupport();
      this.results = caseTypeResults.concat(caseExternalSupportResults);
      this.isLoading = false;
    },

    async fetchCaseTypes() {
      const url = '/api/casetype/?q=' + encodeURIComponent(this.searchTerm);
      const response = await window.fetch(url);
      const result = await response.json();

      return result.map((r) => ({
        title: r.title_highlighted,
        description: r.short_description_highlighted,
        // icon: r.icon_name,
        url: r.url,
        type: this.resultType.internal,
      }));
    },

    async fetchExternalSupport() {
      const url =
        '/api/externalsupport/?q=' + encodeURIComponent(this.searchTerm);
      const response = await window.fetch(url);
      const result = await response.json();

      return result.map((r) => ({
        title: r.name_highlighted,
        description: r.description_highlighted,
        url: r.url,
        // icon: 'fas fa-external-link-alt',
        type: this.resultType.external,
      }));
    },
  };
};

initSmoothAnchorLinkScroll();
