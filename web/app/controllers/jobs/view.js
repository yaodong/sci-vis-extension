import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Controller.extend({

  imageBaseUrl: Ember.computed("model", function () {
    return Config.APP.API_HOST + "/static/jobs/" + this.get("model.id");
  }),

  previewImgUrl: Ember.computed("imageBaseUrl", function () {
    return this.get("imageBaseUrl") + "/base_preview.gif";
  }),

  persistenceDiagramUrl: Ember.computed("imageBaseUrl", function () {
    return this.get("imageBaseUrl") + "/base_diagram.png";
  }),

  bestProjectionImageUrl: Ember.computed("bestIndex", "imageBaseUrl", function () {
    return this.get("imageBaseUrl") + "/projected_" + this.get("bestIndex") + "_preview_graph.png";
  }),

  best: Ember.computed("model", function () {
    let bestIndex = this.get("model.results.best");
    return this.get("model.results.directions")[bestIndex];
  }),

  bestIndex: Ember.computed("best", function () {
    return this.get("best")['index'];
  }),

  bestLongitude: Ember.computed("best", function () {
    return Math.round(this.get("best")['longitude'] * 100) / 100;
  }),

  bestLatitude: Ember.computed("best", function () {
    return Math.round(this.get("best")['distance'] * 100) / 100;
  }),

  bestDistance: Ember.computed("best", function () {
    return Math.round(this.get("best")['distance'] * 100) / 100;
  }),

  selectedIndex: null,
  selectedLongitude: 'N/A',
  selectedLatitude: 'N/A',
  selectedDistance: 'N/A',

  actions: {
    directionChanged(index, longitude, latitude, distance) {
      this.set("selectedIndex", index);
      this.set("selectedLongitude", Math.round(longitude * 100) / 100);
      this.set("selectedLatitude", Math.round(latitude * 100) / 100);
      this.set("selectedDistance", Math.round(distance * 100) / 100);
    }
  }

});
