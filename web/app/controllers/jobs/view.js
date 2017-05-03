import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Controller.extend({

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
    directionChanged(index, altitude, azimuth, distance) {
      this.set("index", index);
      this.set("altitude", altitude);
      this.set("azimuth", azimuth);
      this.set("distance", distance);
    }
  }

});
