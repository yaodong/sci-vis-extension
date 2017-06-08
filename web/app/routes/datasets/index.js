import Ember from 'ember';

export default Ember.Route.extend({
  model() {
    return this.get('store').findAll('dataset', {reload: true}).then((items) => {
      return items.sortBy('-id');
    });
  }
});
