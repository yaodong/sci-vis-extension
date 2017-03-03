import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('inspector-diagram', 'Integration | Component | inspector diagram', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{inspector-diagram}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#inspector-diagram}}
      template block text
    {{/inspector-diagram}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
