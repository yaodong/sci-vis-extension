import Ember from 'ember';
import Config from 'webapp/config/environment';

export default Ember.Controller.extend({
  imageBaseUrl: Ember.computed("model", function() {
    return Config.APP.API_HOST + "/static/jobs/";
  }),
});
