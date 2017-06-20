import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('analyses-layouts-sphere-evenly-sampling', 'Integration | Component | analyses layouts sphere evenly sampling', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{analyses-layouts-sphere-evenly-sampling}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#analyses-layouts-sphere-evenly-sampling}}
      template block text
    {{/analyses-layouts-sphere-evenly-sampling}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
