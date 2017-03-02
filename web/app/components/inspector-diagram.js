import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Component.extend({

  type: '',

  baseUrl: Ember.computed("model", function() {
    return Config.APP.API_HOST + "/static/jobs/"+ this.get("model.ticket");
  }),

  url: Ember.computed("baseUrl", "zx", "zy", "type", function() {
    let baseUrl = this.get('baseUrl');
    return baseUrl + '/rotated_' + this.get('zx') + '__' + this.get('zy') + '-' + this.get("type") + '.png';
  })

});
