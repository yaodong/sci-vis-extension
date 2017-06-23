import Ember from 'ember';

export default Ember.Route.extend({

  model() {
    return {
      analyses: this.get('store').query('analysis', {
        ordering: '-id',
        page: 1
      })
    };
  }

});
