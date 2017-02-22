import Ember from 'ember';
import Config from 'webapp/config/environment';
const $ = window.$;

export default Ember.Component.extend({

  zx: null,
  zy: null,
  model: null,
  className: "detail-image",

  didReceiveAttrs() {
    this._super(...arguments);
    let className = this.get("className");
    $("a.ember-lightbox a." + className).attr("src", this.get("projectionImageUrl"));
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
