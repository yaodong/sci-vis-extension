import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Component.extend({

  prefix: '',

  baseUrl: Ember.computed("model", function() {
    return Config.APP.API_HOST + "/static/jobs/"+ this.get("model.ticket") + "/images";
  }),

  url: Ember.computed("baseUrl", "zx", "zy", "prefix", function() {
    let baseUrl = this.get('baseUrl');
    return baseUrl + '/' + this.get('prefix') + this.get('zx') + '__' + this.get('zy') + '.png';
  })

});
