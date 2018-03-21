import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('analyses-layouts-best-linear-projection', 'Integration | Component | analyses layouts best linear projection', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{analyses-layouts-best-linear-projection}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#analyses-layouts-best-linear-projection}}
      template block text
    {{/analyses-layouts-best-linear-projection}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
