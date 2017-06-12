import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType,
  rootURL: config.rootURL
});

Router.map(function() {
  this.route('jobs', function() {
    this.route('new');
    this.route('view', { path: '/:id' });
  });
  this.route('home', { path: '/'});
  this.route('datasets', function() {
    this.route('new');
  });

  this.route('analyses', function() {
    this.route('view', { path: '/:id' });
    this.route('new');
  });
});

export default Router;
