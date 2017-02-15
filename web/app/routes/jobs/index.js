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
        console.log("bind reloading " + post.get("id"));
        Ember.run.later(this, (p) => {
          console.log("reloading " + p.get("id"));
          p.reload().then(bindReloading);
        }, post, interval);
      }
    };

    Ember.$.map(posts, (post) => {
      bindReloading(post);
    });

  }
});
