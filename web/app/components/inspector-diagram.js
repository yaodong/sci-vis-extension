import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Component.extend({

  type: '',

  baseUrl: Ember.computed("model", function() {
    return Config.APP.API_HOST + "/static/jobs/"+ this.get("model.id");
  }),

  url: Ember.computed("baseUrl", "index", "type", function() {
    let baseUrl = this.get('baseUrl');
    return baseUrl + '/projected_' + this.get('index') + '_' + this.get("type") + '.png';
  })

});
