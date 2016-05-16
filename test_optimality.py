from __future__ import division
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
from cwc.models.density_estimators import MyMultivariateNormal

np.random.seed(42)
plt.ion()
plt.rcParams['figure.figsize'] = (7,4)
plt.rcParams['figure.autolayout'] = True

colors = ['red', 'blue', 'yellow', 'orange', 'cyan']

def one_vs_rest_roc_curve(y,p):
    """Returns the roc curve of class 0 vs the rest of the classes"""
    aux = np.copy(y)
    aux[aux!=0] = 1
    return roc_curve(aux, p)

def convex_hull(points):
    """Computes the convex hull of a set of 2D points.
    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
      starting from the vertex with the lexicographically smallest coordinates.
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.
    Source code from:
    https://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Convex_hull/Monotone_chain
    """

    # Sort the points lexicographically (tuples are compared lexicographically).
    # Remove duplicates to detect the case we have just one unique point.
    points = sorted(set(points))

    # Boring case: no points or a single point, possibly repeated multiple times.
    if len(points) <= 1:
        return points

    # 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product.
    # Returns a positive value, if OAB makes a counter-clockwise turn,
    # negative for clockwise turn, and zero if the points are collinear.
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return upper

def plot_data(x,y, fig=None, title=None):
    if fig is None:
        fig = plt.figure('Data')
    fig.clf()
    ax = fig.add_subplot(111)
    classes = np.unique(y)
    for c in classes:
        ax.scatter(x[y==c,0], x[y==c,1], c=colors[c], label='Class {}'.format(c))
    ax.legend()


def plot_data_and_contourlines(x,y,x_grid,p0,p1, delta=50, fig=None, title=None):
    if fig is None:
        fig = plt.figure('gaussians')
    fig.clf()
    plot_data(x,y,fig=fig)

    ax = fig.add_subplot(111)
    # HEATMAP OF PROBABILITIES
    #levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    # TODO Change colors of the contour lines to the matching class
    CS = ax.contour(x_grid[:,0].reshape(delta,delta),
                     x_grid[:,1].reshape(delta,delta),
                     p0.reshape(delta,-1), linewidths=3,
                     alpha=1.0, cmap='autumn_r') # jet
    ax.clabel(CS, fontsize=20, inline=2)
    CS = ax.contour(x_grid[:,0].reshape(delta,delta),
                     x_grid[:,1].reshape(delta,delta),
                     p1.reshape(delta,-1), linewidths=3,
                     alpha=1.0, cmap='winter_r') # jet_r
    ax.clabel(CS, fontsize=20, inline=2)

    if title is not None:
        ax.set_title(title)


def plot_posterior(x,y,x_grid, posterior, delta=50, fig=None, title=None):
    if fig is None:
        fig = plt.figure('posterior')
    fig.clf()
    plot_data(x,y,fig=fig)

    ax = fig.add_subplot(111)
    # HEATMAP OF PROBABILITIES
    #levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    # TODO Change colors of the contour lines to the matching class
    CS = ax.contour(x_grid[:,0].reshape(delta,delta),
                     x_grid[:,1].reshape(delta,delta),
                     posterior.reshape(delta,-1), linewidths=3,
                     alpha=0.8)
    ax.clabel(CS, fontsize=20, inline=2)

    if title is not None:
        ax.set_title(title)


def get_grid(x, delta=50):
    x_min = np.min(x,axis=0)
    x_max = np.max(x,axis=0)

    x1_lin = np.linspace(x_min[0], x_max[0], delta)
    x2_lin = np.linspace(x_min[1], x_max[1], delta)

    MX1, MX2 = np.meshgrid(x1_lin, x2_lin)
    x_grid = np.asarray([MX1.flatten(),MX2.flatten()]).T

    return x_grid


def main():
    samples = [500,         # Class 1
               500]         # Class 2
    means = [[0,0],       # Class 1
             [2,2]]       # Class 2
    covs = np.array([[[1,0],       # Class 1
             [0,1]],
            [[1,0],       # Class 2
             [0,1]]])

    mvn0 = MyMultivariateNormal(means[0], covs[0])
    mvn1 = MyMultivariateNormal(means[1], covs[1])
    mvn2 = MyMultivariateNormal([-3,3], covs[0]*0.1)

    x0 = mvn0.sample(samples[0])
    x1 = mvn1.sample(samples[1])
    x2 = mvn2.sample(300)

    x = np.vstack([x0, x1, x2])
    y = np.hstack([np.zeros(len(x0)), np.ones(len(x1)),
        np.ones(len(x2))*2]).astype(int)

    x_grid = get_grid(x)

    p0_grid =  mvn0.score(x_grid)
    p1_grid =  mvn1.score(x_grid)

    prior = samples[0]/sum(samples)
    posterior = (p0_grid*prior)/(p0_grid*prior+p1_grid*(1-prior))

    fig = plt.figure('Density')
    plot_data_and_contourlines(x,y,x_grid,p0_grid,p1_grid,delta=50,fig=fig, title='Density')
    fig = plt.figure('Bayes')
    plot_posterior(x,y,x_grid,posterior,delta=50, fig=fig, title='Bayes optimal')

    fig = plt.figure('P_Miquel')
    plot_data_and_contourlines(x,y,x_grid,p0_grid*posterior,p1_grid*(1-posterior)
                               ,delta=50,fig=fig, title='P_Miquel')
    q0 = mvn0.score(x)
    q1 = mvn1.score(x)
    posterior = (q0*prior)/(q0*prior+q1*(1-prior))
    roc = one_vs_rest_roc_curve(y, q0*posterior)
    fig = plt.figure('roc_miquel_posterior')
    fig.clf()
    ax = fig.add_subplot(111)
    ax.plot(roc[1], roc[0])
    ax.plot([0,1],[0,1], 'g--')
    ax.plot([0,1],[1,0], 'g--')
    upper_hull = convex_hull(zip(roc[1],roc[0]))
    rg_hull, pg_hull = zip(*upper_hull)
    plt.plot(rg_hull, pg_hull, 'r--')
    ax.set_title('ROC Miquel posterior')

    q0 = mvn0.score(x)
    roc = one_vs_rest_roc_curve(y, q0)
    fig = plt.figure('roc_curve')
    fig.clf()
    ax = fig.add_subplot(111)
    ax.plot(roc[1], roc[0])
    ax.plot([0,1],[0,1], 'g--')
    ax.plot([0,1],[1,0], 'g--')
    upper_hull = convex_hull(zip(roc[1],roc[0]))
    rg_hull, pg_hull = zip(*upper_hull)
    plt.plot(rg_hull, pg_hull, 'r--')
    ax.set_title('ROC Density class 0')


    q1 = mvn1.score(x)
    q_posterior = (q0*prior)/(q0*prior+q1*(1-prior))
    roc = one_vs_rest_roc_curve(y, q_posterior)
    fig = plt.figure('roc_curve_posterior')
    fig.clf()
    ax = fig.add_subplot(111)
    ax.plot(roc[1], roc[0])
    ax.plot([0,1],[0,1], 'g--')
    ax.plot([0,1],[1,0], 'g--')
    upper_hull = convex_hull(zip(roc[1],roc[0]))
    rg_hull, pg_hull = zip(*upper_hull)
    plt.plot(rg_hull, pg_hull, 'r--')
    ax.set_title('ROC Bayes Optimal')
    #prior_background = 0.2
    #density_background = 0.3
    #posterior_vs_background = (p0_grid*(1-prior_background))/(p0_grid*(1-prior_background) + density_background*prior_background)
    #new_posterior = posterior_vs_background*posterior
    #plot_posterior(x,y,x_grid,new_posterior,delta=50)

    P_t = 0.8
    P_b = (1-P_t)
    P_x_b = 0.3
    numerator = p0_grid*prior*P_t
    denominator = numerator + p1_grid*(1-prior)*P_t + P_x_b*P_b
    P_t_0_x = numerator/denominator

    numerator = p1_grid*(1-prior)*P_t
    denominator = numerator + p0_grid*prior*P_t + P_x_b*P_b
    P_t_1_x = numerator/denominator
    fig = plt.figure('P_telmo')
    plot_data_and_contourlines(x,y,x_grid,P_t_0_x,P_t_1_x,delta=50, fig=fig, title='P_telmo')


    # Compute predictions for all samples
    P_t = 0.8
    P_b = (1-P_t)
    P_x_b = 0.3
    numerator = q0*prior*P_t
    denominator = numerator + q1*(1-prior)*P_t + P_x_b*P_b
    P_t_0_x = numerator/denominator

    # Plot the ROC curve
    roc = one_vs_rest_roc_curve(y, P_t_0_x)
    fig = plt.figure('roc_telmo_posterior')
    fig.clf()
    ax = fig.add_subplot(111)
    ax.plot(roc[1], roc[0])
    ax.plot([0,1],[0,1], 'g--')
    ax.plot([0,1],[1,0], 'g--')
    upper_hull = convex_hull(zip(roc[1],roc[0]))
    rg_hull, pg_hull = zip(*upper_hull)
    plt.plot(rg_hull, pg_hull, 'r--')
    ax.set_title('ROC Telmo posterior')




    #plot_posterior(x,y,x_grid,(p0_grid+p1_grid)/2,delta=50)
    #plot_posterior(x,y,x_grid,posterior,delta=50)

    #P_t = 0.8
    #P_b = (1-P_t)
    #P_x_b = 0.3
    #P_0_t_x = posterior
    #P_x_t = p0_grid*prior+p1_grid*(1-prior)
    #numerator = P_0_t_x*P_x_t*P_t
    #denominator = P_x_t*P_t*P_x_b*P_b
    #P_telmo = numerator/denominator
    #fig = plt.figure('P_telmo')
    #plot_posterior(x,y,x_grid,posterior,delta=50, fig=fig, title='P_telmo')

    return 0

if __name__ == "__main__":
    sys.exit(main())