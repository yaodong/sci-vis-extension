import Ember from 'ember';
import Config from 'singer/config/environment';

export default Ember.Controller.extend({

  selected: null,

  actions: {
    detailChanged(data) {
      this.set("selected", {
        distance: data["dis"],
        direction: "[" + data["zx"] + ", " + data["zy"] + "]",
        imageUrl: Config.APP.API_HOST + "/static/jobs/"+ this.get("model.ticket") + "/images/" + data["zx"] + "__" + data["zy"] + ".png",
      });
    }
  }

});
