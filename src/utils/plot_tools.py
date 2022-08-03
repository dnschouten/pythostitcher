import glob
import os
import warnings
import numpy as np
import imageio
import matplotlib.pyplot as plt

from .fuse_images_lowres import fuse_images_lowres
from .get_resname import get_resname


def plot_rotation_result(quadrant_a, quadrant_b, quadrant_c, quadrant_d):
    """
    Custom function to plot the result of the automatic rotation of all quadrants.

    Input:
        - All quadrants

    Output:
        - Figure displaying the rotation
    """

    # Get pad values for every image
    max_shape = np.max(
        [
            quadrant_a.mask.shape,
            quadrant_b.mask.shape,
            quadrant_c.mask.shape,
            quadrant_d.mask.shape,
        ],
        axis=0,
    )
    quadrants = [quadrant_a, quadrant_b, quadrant_c, quadrant_d]
    pad_mask = [((max_shape - q.mask.shape) / 2).astype(int) for q in quadrants]
    pad_rot_mask = [((max_shape - q.rot_mask.shape) / 2).astype(int) for q in quadrants]

    # Apply padding
    padded_mask = [
        np.pad(q.mask, [[p[0], p[0]], [p[1], p[1]]])
        for p, q in zip(pad_mask, quadrants)
    ]
    padded_rot_mask = [
        np.pad(q.rot_mask, [[p[0], p[0]], [p[1], p[1]]])
        for p, q in zip(pad_rot_mask, quadrants)
    ]

    # Get x/y values of bounding box around quadrant
    corners_x = [
        [c[0] + p[1] for c in q.bbox_corners] + [q.bbox_corners[0][0] + p[1]]
        for p, q in zip(pad_mask, quadrants)
    ]
    corners_y = [
        [c[1] + p[0] for c in q.bbox_corners] + [q.bbox_corners[0][1] + p[0]]
        for p, q in zip(pad_mask, quadrants)
    ]

    # Plot rotation result
    plt.figure(figsize=(6, 12))
    plt.suptitle("Quadrants before and after \nautomatic rotation", fontsize=20)

    for c, (pad, p_mask, p_rmask, c_x, c_y, q) in enumerate(
        zip(pad_mask, padded_mask, padded_rot_mask, corners_x, corners_y, quadrants), 1
    ):
        plt.subplot(4, 2, (c * 2) - 1)
        plt.axis("off")
        plt.title(q.quadrant_name, fontsize=16)
        plt.imshow(p_mask, cmap="gray")
        plt.scatter(
            q.mask_corner_a[0] + pad[1],
            q.mask_corner_a[1] + pad[0],
            facecolor="r",
            s=100,
        )
        plt.plot(c_x, c_y, linewidth=4, c="r")
        plt.subplot(4, 2, c * 2)
        plt.axis("off")
        plt.title(q.quadrant_name, fontsize=16)
        plt.imshow(p_rmask, cmap="gray")
    plt.savefig(f"../results/{quadrant_a.patient_idx}/images/rotation_result.png")
    plt.close()

    return


def plot_transformation_result(
    quadrant_a, quadrant_b, quadrant_c, quadrant_d, parameters
):
    """
    Custom function to plot the result of the initial transformation to globally
    align the quadrants.

    Input:
        - All quadrants
        - Dict with parameters

    Output:
        - Figure displaying the aligned quadrants
    """

    # Merge all individual quadrant images into one final image
    images = [
        quadrant_a.colour_image,
        quadrant_b.colour_image,
        quadrant_c.colour_image,
        quadrant_d.colour_image,
    ]
    result = fuse_images_lowres(images=images)

    current_res = parameters["resolutions"][parameters["iteration"]]

    # Plot figure
    plt.figure()
    plt.title(f"Initial alignment at resolution {current_res}")
    plt.imshow(result, cmap="gray")
    if parameters["iteration"] == 0:
        plt.savefig(
            f"../results/{parameters['patient_idx']}/"
            f"ga_progression/initial_alignment.png"
        )
    plt.close()

    return


def plot_theilsen_result(quadrant_a, quadrant_b, quadrant_c, quadrant_d, parameters):
    """
    Custom function to plot the result of the Theil-Sen line approximation of the
    quadrants' edges.

    Input:
        - All quadrants
        - Dict with parameters

    Output:
        - Figure displaying the Theil-Sen lines for each quadrant
    """

    # Combine all images
    images = [
        quadrant_a.colour_image,
        quadrant_b.colour_image,
        quadrant_c.colour_image,
        quadrant_d.colour_image,
    ]
    combi_image = fuse_images_lowres(images=images)

    # Set some plotting parameters
    ratio = parameters["resolution_scaling"][parameters["iteration"]]
    ms = np.sqrt(2500 * np.sqrt(ratio))

    # Plot theilsen lines with marked endpoints
    plt.figure()
    plt.title(
        f"Alignment at resolution {parameters['resolutions'][parameters['iteration']]}"
        f"\n before genetic algorithm"
    )
    plt.imshow(combi_image, cmap="gray")
    plt.plot(
        quadrant_a.v_edge_theilsen_endpoints[:, 0],
        quadrant_a.v_edge_theilsen_endpoints[:, 1],
        linewidth=2,
        color="g",
    )
    plt.plot(
        quadrant_a.h_edge_theilsen_endpoints[:, 0],
        quadrant_a.h_edge_theilsen_endpoints[:, 1],
        linewidth=2,
        color="b",
    )
    plt.plot(
        quadrant_b.v_edge_theilsen_endpoints[:, 0],
        quadrant_b.v_edge_theilsen_endpoints[:, 1],
        linewidth=2,
        color="g",
    )
    plt.plot(
        quadrant_b.h_edge_theilsen_endpoints[:, 0],
        quadrant_b.h_edge_theilsen_endpoints[:, 1],
        linewidth=2,
        color="b",
    )
    plt.plot(
        quadrant_c.v_edge_theilsen_endpoints[:, 0],
        quadrant_c.v_edge_theilsen_endpoints[:, 1],
        linewidth=2,
        color="g",
    )
    plt.plot(
        quadrant_c.h_edge_theilsen_endpoints[:, 0],
        quadrant_c.h_edge_theilsen_endpoints[:, 1],
        linewidth=2,
        color="b",
    )
    plt.plot(
        quadrant_d.v_edge_theilsen_endpoints[:, 0],
        quadrant_d.v_edge_theilsen_endpoints[:, 1],
        linewidth=2,
        color="g",
    )
    plt.plot(
        quadrant_d.h_edge_theilsen_endpoints[:, 0],
        quadrant_d.h_edge_theilsen_endpoints[:, 1],
        linewidth=2,
        color="b",
    )

    plt.scatter(
        quadrant_a.v_edge_theilsen_endpoints[:, 0],
        quadrant_a.v_edge_theilsen_endpoints[:, 1],
        marker="*",
        s=ms,
        color="g",
    )
    plt.scatter(
        quadrant_a.h_edge_theilsen_endpoints[:, 0],
        quadrant_a.h_edge_theilsen_endpoints[:, 1],
        marker="+",
        s=ms,
        color="b",
    )
    plt.scatter(
        quadrant_b.v_edge_theilsen_endpoints[:, 0],
        quadrant_b.v_edge_theilsen_endpoints[:, 1],
        marker="*",
        s=ms,
        color="g",
    )
    plt.scatter(
        quadrant_b.h_edge_theilsen_endpoints[:, 0],
        quadrant_b.h_edge_theilsen_endpoints[:, 1],
        marker="+",
        s=ms,
        color="b",
    )
    plt.scatter(
        quadrant_c.v_edge_theilsen_endpoints[:, 0],
        quadrant_c.v_edge_theilsen_endpoints[:, 1],
        marker="*",
        s=ms,
        color="g",
    )
    plt.scatter(
        quadrant_c.h_edge_theilsen_endpoints[:, 0],
        quadrant_c.h_edge_theilsen_endpoints[:, 1],
        marker="+",
        s=ms,
        color="b",
    )
    plt.scatter(
        quadrant_d.v_edge_theilsen_endpoints[:, 0],
        quadrant_d.v_edge_theilsen_endpoints[:, 1],
        marker="*",
        s=ms,
        color="g",
    )
    plt.scatter(
        quadrant_d.h_edge_theilsen_endpoints[:, 0],
        quadrant_d.h_edge_theilsen_endpoints[:, 1],
        marker="+",
        s=ms,
        color="b",
    )
    plt.legend(["v edge", "h edge"])
    plt.close()

    return


def plot_rotated_bbox(quadrant_a, quadrant_b, quadrant_c, quadrant_d):
    """
    Custom function to plot the bounding box points after the box has been rotated.
    This basically offers a sanity check to verify that the corner points have been
    rotated correctly.

    Input:
        - All quadrants

    Output:
        - Figure displaying the rotated bounding box points
    """

    # X and y coordinates of the bounding box
    scat_x = [
        quadrant_a.bbox_corner_a[0],
        quadrant_a.bbox_corner_b[0],
        quadrant_a.bbox_corner_c[0],
        quadrant_a.bbox_corner_d[0],
    ]
    scat_y = [
        quadrant_a.bbox_corner_a[1],
        quadrant_a.bbox_corner_b[1],
        quadrant_a.bbox_corner_c[1],
        quadrant_a.bbox_corner_d[1],
    ]

    plt.figure()
    plt.title("Quadrant A")
    plt.imshow(quadrant_a.tform_image, cmap="gray")
    plt.scatter(scat_x, scat_y, s=25, c="r")
    plt.close()

    # X and y coordinates of the bounding box
    scat_x = [
        quadrant_b.bbox_corner_a[0],
        quadrant_b.bbox_corner_b[0],
        quadrant_b.bbox_corner_c[0],
        quadrant_b.bbox_corner_d[0],
    ]
    scat_y = [
        quadrant_b.bbox_corner_a[1],
        quadrant_b.bbox_corner_b[1],
        quadrant_b.bbox_corner_c[1],
        quadrant_b.bbox_corner_d[1],
    ]

    plt.figure()
    plt.title("Quadrant B")
    plt.imshow(quadrant_b.tform_image, cmap="gray")
    plt.scatter(scat_x, scat_y, s=25, c="r")
    plt.close()

    # X and y coordinates of the bounding box
    scat_x = [
        quadrant_c.bbox_corner_a[0],
        quadrant_c.bbox_corner_b[0],
        quadrant_c.bbox_corner_c[0],
        quadrant_c.bbox_corner_d[0],
    ]
    scat_y = [
        quadrant_c.bbox_corner_a[1],
        quadrant_c.bbox_corner_b[1],
        quadrant_c.bbox_corner_c[1],
        quadrant_c.bbox_corner_d[1],
    ]

    plt.figure()
    plt.title("Quadrant C")
    plt.imshow(quadrant_c.tform_image, cmap="gray")
    plt.scatter(scat_x, scat_y, s=25, c="r")
    plt.close()

    # X and y coordinates of the bounding box
    scat_x = [
        quadrant_d.bbox_corner_a[0],
        quadrant_d.bbox_corner_b[0],
        quadrant_d.bbox_corner_c[0],
        quadrant_d.bbox_corner_d[0],
    ]
    scat_y = [
        quadrant_d.bbox_corner_a[1],
        quadrant_d.bbox_corner_b[1],
        quadrant_d.bbox_corner_c[1],
        quadrant_d.bbox_corner_d[1],
    ]

    plt.figure()
    plt.title("Quadrant D")
    plt.imshow(quadrant_d.tform_image, cmap="gray")
    plt.scatter(scat_x, scat_y, s=25, c="r")
    plt.close()

    return


def plot_tformed_edges(quadrant_a, quadrant_b, quadrant_c, quadrant_d):
    """
    Custom function to plot the transformed edges before inputting them into the
    genetic algorithm. This mainly serves as a sanity check while debugging.

    Input:
        - All quadrants

    Output:
        - Figure displaying the transformed edges
    """

    plt.figure()
    plt.title("Transformed edges")
    plt.plot(quadrant_a.h_edge[:, 0], quadrant_a.h_edge[:, 1], c="b")
    plt.plot(quadrant_a.v_edge[:, 0], quadrant_a.v_edge[:, 1], c="g")
    plt.plot(quadrant_b.h_edge_tform[:, 0], quadrant_b.h_edge_tform[:, 1], c="b")
    plt.plot(quadrant_b.v_edge_tform[:, 0], quadrant_b.v_edge_tform[:, 1], c="g")
    plt.plot(quadrant_c.h_edge_tform[:, 0], quadrant_c.h_edge_tform[:, 1], c="b")
    plt.plot(quadrant_c.v_edge_tform[:, 0], quadrant_c.v_edge_tform[:, 1], c="g")
    plt.plot(quadrant_d.h_edge_tform[:, 0], quadrant_d.h_edge_tform[:, 1], c="b")
    plt.plot(quadrant_d.v_edge_tform[:, 0], quadrant_d.v_edge_tform[:, 1], c="g")
    plt.legend(["Hor", "Ver"])
    plt.close()

    return


def plot_tformed_theilsen_lines(quadrant_a, quadrant_b, quadrant_c, quadrant_d):
    """
    Custom function to plot the transformed Theilsen lines before inputting them
    into the genetic algorithm. This function is analogous to the plot_tformed_edges
    function and serves as a sanity check during debugging.

    Input:
        - All quadrants

    Output:
        - Figure displaying the transformed Theil-Sen lines
    """

    plt.figure()
    plt.title("Transformed Theil-Sen lines")
    plt.plot(quadrant_a.h_edge_theilsen[:, 0], quadrant_a.h_edge_theilsen[:, 1], c="b")
    plt.plot(quadrant_a.v_edge_theilsen[:, 0], quadrant_a.v_edge_theilsen[:, 1], c="g")
    plt.plot(
        quadrant_b.h_edge_theilsen_tform[:, 0],
        quadrant_b.h_edge_theilsen_tform[:, 1],
        c="b",
    )
    plt.plot(
        quadrant_b.v_edge_theilsen_tform[:, 0],
        quadrant_b.v_edge_theilsen_tform[:, 1],
        c="g",
    )
    plt.plot(
        quadrant_c.h_edge_theilsen_tform[:, 0],
        quadrant_c.h_edge_theilsen_tform[:, 1],
        c="b",
    )
    plt.plot(
        quadrant_c.v_edge_theilsen_tform[:, 0],
        quadrant_c.v_edge_theilsen_tform[:, 1],
        c="g",
    )
    plt.plot(
        quadrant_d.h_edge_theilsen_tform[:, 0],
        quadrant_d.h_edge_theilsen_tform[:, 1],
        c="b",
    )
    plt.plot(
        quadrant_d.v_edge_theilsen_tform[:, 0],
        quadrant_d.v_edge_theilsen_tform[:, 1],
        c="g",
    )
    plt.legend(["Hor", "Ver"])
    plt.close()

    return


def plot_ga_tform(quadrant_a, quadrant_b, quadrant_c, quadrant_d):
    """
    Custom function to show the transformation of the Theil-Sen lines which was found
    by the genetic algorithm.

    Input:
        - All quadrants

    Output:
        - Figure displaying the transformed Theil-Sen lines by only taking into account
          the optimal transformation found by the genetic algorithm.
    """

    plt.figure()
    plt.subplot(121)
    plt.title("Theil-Sen lines before GA tform")
    plt.plot(quadrant_a.h_edge_theilsen_coords, linewidth=3, color="r")
    plt.plot(quadrant_a.v_edge_theilsen_coords, linewidth=3, color="r")
    plt.plot(quadrant_b.h_edge_theilsen_coords, linewidth=3, color="r")
    plt.plot(quadrant_b.v_edge_theilsen_coords, linewidth=3, color="r")
    plt.plot(quadrant_c.h_edge_theilsen_coords, linewidth=3, color="r")
    plt.plot(quadrant_c.v_edge_theilsen_coords, linewidth=3, color="r")
    plt.plot(quadrant_d.h_edge_theilsen_coords, linewidth=3, color="r")
    plt.plot(quadrant_d.v_edge_theilsen_coords, linewidth=3, color="r")

    plt.subplot(122)
    plt.title("Theil-Sen lines after GA tform")
    plt.plot(quadrant_a.h_edge_theilsen_tform, linewidth=3, color="g")
    plt.plot(quadrant_a.v_edge_theilsen_tform, linewidth=3, color="g")
    plt.plot(quadrant_b.h_edge_theilsen_tform, linewidth=3, color="g")
    plt.plot(quadrant_b.v_edge_theilsen_tform, linewidth=3, color="g")
    plt.plot(quadrant_c.h_edge_theilsen_tform, linewidth=3, color="g")
    plt.plot(quadrant_c.v_edge_theilsen_tform, linewidth=3, color="g")
    plt.plot(quadrant_d.h_edge_theilsen_tform, linewidth=3, color="g")
    plt.plot(quadrant_d.v_edge_theilsen_tform, linewidth=3, color="g")
    plt.close()

    return


def plot_ga_result(final_image, parameters):
    """
    Plotting function to plot the transformation of the quadrants which was found
    by the genetic algorithm.

    Input:
        - All quadrants
        - Dict with parameters
        - Final transformation from genetic algorithm

    Output:
        - Figure displaying the end result obtained by the genetic algorithm
    """

    current_res_name = get_resname(parameters["resolutions"][parameters["iteration"]])

    # Save result
    plt.figure()
    plt.title(
        f"Alignment at resolution {current_res_name}\n after genetic algorithm "
        f"(fitness={np.round(parameters['GA_fitness'][-1], 2)})"
    )
    plt.imshow(final_image)
    plt.savefig(
        f"../results/{parameters['patient_idx']}/ga_progression/"
        f"ga_result_{current_res_name}.png"
    )
    plt.close()

    return


def make_tform_gif(parameters):
    """
    Custom function to make a gif of all the tformed results after the genetic algorithm
    as a visual check of the result. This function requires that intermediate results of
    the genetic algorithm from the different resolutions are saved in a directory called
    images. This function will then combine these images into the GIF.

    Input:
        - Dict with parameters

    Output:
        - GIF file of the transformation
    """

    # Make gif of the transformation
    imsavedir = (
        f"{parameters['results_dir']}/{parameters['patient_idx']}/ga_progression/"
    )
    gifsavedir = (
        f"{parameters['results_dir']}/{parameters['patient_idx']}/tform_progression.gif"
    )

    all_images = glob.glob(imsavedir + "/*")
    all_images = sorted(all_images, key=lambda t: os.stat(t).st_mtime)

    images = []
    for name in all_images:
        image = imageio.imread(name)
        images.append(image)

    imageio.mimsave(gifsavedir, images, duration=0.75)

    return


def plot_sampled_patches(total_im, patch_indices_x, patch_indices_y, ts_lines):
    """
    Custom function to visualize the patches which are extracted in the histogram cost
    function. This function serves as a visual check that the patches are extracted
    correctly.

    Input:
        - Final recombined image
        - X/Y indices of the extracted patches
        - Theil-Sen lines

    Output:
        - Figure displaying the sampled patches
    """

    # Plotting parameters
    ts_line_colours = ["b", "g"] * 4

    plt.figure()
    plt.title("Sampled patches on TheilSen lines")
    plt.imshow(total_im, cmap="gray")
    for x, y in zip(patch_indices_x.values(), patch_indices_y.values()):
        plt.plot(x, y, linewidth=0.5, c="r")
    for ts, c in zip(ts_lines, ts_line_colours):
        plt.plot(ts[:, 0], ts[:, 1], linewidth=2, c=c)
    plt.close()

    return


def plot_overlap_cost(im, relative_overlap):
    """
    Custom function to plot the overlap between the quadrants. Currently the overlap
    between the quadrants is visualized as a rather gray area, this could of course be
    visualized more explicitly.

    Input:
        - Final stitched image
        - Percentual overlap

    Output:
        - Figure displaying the overlap between the quadrants
    """

    plt.figure()
    plt.title(
        f"Visualization of overlapping quadrants {np.round(relative_overlap*100, 1)}%"
    )
    plt.imshow(im, cmap="gray")
    plt.close()

    return


def plot_ga_multires(parameters):
    """
    Custom function to plot how the fitness improves at multiple resolutions.

    NOTE: The fitness depends on the cost function being used and may not scale correctly
    with the resolutions. This may result in a decreasing fitness for higher resolutions
    while the visual fitness increases. Example: absolute distance between the endpoints
    of the edges increases for higher resolutions leading to a lower fitness when this is
    the only factor in the cost function.

    Input:
        - Dict with parameters

    Output:
        - Figure displaying the evolution of the fitness over different resolutions.
    """

    # Set some plotting parameters
    fitness = parameters["GA_fitness"]
    xticks_loc = list(np.arange(0, 5))
    xticks_label = ["Initial"] + parameters["resolutions"]

    # Only plot when the GA fitness has been tracked properly (e.g. when the cost function
    # has been scaled properly throughout the different resolutions).
    if len(fitness) == len(xticks_label):
        plt.figure()
        plt.title("Fitness progression at multiple resolutions")
        plt.plot(xticks_loc, fitness)
        plt.xlabel("Resolution")
        plt.xticks(xticks_loc, xticks_label)
        plt.ylabel("Fitness")
        plt.savefig(f"../results/{parameters['patient_idx']}/images/GA_fitness_result")
        plt.close()
    else:
        warnings.warn(
            "Could not plot fitness progression for multiple resolutions, "
            "try running the genetic algorithm from scratch by deleting "
            "the results directory of this patient"
        )

    return
