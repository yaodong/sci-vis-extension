import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Controller.extend({
  selected: null,

  imageBaseUrl: Ember.computed("model", function() {
    return Config.APP.API_HOST + "/static/jobs/"+ this.get("model.ticket") + "/images";
  }),

  previewImgUrl: Ember.computed("imageBaseUrl", function() {
    return this.get("imageBaseUrl") + "/preview.gif";
  }),

  actions: {
    detailChanged(data) {
      let imageBaseUrl = this.get("imageBaseUrl");
      this.set("selected", {
        distance: data["dis"],
        direction: "[" + data["zx"] + ", " + data["zy"] + "]",
        imageUrl: imageBaseUrl + '/' + data["zx"] + "__" + data["zy"] + ".png",
      });
    }
  }

});
