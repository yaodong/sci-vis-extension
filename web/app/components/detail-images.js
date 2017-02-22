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
  },

  didUpdate() {
    this._super(...arguments);
    let className = this.get("className");
    $("a.ember-lightbox img." + className).map((idx, el) => {
      let img = $(el);
      let box = img.parent(".ember-lightbox");
      img.attr("src", box.attr("href"));
    });
  },

  baseUrl: Ember.computed("model", function() {
    return Config.APP.API_HOST + "/static/jobs/"+ this.get("model.ticket") + "/images";
  }),

  projectionImageUrl: Ember.computed("model", "baseUrl", "zx", "zy", function() {
    let baseUrl = this.get("baseUrl");
    return baseUrl + '/' + this.get("zx") + '__' + this.get("zy") + '.png';
  }),

  baseDiagramUrl: Ember.computed("model", "baseUrl", function() {
    let baseUrl = this.get("baseUrl");
    return baseUrl + '/diagram_base.png';
  }),

  projDiagramUrl: Ember.computed("model", "baseUrl", "zx", "zy", function() {
    let baseUrl = this.get("baseUrl");
    return baseUrl + '/diagram_' + this.get("zx") + '__' + this.get("zy") + '.png';
  })

});
