import Ember from 'ember';
import Config from 'webapp/config/environment';
const $ = window.$;

export default Ember.Component.extend({

  zx: null,

  zy: null,

  model: null,

  didReceiveAttrs() {
    this._super(...arguments);
    $("a.ember-lightbox").map((ix, box) => {
      $(box).find("img").attr("src", this.get("projectionImageUrl"));
    });
  },

  baseUrl: Ember.computed("model", function() {
    return Config.APP.API_HOST + "/static/jobs/"+ this.get("model.ticket") + "/images";
  }),

  projectionImageUrl: Ember.computed("model", "baseUrl", "zx", "zy", function() {
    let results = this.get("model.outputs.bottleneck_distances");
    let baseUrl = this.get("baseUrl");
    return baseUrl + '/' + this.get("zx") + '__' + this.get("zy") + '.png';
  })

});
