import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Component.extend({
  store: Ember.inject.service(),
  ajax: Ember.inject.service(),

  init() {
    this._super(...arguments);
    this.refreshSphereData();
    this.fetchPreviewData();
  },

  analysis: null,

  sphereData: null,

  previewIsReady: null,

  imageBaseUrl: Ember.computed("analysis", function () {
    return Config.APP.API_HOST + "/static/analyses/" + this.get("analysis.id");
  }),

  images: Ember.computed("previewIsReady", "analysis", "imageBaseUrl", function () {
    if (this.get("previewIsReady")) {
      return {
        preview: this.get("imageBaseUrl") + "/base_preview.gif",
        persistence: this.get("imageBaseUrl") + '/base_diagram.png'
      };
    } else {
      return {preview: null, persistence: null};
    }
  }),

  fetchPreviewData() {
    this.get('ajax').post(Config.APP.API_HOST + '/api/analyses/query', {
      data: {
        'analysis_id': this.get('analysis.id'),
        'function': 'sphere_is_ready'
      }
    }).then((response) => {
      this.set('previewIsReady', response['is_ready']);
    });
  },

  projectedImages: Ember.computed("currentDirectionData", "imageBaseUrl", function () {
    const index = this.get("currentDirectionData.index");
    const imageUrl = this.get("imageBaseUrl") + "/projected_" + index + "_";

    let images = {
      dots: imageUrl + "preview_dots.png",
      diagram: imageUrl + "diagram.png"
    };

    if (this.get('analysis.dataset.format') === 'graph') {
      images.graph = imageUrl + "preview_graph.png";
    } else {
      images.graph = null;
    }

    return images;
  }),

  refreshSphereData() {
    this.get('ajax').post(Config.APP.API_HOST + '/api/analyses/query', {
      data: {
        'analysis_id': this.get('analysis.id'),
        'function': 'sphere_projection_data'
      }
    }).then((response) => {
      this.set('sphereData', response);
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
