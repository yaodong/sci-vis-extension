import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Controller.extend({

  bestProjection: Ember.computed("model", function() {
    return this.get("model.outputs.best_projection");
  }),

  imageBaseUrl: Ember.computed("model", function() {
    return Config.APP.API_HOST + "/static/jobs/"+ this.get("model.id");
  }),

  previewImgUrl: Ember.computed("imageBaseUrl", function() {
    return this.get("imageBaseUrl") + "/base_preview.gif";
  }),

  persistenceDiagramUrl: Ember.computed("imageBaseUrl", function() {
    return this.get("imageBaseUrl") + "/base_diagram.png";
  }),

  actions: {
    directionChanged(zx, zy, distance) {
      this.set("zx", zx);
      this.set("zy", zy);
      this.set("distance", distance);
    }
  }

});
