import Ember from 'ember';

export default Ember.Route.extend({
  model() {
    return this.get('store').findAll('job', {reload: true}).then((jobs) => {
      return jobs.sortBy('-id');
    });
  },

  afterModel(posts, transition) {
    let interval = 1000 * 10;

    let bindReloading = function(post) {
      if (post.get('percentage') < 100 && post.get('status') == null) {
        Ember.run.later(this, (p) => {
          p.reload().then(bindReloading);
        }, post, interval);
      }
    };

    Ember.$.map(posts, (post) => {
      bindReloading(post);
    });

  }
});
