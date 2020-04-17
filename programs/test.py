import numpy
import pylab

from matplotlib.widgets import Button, Slider


def gauss(sigma, mu, x):
    return (1.0 / (sigma * numpy.sqrt(2.0 * numpy.pi)) *
            numpy.exp(-((x - mu) ** 2) / (2 * sigma * sigma)))


def addPlot(graph_axes, sigma, mu):
    x = numpy.arange(-5.0, 5.0, 0.01)
    y = gauss(sigma, mu, x)
    graph_axes.plot(x, y)

    pylab.draw()


if __name__ == '__main__':
    def onButtonAddClicked(event):
        global slider_sigma
        global slider_mu
        global graph_axes

        addPlot(graph_axes, slider_sigma.val, slider_mu.val)

    def onButtonClearClicked(event):
        global graph_axes

        graph_axes.clear()
        graph_axes.grid()
        pylab.draw()

    fig, graph_axes = pylab.subplots()
    graph_axes.grid()

    fig.subplots_adjust(left=0.07, right=0.95, top=0.95, bottom=0.4)

    axes_button_add = pylab.axes([0.55, 0.05, 0.4, 0.075])
    button_add = Button(axes_button_add, 'Add')
    button_add.on_clicked(onButtonAddClicked)

    axes_button_clear = pylab.axes([0.05, 0.05, 0.4, 0.075])
    button_clear = Button(axes_button_clear, 'Clear')
    button_clear.on_clicked(onButtonClearClicked)

    axes_slider_sigma = pylab.axes([0.05, 0.25, 0.85, 0.04])
    slider_sigma = Slider(axes_slider_sigma,
                          label='sigma',
                          valmin=0.1,
                          valmax=1.0,
                          valinit=0.5,
                          valfmt='%1.2f')

    axes_slider_mu = pylab.axes([0.05, 0.17, 0.85, 0.04])
    slider_mu = Slider(axes_slider_mu,
                       label='mu',
                       valmin=-4.0,
                       valmax=4.0,
                       valinit=0.0,
                       valfmt='%1.2f')

    pylab.show()