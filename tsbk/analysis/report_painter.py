import numpy as np
import matplotlib.pyplot as plt


def get_steps_colors(values):
    values = 1 / values
    _range = np.max(values) - np.min(values)
    _values = (values - np.min(values)) / _range
    colors_data = plt.cm.Wistia(_values)
    return colors_data


def paint_table(df, title_cols, title_text, result_path, fontsize=-1, fig_background_color='white', fig_border='white'):
    df = df.copy()
    df = df.applymap(lambda x: x[:15] + '...' if isinstance(x, str) and len(x) > 15 else x)

    # Get headers
    footer_text = ''
    cols_header = df.columns
    cols_header_data = df.columns[1:]
    if title_cols != None:
        cols_header_data = df.columns[len(title_cols):]

    df_data = df[cols_header_data]

    # Get data
    cell_text = []
    for i, row in df.iterrows():
        data_row = list(row.values[0:len(title_cols)]) + [f'{x:1.3f}' for x in row.values[len(title_cols):]]
        cell_text.append(data_row)

    # Get colors
    colors_cells = []
    for i, row in df_data.iterrows():
        colors_data = get_steps_colors(row.values)
        colors_row = np.append(plt.cm.binary(np.full(len(title_cols), 1)), colors_data, axis=0)
        colors_cells.append(colors_row)

    colors_header = plt.cm.binary(np.full(len(cols_header), 1))

    # Figure
    plt.figure(linewidth=2,
               edgecolor=fig_border,
               facecolor=fig_background_color,
               tight_layout={'pad': 1},
               # figsize=(5,3)
               )

    # plt.rcParams.update({"font.size": 20})
    the_table = plt.table(cellText=cell_text,
                          cellColours=colors_cells,
                          rowLoc='right',
                          colColours=colors_header,
                          colLabels=cols_header,
                          loc='center')

    # Set font size if user set it
    if fontsize > 0:
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(fontsize)

    the_table.scale(1, 1.5)
    # Hide axes
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    # Hide axes border
    plt.box(on=None)
    # Add title
    cell_height = the_table[0, 0].get_height()
    center = 0.5
    distance_cell_title = 0.02
    y = center + cell_height * (df.shape[0] + 1) / 2 + distance_cell_title
    plt.suptitle(title_text, y=y)
    # Add footer
    plt.figtext(0.95, 0.05, footer_text, horizontalalignment='right', size=6, weight='light')
    # Force the figure to update, so backends center objects correctly within the figure.
    # Without plt.draw() here, the title will center on the axes and not the figure.
    plt.draw()

    # Create image. plt.savefig ignores figure edge and face colors, so map them.
    fig = plt.gcf()
    plt.savefig(result_path,
                # bbox='tight',
                edgecolor=fig.get_edgecolor(),
                facecolor=fig.get_facecolor(),
                dpi=400
                )
