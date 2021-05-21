import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

def colored_line(ax, x, y, c, **kwargs):
    """Helper function to take a set of points and turn them into a collection of
    lines colored by another array

    Parameters
    ----------
    x : array-like
        x-axis coordinates
    y : array-like
        y-axis coordinates
    c : array-like
        values used for color-mapping
    kwargs : dict
        Other keyword arguments passed to :class:`matplotlib.collections.LineCollection`

    Returns
    -------
        The created :class:`matplotlib.collections.LineCollection` instance.
    """
    # Paste values end to end
    points = np.concatenate([x, y])

    # Exploit numpy's strides to present a view of these points without copying.
    # Dimensions are (segment, start/end, x/y). Since x and y are concatenated back to back,
    # moving between segments only moves one item; moving start to end is only an item;
    # The move between x any moves from one half of the array to the other
    num_pts = points.size // 2
    final_shape = (num_pts - 1, 2, 2)
    final_strides = (points.itemsize, points.itemsize, num_pts * points.itemsize)
    segments = np.lib.stride_tricks.as_strided(points, shape=final_shape,
                                               strides=final_strides)

    if 'norm' not in kwargs:
        kwargs['norm'] = plt.Normalize(np.min(c), np.max(c))

    # Create a LineCollection from the segments and set it to colormap based on c
    lc = LineCollection(segments, **kwargs)
    lc.set_array(c)
    return ax.add_collection(lc)

