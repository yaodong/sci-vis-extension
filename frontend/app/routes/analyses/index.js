import Ember from 'ember';

export default Ember.Route.extend({

  model() {
    return this.get('store').findAll('analysis', {reload: true}).then((items) => {
      return items.sortBy('-id');
    });
  }

});
