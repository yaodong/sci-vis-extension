import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Controller.extend({

  bestProjection: Ember.computed("model", function() {
    return this.get("model.outputs.best_projection");
  }),

  zx: Ember.computed("bestProjection", function() {
    return this.get("bestProjection")[0];
  }),

  zy: Ember.computed("bestProjection", function() {
    return this.get("bestProjection")[1];
  }),

  distance: Ember.computed("bestProjection", function() {
    return this.get("bestProjection")[2];
  }),

  imageBaseUrl: Ember.computed("model", function() {
    return Config.APP.API_HOST + "/static/jobs/"+ this.get("model.ticket") + "/images";
  }),

  previewImgUrl: Ember.computed("imageBaseUrl", function() {
    return this.get("imageBaseUrl") + "/preview.gif";
  }),

  previewImgUrl: Ember.computed("imageBaseUrl", function() {
    return this.get("imageBaseUrl") + "/preview.gif";
  }),


  projectionImageUrl: Ember.computed("model", "imageBaseUrl", "zx", "zy", function() {
    let results = this.get("model.outputs.bottleneck_distances");
    let baseUrl = this.get("imageBaseUrl");
    return baseUrl + '/' + this.get("zx") + '__' + this.get("zy") + '.png';
  }),

  actions: {
    directionChanged(zx, zy, distance) {
      this.set("zx", zx);
      this.set("zy", zy);
      this.set("distance", distance);
    }
  }

});
