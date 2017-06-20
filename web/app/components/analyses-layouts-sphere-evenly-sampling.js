import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Component.extend({

  store: Ember.inject.service(),

  init() {
    this._super(...arguments);
    this.refreshSphereData();
  },

  analysis: null,

  imageBaseUrl: Ember.computed("analysis", function () {
    return Config.APP.API_HOST + "/static/analyses/" + this.get("analysis.id");
  }),

  images: Ember.computed("analysis", "imageBaseUrl", function () {
    return {
      preview: this.get("imageBaseUrl") + "/base_preview.gif",
      persistence: null,
      projection: null
    };
  }),

  projectedImages: Ember.computed("currentDirectionData", "imageBaseUrl", function () {
    const index = this.get("currentDirectionData.index");
    const imageUrl = this.get("imageBaseUrl") + "/projected_" + index + "_";

    let images = {
      dots: imageUrl + "preview_dots.png",
      diagram: imageUrl + "diagram.png"
    };

    if (this.get('analysis.dataset.format') == 'graph') {
      images.graph = imageUrl + "preview_graph.png";
    } else {
      images.graph = null;
    }

    return images;
  }),

  sphereData: null,

  refreshSphereData() {
    this.get('store').findRecord('query', `${this.get('analysis.id')}--project-directions`).then((q) => {
      this.set('sphereData', q.get('content'));
    });
  },

  currentDirectionData: null,

  actions: {
    sphereDirectionChanged(index, longitude, latitude, distance) {
      this.set('currentDirectionData', {
        index: index,
        longitude: longitude,
        latitude: latitude,
        distance: distance
      });
    }
  }

});
