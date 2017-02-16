import DRFAdapter from './drf';
import ENV from 'webapp/config/environment';

export default DRFAdapter.extend({
  host: ENV.APP.API_HOST
});
