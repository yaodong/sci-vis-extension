import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Component.extend({

  store: Ember.inject.service(),

  init() {
    this._super(...arguments);
    this.refreshSphereData();
  },

  analysis: null,

  images: Ember.computed("analysis", function () {
    let imageBaseUrl = Config.APP.API_HOST + "/static/analyses/" + this.get("analysis.id");
    return {
      preview: imageBaseUrl + "/base_preview.gif",
      persistence: null,
      projection: null,
    }
  }),

  sphereData: null,

  refreshSphereData() {
    this.get('store').findRecord('query', `${this.get('analysis.id')}::shpere-data`).then((q) => {
      this.set('sphereData', q.get('content'));
    });
  },


  directionData: {},

  actions: {
    sphereDirectionChanged(index, longitude, latitude, distance) {
      this.set("directionData.index", index);
      this.set("directionData.longitude", longitude);
      this.set("directionData.latitude", latitude);
      this.set("directionData.distance", distance);
    }
  }

});
