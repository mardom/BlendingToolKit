from abc import ABC
from btk.multiprocess import multiprocess


class Measurement_params(ABC):
    """Class with functions to perform detection/deblending/measurement."""

    def make_measurement(self, data, index):
        """Function describing how the measurement algorithm is run.

        Args:
            data (dict): Output generated by btk.draw_blends containing blended
                         images, isolated images, observing conditions and
                         blend catalog, for a given batch.
            index (int): Index number of blend scene in the batch to preform
                         measurement on.

        Returns:
            output of measurement algorithm (fluxes, shapes, size, etc.) as
            an astropy catalog.
        """
        return None

    def get_deblended_images(self, data, index):
        """Function describing how the deblending algorithm is run.

        Args:
            data (dict): Output generated by btk.draw_blends containing blended
                         images, isolated images, observing conditions and
                         blend catalog, for a given batch.
            index (int): Index number of blend scene in the batch to preform
                         measurement on.

        Returns:
            output of deblending algorithm as a dict.
        """
        return None


def run_batch(measurement_params, blend_output, index):
    deblend_results = measurement_params.get_deblended_images(
        data=blend_output, index=index
    )
    measured_results = measurement_params.make_measurement(
        data=blend_output, index=index
    )
    return [deblend_results, measured_results]


def generate(
    measurement_params, draw_blend_generator, Args, multiprocessing=False, cpus=1
):
    """Generates output of deblender and measurement algorithm.

    Args:
        measurement_params: Instance from class
                            `btk.measure.Measurement_params`.
        draw_blend_generator: Generator that outputs dict with blended images,
                              isolated images, observing conditions and blend
                              catalog.
        Args: Class containing input parameters.
        multiprocessing: If true performs multiprocessing of measurement.
        cpus: If multiprocessing is True, then number of parallel processes to
             run [Default :1].
    Returns:
        draw_blend_generator output, deblender output and measurement output.
    """
    while True:
        blend_output = next(draw_blend_generator)
        batch_size = len(blend_output["blend_images"])
        deblend_results = {}
        measured_results = {}
        input_args = [
            (measurement_params, blend_output, i) for i in range(Args.batch_size)
        ]
        batch_results = multiprocess(
            run_batch, input_args, cpus, multiprocessing, Args.verbose,
        )
        for i in range(batch_size):
            deblend_results.update({i: batch_results[i][0]})
            measured_results.update({i: batch_results[i][1]})
        if Args.verbose:
            print("Measurement performed on batch")
        yield blend_output, deblend_results, measured_results
