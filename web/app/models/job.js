import DS from 'ember-data';

export default DS.Model.extend({
  name: DS.attr('string'),
  method: DS.attr('string'),
  inputs: DS.attr(),
  outputs: DS.attr(),
  startedAt: DS.attr('date'),
  createdAt: DS.attr('date'),
  completedAt: DS.attr('date'),
  percentage: DS.attr()
});
