import DS from 'ember-data';
import ENV from 'webapp/config/environment';

export default DS.JSONAPIAdapter.extend({
  host: ENV.APP.API_HOST,
  namespace: 'api'
});
