from analyses.models import Analysis, Context


class SphereEvenlySampling:
    def __init__(self, analysis):
        self.analysis = analysis

    def query_test(self):
        return "test success"

    def query_project_directions(self):

        sample_size_ct = Context.objects.filter(
            analysis=self.analysis,
            name='samples.size').get()

        sample_size = sample_size_ct.value

        directions = {}
        for i in range(0, sample_size):

            try:
                result_ct = Context.objects.filter(
                    analysis=self.analysis,
                    name='projected.result.%i' % i
                ).get()
                directions[result_ct.value['index']] = result_ct.value
            except Context.DoesNotExist:
                pass

        return directions
