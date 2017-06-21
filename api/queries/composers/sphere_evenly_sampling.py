from analyses.models import Context


class SphereEvenlySampling:
    def __init__(self, analysis):
        self.analysis = analysis

    def query_test(self):
        return "test success"

    def query_project_directions(self):

        try:
            sample_size_ct = Context.objects.filter(
                analysis=self.analysis,
                name='samples.size').get()
        except Context.DoesNotExists:
            return None

        sample_size = int(sample_size_ct.value)

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

        if directions:
            return directions
        else:
            return None

    def query_preview_data(self):

        try:
            preview_status = Context.objects.filter(
                analysis=self.analysis,
                name="preview.is_ready").get()
            return bool(preview_status.value)
        except Context.DoesNotExist:
            return False
